########
# Routes that need user to be authenticated
########

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.exceptions import RequestValidationError

from pawprints.api.service.user_service import UserServiceDep
from pawprints.auth.permission import current_auth_user, has_permission
from pawprints.exceptions import (
    AuthenticationFailedError,  # 2000 / 401
    DBError,  # 1000 / 500
    InvalidRequestBodyError,  # 3000 / 400
    PermissionDeniedError,  # 2001 / 403
    PetitionAlreadySignedError,  # 4001 / 409
    PetitionNotFoundError,  # 4000 / 404
    ServiceError,  # base (pass-through)
    UserHasNotSignedPetitionError,  # 5005 / 400
    UserNotFoundError,  # 5000 / 404
)
from pawprints.models.orm import User
from pawprints.models.schema import (
    PermissionEnum,
    PetitionSignResponse,
    ReturnUserProfile,
    ReturnUsers,
    Success,
    UpdateUserRoleRequest,
)

router = APIRouter(tags=["Users"])


# --- Helpers ------------------------------------------------------------------


def _ctx(op: str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build a consistent context payload for all error types."""
    base: dict[str, Any] = {"op": op}
    if extra:
        base.update(extra)
    return base


def map_validation_error(
    e: RequestValidationError,
    *,
    op: str,
) -> ServiceError:
    """
    Map FastAPI/Pydantic validation errors (422) to a standardized ServiceError.
    """
    return InvalidRequestBodyError(context=_ctx(op, {"errors": e.errors()}))


# --- 2) HTTPException mapper --------------------------------------------------


def _map_http_exc(
    e: HTTPException,
    *,
    op: str,
    hint: str | None = None,
) -> ServiceError:
    """
    Map FastAPI HTTPException to standardized ServiceErrors.

    `hint` helps disambiguate certain status codes:
      - "user"       -> 404 => UserNotFoundError
      - "petition"   -> 404 => PetitionNotFoundError; 409 => PetitionAlreadySignedError
      - "unsign"     -> 400 => UserHasNotSignedPetitionError
    """
    status = e.status_code
    ctx = _ctx(op, {"status_code": status, "original_detail": getattr(e, "detail", None)})

    if status == 401:
        return AuthenticationFailedError(context=ctx)

    if status == 403:
        return PermissionDeniedError(context=ctx)

    if status == 404:
        if hint == "user":
            return UserNotFoundError(context=ctx)
        if hint == "petition":
            return PetitionNotFoundError(context=ctx)
        # sensible default (keeps prior behavior)
        return UserNotFoundError(context=ctx)

    if status == 409:
        if hint == "petition":
            return PetitionAlreadySignedError(context=ctx)
        return DBError(message="Conflict", context=ctx)

    if status == 400 and hint == "unsign":
        return UserHasNotSignedPetitionError(context=ctx)

    if status == 422:
        # Some code paths raise 422 via HTTPException instead of RequestValidationError
        return InvalidRequestBodyError(context=ctx)

    return DBError(message="Unexpected downstream error.", context=ctx)


########################################
# User
########################################


@router.get(
    "/",
    response_model=ReturnUsers,
    dependencies=[Depends(has_permission(PermissionEnum.user_list))],
    description="Retrieve a list of all users.",
)
async def get_user(
    us: UserServiceDep,
    page: int = 1,
    items_per_page: int = 10,
    role_name: str | None = None,
    search: str | None = None,
) -> ReturnUsers:
    """
    Retrieve a paginated list of all users (admin/authorized only).
    Supports filtering by role_name and searching by username.
    Search uses prefix matching (e.g., 'jsmith' matches 'jsmith', 'jsmith123', etc.).
    """
    page_info, users_data = await us.get_users_data(
        page=page, items_per_page=items_per_page, role_name=role_name, search=search
    )
    return ReturnUsers(page_info=page_info, users=users_data)


@router.get(
    "/me",
    response_model=ReturnUserProfile,
    description="Retrieve the profile of the currently authenticated user.",
)
async def get_me(
    us: UserServiceDep,
    current_user: User = Depends(current_auth_user),
) -> ReturnUserProfile:
    """
    Retrieve the profile of the currently authenticated user.
    """
    return await us.get_user_profile(current_user)


@router.post(
    "/{petition_id}/sign",
    response_model=PetitionSignResponse,
)
async def sign_petition(
    us: UserServiceDep,
    petition_id: int,
    current_user: User = Depends(current_auth_user),
) -> PetitionSignResponse:
    """
    Sign a specific petition.
    """
    return await us.sign_petition(petition_id, current_user)


@router.post(
    "/{petition_id}/unsign",
    response_model=PetitionSignResponse,
)
async def unsign_petition(
    us: UserServiceDep,
    petition_id: int,
    current_user: User = Depends(current_auth_user),
) -> PetitionSignResponse:
    """
    Remove a user's signature from a petition.
    """
    return await us.unsign_petition(petition_id, current_user)


@router.get(
    "/{petition_id}/can_sign",
    response_model=Success,
)
async def can_sign_petition(
    us: UserServiceDep,
    petition_id: int,
    current_user: User = Depends(current_auth_user),
) -> Success:
    """
    Check if the current user has signed a specific petition.
    """
    can_sign, error = await us.can_user_sign_petition(petition_id, current_user)

    if not can_sign:
        raise error

    return Success(message="User can sign the petition", status_code=200)


@router.put(
    "/{username}/role",
    response_model=Success,
)
async def update_user_role(
    us: UserServiceDep,
    username: str,
    request: UpdateUserRoleRequest,
    current_user: User = Depends(has_permission(PermissionEnum.user_role_assign)),
) -> Success:
    """
    Update a user's role.
    """
    if username == current_user.username:
        # Prevent self-escalation
        raise PermissionDeniedError(
            message="Users cannot change their own role.",
            context={"self_update": True, "target": username},
        )

    await us.update_user_role(username, request.role_id)
    return Success(message="User role updated successfully", status_code=200)
