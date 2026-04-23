from __future__ import annotations

from itertools import groupby
from operator import itemgetter
from typing import Annotated

from fastapi import Depends
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from pawprints.database.session import get_async_db_session
from pawprints.exceptions import (
    DBError,  # 1000 / 500
    PermissionNotFoundError,  # 6002 / 404
    RoleAlreadyExistsError,  # 6001 / 409
    RoleNotFoundError,  # 6000 / 404
)
from pawprints.models.orm import Permission, Role, RolePermission
from pawprints.models.schema import PermissionSchema, RoleSchema


class RoleService:
    """Service class for role-related operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_roles(self) -> list[RoleSchema]:
        """Retrieve all roles in the system."""
        try:
            roles_stmt = select(Role).order_by(Role.name.asc())
            roles_res = await self.session.execute(roles_stmt)
            roles = roles_res.scalars().all()
            return [
                RoleSchema(id=r.id, name=r.name, description=(r.description or ""), permissions=[])
                for r in roles
            ]
        except Exception as e:
            raise DBError(
                message="Failed to fetch roles.",
                context={"op": "role_list", "error": repr(e)},
            ) from e

    async def create_role(self, role: RoleSchema) -> RoleSchema:
        """Create a new role in the system."""
        try:
            # Check if role name already exists
            if await self.session.scalar(select(Role.id).where(Role.name == role.name)):
                raise RoleAlreadyExistsError(message="Role name already exists.")

            async with self.session.begin_nested():
                new_role = Role(name=role.name, description=role.description)
                self.session.add(new_role)
                await self.session.flush()  # get new id

                perm_ids = sorted(
                    {p.id for p in (role.permissions or []) if p and p.id is not None}
                )
                attached_perms: list[PermissionSchema] = []

                if perm_ids:
                    # Validate permissions (single IN query)
                    rows = await self.session.execute(
                        select(Permission.id, Permission.name)
                        .where(Permission.id.in_(perm_ids))
                        .order_by(Permission.id)
                    )
                    found = rows.all()
                    found_ids = {r.id for r in found}
                    missing = [pid for pid in perm_ids if pid not in found_ids]
                    if missing:
                        raise PermissionNotFoundError(message=f"Unknown permission ids: {missing}")

                    # Bulk insert role-permission links
                    self.session.add_all(
                        RolePermission(role_id=new_role.id, permission_id=pid) for pid in found_ids
                    )
                    attached_perms = [PermissionSchema(id=r.id, name=r.name) for r in found]

            return RoleSchema(
                id=new_role.id,
                name=new_role.name,
                description=new_role.description,
                permissions=attached_perms,
            )
        except (RoleAlreadyExistsError, PermissionNotFoundError):
            raise
        except Exception as e:
            raise DBError(
                message="Failed to create role.",
                context={"op": "role_create", "role_name": role.name, "error": repr(e)},
            ) from e

    async def delete_role(self, role_id: int) -> None:
        """Delete a role from the system."""

        role = await self.session.get(Role, role_id)
        if not role:
            raise RoleNotFoundError(message="Role not found.")

        try:
            await self.session.delete(role)
            async with self.session.begin_nested():
                # Remove all role-permission links
                await self.session.execute(
                    delete(RolePermission).where(RolePermission.role_id == role_id)
                )
                # Remove the role
                await self.session.execute(delete(Role).where(Role.id == role_id))
        except RoleNotFoundError:
            raise
        except Exception as e:
            raise DBError(
                message="Failed to delete role.",
                context={"op": "role_delete", "role_id": role_id, "error": repr(e)},
            ) from e

    async def update_role(self, role: RoleSchema) -> RoleSchema:
        """Update a role in the system."""
        try:
            # Check if role exists
            existing_role = await self.session.get(Role, role.id)
            if not existing_role:
                raise RoleNotFoundError(message="Role not found.")

            # Check for name collision
            if await self.session.scalar(select(Role).where(Role.name == role.name)):
                raise RoleAlreadyExistsError(message="Role name already exists.")

            async with self.session.begin_nested():
                existing_role.name = role.name
                existing_role.description = role.description
                self.session.add(existing_role)

            return RoleSchema(
                id=existing_role.id,
                name=existing_role.name,
                description=existing_role.description,
            )
        except (RoleNotFoundError, RoleAlreadyExistsError):
            raise
        except Exception as e:
            raise DBError(
                message="Failed to update role.",
                context={"op": "role_update", "role_id": role.id, "error": repr(e)},
            ) from e

    async def update_role_permissions(self, role_id: int, permission_ids: list[int]) -> RoleSchema:
        """Update the permissions of a role."""
        try:
            # Check if role exists
            role = await self.session.get(Role, role_id)
            if not role:
                raise RoleNotFoundError(message="Role not found.")

            async with self.session.begin_nested():
                # Remove existing permissions
                await self.session.execute(
                    delete(RolePermission).where(RolePermission.role_id == role_id)
                )

                # Add new permissions
                if permission_ids:
                    rows = await self.session.execute(
                        select(Permission.id, Permission.name)
                        .where(Permission.id.in_(permission_ids))
                        .order_by(Permission.id)
                    )
                    found = rows.all()
                    found_ids = {r.id for r in found}
                    missing = [pid for pid in permission_ids if pid not in found_ids]
                    if missing:
                        raise PermissionNotFoundError(message=f"Unknown permission ids: {missing}")

                    self.session.add_all(
                        RolePermission(role_id=role_id, permission_id=pid) for pid in found_ids
                    )
                    attached_perms = [PermissionSchema(id=r.id, name=r.name) for r in found]
                else:
                    attached_perms = []

            return RoleSchema(
                id=role.id,
                name=role.name,
                description=role.description,
                permissions=attached_perms,
            )
        except (RoleNotFoundError, PermissionNotFoundError):
            raise
        except Exception as e:
            # session.begin() auto-rolls back on exception; explicit rollback is safe but not required
            await self.session.rollback()
            raise DBError(
                message="Failed to update role permissions.",
                context={"op": "role_permission_update", "role_id": role_id, "error": repr(e)},
            ) from e

    async def get_roles_with_permissions(self) -> list[RoleSchema]:
        try:
            role_cols = (Role.id, Role.name, Role.description)
            perm_id = Permission.id.label("perm_id")
            perm_name = Permission.name.label("perm_name")

            stmt = (
                select(*role_cols, perm_id, perm_name)
                .select_from(Role)
                .join(RolePermission, RolePermission.role_id == Role.id, isouter=True)
                .join(Permission, Permission.id == RolePermission.permission_id, isouter=True)
                .order_by(Role.id, Permission.id)
            )

            result = (await self.session.execute(stmt)).all()

            roles_data: list[RoleSchema] = []
            for (r_id, r_name, r_desc), rows in groupby(result, key=itemgetter(0, 1, 2)):
                perms = [
                    PermissionSchema(id=row.perm_id, name=row.perm_name)
                    for row in rows
                    if row.perm_id is not None
                ]
                roles_data.append(
                    RoleSchema(
                        id=r_id,
                        name=r_name,
                        description=r_desc,
                        permissions=perms,
                    )
                )
            return roles_data
        except Exception as e:
            raise DBError(
                message="Failed to fetch roles with permissions.",
                context={"op": "role_list_with_permissions", "error": repr(e)},
            ) from e

    async def duplicate_role(self, role_id: int, new_name: str) -> RoleSchema:
        """Duplicate an existing role with all its permissions."""
        try:
            # Check if source role exists
            source_role = await self.session.get(Role, role_id)
            if not source_role:
                raise RoleNotFoundError(message=f"Source role with ID {role_id} not found.")

            # Check if new name already exists
            if await self.session.scalar(select(Role.id).where(Role.name == new_name)):
                raise RoleAlreadyExistsError(message=f"Role '{new_name}' already exists.")

            async with self.session.begin_nested():
                # Create new role with same description
                new_role = Role(name=new_name, description=source_role.description)
                self.session.add(new_role)
                await self.session.flush()  # get new_role.id

                # Get all permissions from source role
                perm_stmt = (
                    select(Permission.id, Permission.name)
                    .select_from(RolePermission)
                    .join(Permission, Permission.id == RolePermission.permission_id)
                    .where(RolePermission.role_id == role_id)
                    .order_by(Permission.id)
                )
                perm_result = await self.session.execute(perm_stmt)
                permissions = perm_result.all()

                # Copy permissions to new role
                if permissions:
                    self.session.add_all(
                        RolePermission(role_id=new_role.id, permission_id=perm.id)
                        for perm in permissions
                    )

                attached_perms = [
                    PermissionSchema(id=perm.id, name=perm.name) for perm in permissions
                ]

            return RoleSchema(
                id=new_role.id,
                name=new_role.name,
                description=new_role.description,
                permissions=attached_perms,
            )
        except (RoleNotFoundError, RoleAlreadyExistsError):
            raise
        except Exception as e:
            raise DBError(
                message="Failed to duplicate role.",
                context={
                    "op": "role_duplicate",
                    "source_role_id": role_id,
                    "new_name": new_name,
                    "error": repr(e),
                },
            ) from e


def get_role_service(
    session: Annotated[AsyncSession, Depends(get_async_db_session)],
) -> RoleService:
    """Dependency: get RoleService instance."""
    return RoleService(session=session)


RoleServiceDep = Annotated[RoleService, Depends(get_role_service)]
