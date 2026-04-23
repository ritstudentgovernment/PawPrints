from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pawprints.database.session import get_async_db_session
from pawprints.exceptions import DBError  # 1000 / 500
from pawprints.models.orm import Permission
from pawprints.models.schema import PermissionSchema


class PermissionService:
    """Service class for permission-related operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_permissions(self) -> list[PermissionSchema]:
        """
        Retrieve all permissions in the system.

        Returns
        -------
        list[PermissionSchema]

        Raises
        ------
        DBError
            If a database error occurs (code 1000).
        """
        try:
            stmt = select(Permission).order_by(Permission.name.asc())
            res = await self.session.execute(stmt)
            perms = res.scalars().all()
            return [PermissionSchema(id=p.id, name=p.name) for p in perms]
        except Exception as e:
            # Standardized server error with helpful context for observability
            raise DBError(
                message="Failed to fetch permissions.",
                context={"op": "permission_list", "error": repr(e)},
            ) from e


def get_permission_service(
    session: Annotated[AsyncSession, Depends(get_async_db_session)],
) -> PermissionService:
    """Dependency: get PermissionService instance."""
    return PermissionService(session=session)


PermissionServiceDep = Annotated[PermissionService, Depends(get_permission_service)]
