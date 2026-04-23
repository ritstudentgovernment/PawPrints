from __future__ import annotations

import logging

from fastapi import Depends, Request
from sqlalchemy import and_, exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from config import Config
from pawprints.api.utils import DBSessionDep
from pawprints.auth.jwt import decode_jwt_token
from pawprints.database.session import get_async_db_session
from pawprints.exceptions import (
    AuthenticationFailedError,  # 2000 / 401
    InternalServerError,  # 1000 / 500
    PermissionDeniedError,  # 2001 / 403
    UserNotFoundError,  # 5000 / 404
)
from pawprints.models.orm import Permission, RolePermission, User, UserRole
from pawprints.models.schema import PermissionEnum

logger = logging.getLogger("pawprints.auth")
config = Config()


def is_dev(config: Config) -> bool:
    return (config.MODE or "").upper() == "DEV"


def _perm_name(p: PermissionEnum | str) -> str:
    return p.value if isinstance(p, PermissionEnum) else str(p)


def has_permission(permission: PermissionEnum | str):
    """
    Dependency: ensure the current user has a role that grants ``permission``.

    Raises
    ------
    PermissionDeniedError
        If the user has no roles or lacks the required permission.
    """
    perm = _perm_name(permission)

    async def permission_checker(
        user: User = Depends(current_auth_user),
        db: AsyncSession = Depends(get_async_db_session),
    ) -> User:
        if is_dev(config):
            logger.debug("[DEV] Bypassing permission check '%s' for %s", perm, user.username)
            return user

        has_any_role = await db.scalar(select(exists().where(UserRole.username == user.username)))
        if not has_any_role:
            raise PermissionDeniedError(
                message="User has no roles.",
                context={"username": user.username, "op": "has_permission:any_role"},
            )

        has_perm = await db.scalar(
            select(
                exists().where(
                    and_(
                        UserRole.username == user.username,
                        RolePermission.role_id == UserRole.role_id,
                        RolePermission.permission_id == Permission.id,
                        Permission.name == perm,
                    )
                )
            )
        )
        if not has_perm:
            raise PermissionDeniedError(
                message=f"User lacks required permission: `{perm}`",
                context={"username": user.username, "permission": perm, "op": "has_permission"},
            )

        return user

    return permission_checker


async def current_auth_user(request: Request, session: DBSessionDep) -> User:
    """
    Extract a JWT from the Authorization header (Bearer) or ``pawcess`` cookie
    and return the matching User row.

    Raises
    ------
    InternalServerError
        DEV mode enabled but ``DEV_USERNAME`` is not configured.
    AuthenticationFailedError
        Token missing, invalid, or expired.
    UserNotFoundError
        Token is valid but references a username not in the database.
    """
    if is_dev(config):
        dev_username = config.DEV_USERNAME
        if not dev_username:
            raise InternalServerError(
                message="DEV_USERNAME environment variable not set for development.",
                context={"op": "current_auth_user:dev_config"},
            )
        user = await session.get(User, dev_username)
        if not user:
            raise UserNotFoundError(
                message=f"Development user '{dev_username}' not found in the database.",
                context={"username": dev_username, "op": "current_auth_user:dev_lookup"},
            )
        return user

    # Prefer Authorization header; fall back to cookie.
    raw = request.headers.get("Authorization") or request.cookies.get(config.AUTH_COOKIE_NAME)
    if not raw:
        raise AuthenticationFailedError(
            message="Missing authentication token.",
            context={"op": "current_auth_user:token_source"},
        )

    token = raw.removeprefix("Bearer ").strip()

    try:
        payload = decode_jwt_token(token)
        username: str | None = payload.get("username")
        if not username:
            raise ValueError("username claim missing from token")
    except Exception as e:
        raise AuthenticationFailedError(
            message="Invalid or expired token.",
            context={"op": "current_auth_user:decode", "error": repr(e)},
        ) from e

    user = await session.get(User, username)
    if not user:
        raise UserNotFoundError(
            message="User not found.",
            context={"username": username, "op": "current_auth_user:db_lookup"},
        )

    return user
