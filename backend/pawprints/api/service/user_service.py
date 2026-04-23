from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime
import math
from typing import Annotated

from fastapi import Depends
from sqlalchemy import and_, delete, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from pawprints.database.session import get_async_db_session
from pawprints.exceptions import (
    DBError,  # 1000 / 500
    PetitionAlreadySignedError,  # 4001 / 409
    PetitionNotFoundError,  # 4000 / 404
    RoleNotFoundError,  # 6000 / 404
    UserHasNotSignedPetitionError,  # 5005 / 400
    UserNotFoundError,  # 5000 / 404
)
from pawprints.exceptions.petitions import OwnPetitionError, PetitionClosedError
from pawprints.models.orm import (
    Committee,
    Petition,
    PetitionSignature,
    Role,
    StatusEnum,
    User,
    UserCommitteeAssociation,
    UserRole,
)
from pawprints.models.schema import (
    CommitteeSchema,
    PageInfo,
    PetitionSignResponse,
    ReturnUserProfile,
    RoleSchema,
    UserSchema,
)


class UserService:
    """Service class for user-related operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _build_user_filters(self, role_name: str | None, search: str | None) -> list:
        """Build filter conditions for user queries."""
        filters = []
        if role_name:
            filters.append(Role.name == role_name)
        if search:
            search_pattern = f"{search}%"
            filters.append(User.username.ilike(search_pattern))
        return filters

    def _apply_user_ordering(self, stmt, search: str | None):
        """Apply ordering to user query based on search."""
        if search:
            search_lower = search.lower()
            search_pattern_lower = f"{search_lower}%"
            return stmt.order_by(
                func.lower(User.username).like(search_pattern_lower).desc(),
                User.username,
            )
        return stmt.order_by(User.last_name, User.first_name, User.username)

    async def _get_total_users_count(self, role_name: str | None, search: str | None) -> int:
        count_stmt = select(func.count(func.distinct(User.username))).select_from(User)

        query_filters = []

        if role_name:
            count_stmt = count_stmt.join(UserRole).join(Role)
            query_filters.append(Role.name == role_name)

        if search:
            query_filters.append(User.username.ilike(f"{search}%"))

        if query_filters:
            count_stmt = count_stmt.where(and_(*query_filters))

        result = await self.session.execute(count_stmt)
        total_items = result.scalar_one_or_none()
        return int(total_items or 0)

    async def _fetch_paginated_users(
        self,
        page: int,
        items_per_page: int,
        role_name: str | None,
        search: str | None,
    ) -> list[dict]:
        """Fetch paginated list of users as dicts to avoid lazy loading."""
        offset = (page - 1) * items_per_page

        users_stmt = select(
            User.username,
            User.first_name,
            User.last_name,
            User.rit_edu_account_type,
            User.rit_edu_campus_u,
            User.rit_edu_campus_g,
            User.rit_edu_college_u,
            User.rit_edu_college_g,
        )

        if role_name:
            users_stmt = users_stmt.select_from(User).join(UserRole).join(Role)

        filters = self._build_user_filters(role_name, search)
        if filters:
            users_stmt = users_stmt.where(and_(*filters))

        users_stmt = users_stmt.group_by(User.username, User.first_name, User.last_name)

        users_stmt = self._apply_user_ordering(users_stmt, search)
        users_stmt = users_stmt.limit(items_per_page).offset(offset)

        users_result = await self.session.execute(users_stmt)
        rows = users_result.all()

        # Convert rows to dicts
        return [
            {
                "username": row.username,
                "first_name": row.first_name,
                "last_name": row.last_name,
                "rit_edu_account_type": row.rit_edu_account_type,
                "rit_edu_campus_u": row.rit_edu_campus_u,
                "rit_edu_campus_g": row.rit_edu_campus_g,
                "rit_edu_college_u": row.rit_edu_college_u,
                "rit_edu_college_g": row.rit_edu_college_g,
            }
            for row in rows
        ]

    async def _fetch_user_roles(self, usernames: list[str]) -> dict[str, list[dict]]:
        """Fetch all roles for given usernames."""
        roles_stmt = (
            select(UserRole.username, Role.id, Role.name, Role.description)
            .select_from(UserRole)
            .join(Role, Role.id == UserRole.role_id)
            .where(UserRole.username.in_(usernames))
            .order_by(UserRole.username, Role.id)
        )

        roles_result = await self.session.execute(roles_stmt)
        rows = roles_result.all()

        roles_by_username: dict[str, list[dict]] = defaultdict(list)
        for username, role_id, role_name, role_description in rows:
            roles_by_username[username].append(
                {
                    "id": role_id,
                    "name": role_name,
                    "description": role_description,
                }
            )

        return roles_by_username

    def _build_user_schemas(
        self, users: list[dict], roles_by_username: dict[str, list[dict]]
    ) -> list[UserSchema]:
        """Build UserSchema objects from users and their roles."""
        users_data: list[UserSchema] = []
        for u in users:
            roles = roles_by_username.get(u["username"], [])
            roles_data = [
                RoleSchema(
                    id=r["id"],
                    name=r["name"],
                    description=r["description"],
                    permissions=[],
                )
                for r in roles
            ]
            users_data.append(
                UserSchema(
                    username=u["username"],
                    first_name=u["first_name"],
                    last_name=u["last_name"],
                    roles=roles_data,
                    rit_edu_account_type=u["rit_edu_account_type"],
                    rit_edu_campus_u=u["rit_edu_campus_u"],
                    rit_edu_campus_g=u["rit_edu_campus_g"],
                    rit_edu_college_u=u["rit_edu_college_u"],
                    rit_edu_college_g=u["rit_edu_college_g"],
                )
            )
        return users_data

    async def get_users_data(
        self,
        page: int,
        items_per_page: int,
        role_name: str | None = None,
        search: str | None = None,
    ) -> tuple[PageInfo, list[UserSchema]]:
        """Retrieve a paginated list of users with their roles (SQL pagination + 1 role query)."""
        try:
            # Normalize pagination inputs
            page = max(page, 1)
            items_per_page = max(items_per_page, 1)

            # Fetch paginated users first to check if there are any
            page_users = await self._fetch_paginated_users(page, items_per_page, role_name, search)

            if not page_users:
                raise UserNotFoundError(
                    message="No users found for this page.",
                    context={
                        "page": page,
                        "items_per_page": items_per_page,
                        "role_name": role_name,
                        "search": search,
                    },
                )

            # Get total count (do this after so it only runs if we have results)
            total_items = await self._get_total_users_count(role_name, search)
            total_pages = max(1, math.ceil(total_items / items_per_page))

            # Fetch roles for users
            usernames = [u["username"] for u in page_users]
            roles_by_username = await self._fetch_user_roles(usernames)

            # Build schemas
            users_data = self._build_user_schemas(page_users, roles_by_username)

            # Build page info
            page_info = PageInfo(
                page=page,
                items=len(users_data),
                total_items=total_items,
                total_pages=total_pages,
            )

            return page_info, users_data

        except UserNotFoundError:
            raise
        except Exception as e:
            raise DBError(
                message="Failed to list users.",
                context={
                    "op": "user_list",
                    "page": page,
                    "items": items_per_page,
                    "role_name": role_name,
                    "search": search,
                    "error": repr(e),
                },
            ) from e

    async def get_user_profile(self, user: User) -> ReturnUserProfile:
        """Retrieve the profile of a user, including their roles and committees."""
        try:
            # Roles
            stmt = (
                select(Role)
                .select_from(UserRole)
                .join(Role, Role.id == UserRole.role_id)
                .where(UserRole.username == user.username)
                .order_by(Role.id)
            )
            roles = (await self.session.execute(stmt)).scalars().all()
            roles_data = [
                RoleSchema(id=r.id, name=r.name, description=r.description, permissions=[])
                for r in roles
            ]

            # Committees (load full Committee objects, not just IDs)
            stmt = (
                select(Committee)
                .join(
                    UserCommitteeAssociation, UserCommitteeAssociation.committee_id == Committee.id
                )
                .where(UserCommitteeAssociation.username == user.username)
                .order_by(Committee.id)
            )
            committees = (await self.session.execute(stmt)).scalars().all()
            committees_data = [
                CommitteeSchema(id=c.id, name=c.name, description=c.description) for c in committees
            ]

            return ReturnUserProfile(
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                roles=roles_data,
                committees=committees_data,
                rit_edu_account_type=user.rit_edu_account_type,
                rit_edu_campus_u=user.rit_edu_campus_u,
                rit_edu_campus_g=user.rit_edu_campus_g,
                rit_edu_college_u=user.rit_edu_college_u,
                rit_edu_college_g=user.rit_edu_college_g,
            )
        except Exception as e:
            raise DBError(
                message="Failed to fetch user profile.",
                context={"op": "user_profile", "username": user.username, "error": repr(e)},
            ) from e

    async def sign_petition(self, petition_id: int, user: User) -> PetitionSignResponse:
        """Sign a specific petition."""
        try:
            can_sign, error = await self.can_user_sign_petition(petition_id, user)

            if not can_sign:
                raise error

            # Sign
            await self.session.execute(
                insert(PetitionSignature).values(petition_id=petition_id, user_id=user.username)
            )

            # Increment & Return New Count in one go
            result = await self.session.execute(
                update(Petition)
                .where(Petition.id == petition_id)
                .values(total_signatures=Petition.total_signatures + 1)
                .returning(Petition.total_signatures)
            )
            new_count = result.scalar()

            await self.session.commit()

            return PetitionSignResponse(
                signed=True,
                total_signatures=new_count,
            )

        except Exception as e:
            await self.session.rollback()
            raise DBError(
                message="Failed to sign petition.",
                context={
                    "op": "user_sign_petition",
                    "petition_id": petition_id,
                    "username": user,
                    "error": repr(e),
                },
            ) from e

    async def unsign_petition(self, petition_id: int, user: User) -> PetitionSignResponse:
        """Remove a user's signature from a petition."""
        try:
            # Ensure petition exists
            petition = await self.session.get(Petition, petition_id)
            if not petition:
                raise PetitionNotFoundError(message=f"Petition with ID {petition_id} not found.")

            # Ensure user has signed
            stmt = select(PetitionSignature).where(
                and_(
                    PetitionSignature.petition_id == petition_id,
                    PetitionSignature.user_id == user.username,
                )
            )
            record = (await self.session.execute(stmt)).scalars().first()
            if record is None:
                raise UserHasNotSignedPetitionError(
                    message=f"User '{user.username}' has not signed this petition."
                )

            # Unsign & decrement
            await self.session.execute(
                delete(PetitionSignature).where(
                    and_(
                        PetitionSignature.petition_id == petition_id,
                        PetitionSignature.user_id == user.username,
                    )
                )
            )

            result = await self.session.execute(
                update(Petition)
                .where(Petition.id == petition_id)
                .values(total_signatures=Petition.total_signatures - 1)
                .returning(Petition.total_signatures)
            )
            new_count = result.scalar()

            await self.session.commit()

            return PetitionSignResponse(signed=False, total_signatures=new_count)

        except (PetitionNotFoundError, UserHasNotSignedPetitionError):
            raise
        except Exception as e:
            await self.session.rollback()
            raise DBError(
                message="Failed to unsign petition.",
                context={
                    "op": "user_unsign_petition",
                    "petition_id": petition_id,
                    "username": user.username,
                    "error": repr(e),
                },
            ) from e

    async def can_user_sign_petition(self, petition_id: int, user: User) -> tuple:
        """Check if the user has signed a specific petition."""
        try:
            stmt = (
                select(Petition)
                .where(Petition.id == petition_id)
                .options(selectinload(Petition.author))
            )
            petition = (await self.session.execute(stmt)).unique().scalars().first()
            if not petition:
                return False, PetitionNotFoundError(
                    message=f"Petition with ID {petition_id} not found."
                )

            if petition.author.username == user.username:
                return False, OwnPetitionError(
                    message=f"User '{user.username}' is the author of this petition and cannot sign it."
                )

            # Already signed?
            stmt = select(PetitionSignature).where(
                and_(
                    PetitionSignature.petition_id == petition_id,
                    PetitionSignature.user_id == user.username,
                )
            )
            if (await self.session.execute(stmt)).scalars().first() is not None:
                return False, PetitionAlreadySignedError(
                    message=f"User '{user.username}' has already signed this petition."
                )

            if datetime.now(UTC) > petition.expires:
                return False, PetitionClosedError(
                    message=f"Petition with ID {petition_id} is expired. Cannot sign."
                )

            if petition.has_response or petition.status == StatusEnum.RESPONDED:
                return False, PetitionClosedError(
                    message=f"Petition with ID {petition_id} already has a response. Cannot sign."
                )

            return True, None

        except Exception as e:
            raise DBError(
                message="Failed to check if user has signed petition.",
                context={
                    "op": "can_user_sign_petition",
                    "petition_id": petition_id,
                    "username": user.username,
                    "error": repr(e),
                },
            ) from e

    async def update_user_role(self, username: str, role_id: int) -> None:
        """Update a user's role."""
        try:
            # User exists?
            user = await self.session.get(User, username)
            if not user:
                raise UserNotFoundError(message=f"User '{username}' not found.")

            # Role exists?
            role = await self.session.get(Role, role_id)
            if not role:
                raise RoleNotFoundError(message=f"Role with ID {role_id} not found.")

            # Current role association
            user_role = (
                (await self.session.execute(select(UserRole).where(UserRole.username == username)))
                .scalars()
                .first()
            )

            if user_role:
                user_role.role_id = role_id
            else:
                self.session.add(UserRole(username=username, role_id=role_id))

            await self.session.commit()

        except (UserNotFoundError, RoleNotFoundError):
            raise
        except Exception as e:
            await self.session.rollback()
            raise DBError(
                message="Failed to update user role.",
                context={
                    "op": "user_role_update",
                    "username": username,
                    "role_id": role_id,
                    "error": repr(e),
                },
            ) from e


def get_user_service(
    session: Annotated[AsyncSession, Depends(get_async_db_session)],
) -> UserService:
    """Dependency to get UserService."""
    return UserService(session)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
