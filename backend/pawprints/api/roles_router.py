"""
Roles API router
Contains endpoints for managing role.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.exceptions import RequestValidationError

from pawprints.api.service.role_service import RoleServiceDep
from pawprints.api.utils import _std_perm
from pawprints.auth.permission import has_permission
from pawprints.exceptions import (
    DBError,  # 1000 / 500
    InvalidRequestBodyError,  # 3000 / 400
    PermissionDeniedError,  # 2001 / 403
    PermissionNotFoundError,  # 6002 / 404
    RoleAlreadyExistsError,  # 6001 / 409
    RoleNotFoundError,  # 6000 / 404
    ServiceError,  # base (for pass-through)
)
from pawprints.models.schema import (
    DuplicateRoleRequest,
    PermissionEnum,
    ReturnRolesResponse,
    RoleSchema,
    Success,
    UpdateRolePermissionsRequest,
)

router = APIRouter(tags=["Roles"])


# --- Map legacy HTTP/validation exceptions to standardized ServiceErrors -------
def _map_http_exc(
    e: Exception,
    *,
    op: str,
    hint: str | None = None,
) -> ServiceError:
    """
    Convert HTTPException/RequestValidationError to ServiceError subclass.
    `hint` may be 'role' or 'permission' to disambiguate 404s.
    """
    ctx: dict[str, Any] = {"op": op}

    # Validation from FastAPI/Pydantic
    if isinstance(e, RequestValidationError):
        ctx["errors"] = e.errors()
        return InvalidRequestBodyError(context=ctx)

    # HTTPException from service/deps
    if isinstance(e, HTTPException):
        ctx["original_detail"] = getattr(e, "detail", None)
        if e.status_code == 403:
            return PermissionDeniedError(context=ctx)
        if e.status_code == 404:
            # Disambiguate when updating role permissions
            if hint == "permission":
                return PermissionNotFoundError(context=ctx)
            return RoleNotFoundError(context=ctx)
        if e.status_code == 409:
            return RoleAlreadyExistsError(context=ctx)
        if e.status_code == 422:
            # Normalize to 3000 per your spec (HTTP 400)
            return InvalidRequestBodyError(context=ctx)
        # Anything else -> generic DB/Server error
        return DBError(
            message="Unexpected downstream error.", context={**ctx, "status_code": e.status_code}
        )

    # Fallback generic
    return DBError(message="Unhandled server error.", context=ctx)


# ------------------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------------------


# get all roles (admin only)
@router.get(
    "/",
    response_model=ReturnRolesResponse,
    dependencies=[Depends(_std_perm(has_permission(PermissionEnum.role_list)))],
    description="Retrieve all roles in the system. Needs 'admin' or 'pres' role.",
)
async def get_roles(rs: RoleServiceDep) -> ReturnRolesResponse:
    """
    Retrieve all roles in the system. Admin only.

    Raises
    ------
    PermissionDeniedError
        If the caller lacks `role.list`.
    DBError
        For unexpected database/service failures.
    """
    roles_data = await rs.get_roles()
    return ReturnRolesResponse(roles=roles_data)


# create a role (admin only)
@router.post(
    "/",
    response_model=RoleSchema,
    dependencies=[Depends(_std_perm(has_permission(PermissionEnum.role_create)))],
    description="Create a new role in the system. Needs 'admin' role.",
)
async def create_role(role: RoleSchema, rs: RoleServiceDep) -> RoleSchema:
    """
    Create a new role.

    Raises
    ------
    RoleAlreadyExistsError
        If a role with the same name already exists (6001).
    InvalidRequestBodyError
        If body fails validation (3000).
    DBError
        On unexpected database/service failure.
    """
    return await rs.create_role(role)


# delete a role (admin only)
@router.delete(
    "/{role_id}",
    response_model=Success,
    dependencies=[Depends(_std_perm(has_permission(PermissionEnum.role_delete)))],
    description="Delete a role from the system. Needs 'admin' role.",
)
async def delete_role(role_id: int, rs: RoleServiceDep) -> Success:
    """
    Delete a role and its associations.

    Raises
    ------
    RoleNotFoundError
        If the role does not exist (6000).
    DBError
        On unexpected database/service failure.
    """
    await rs.delete_role(role_id)
    return Success(message="Role deleted successfully.", status_code=200)


# update a role (admin only)
@router.put(
    "/{role_id}",
    response_model=RoleSchema,
    dependencies=[Depends(_std_perm(has_permission(PermissionEnum.role_update)))],
    description="Update a role in the system. Needs 'admin' role.",
)
async def update_role(role_id: int, role: RoleSchema, rs: RoleServiceDep) -> RoleSchema:
    """
    Update a role's name/description.

    Raises
    ------
    RoleNotFoundError
        If the role does not exist (6000).
    RoleAlreadyExistsError
        If renaming to an existing role name (6001).
    InvalidRequestBodyError
        If body fails validation (3000).
    DBError
        On unexpected failures.
    """
    return await rs.update_role(role_id, role)


# update role permissions (admin only)
@router.put(
    "/{role_id}/permissions",
    response_model=RoleSchema,
    dependencies=[Depends(_std_perm(has_permission(PermissionEnum.role_permission_assign)))],
)
async def update_role_permissions(
    role_id: int, request: UpdateRolePermissionsRequest, rs: RoleServiceDep
) -> RoleSchema:
    """
    Update the permissions of a role.

    Raises
    ------
    RoleNotFoundError
        If the role does not exist (6000).
    PermissionNotFoundError
        If any permission IDs are invalid (6002).
    InvalidRequestBodyError
        If body fails validation (3000).
    DBError
        On unexpected failures.
    """
    return await rs.update_role_permissions(role_id, request.permission_ids)


# get roles with permissions (admin only)
@router.get(
    "/permissions",
    response_model=ReturnRolesResponse,
    dependencies=[Depends(_std_perm(has_permission(PermissionEnum.role_list)))],
    description="Retrieve all roles with their associated permissions in the system. Needs 'admin' or 'pres' role.",
)
async def get_roles_with_permissions(rs: RoleServiceDep) -> ReturnRolesResponse:
    """
    Retrieve all roles with their associated permissions. Admin only.

    Raises
    ------
    PermissionDeniedError
        If the caller lacks `role.list`.
    DBError
        On unexpected failures.
    """
    roles_data = await rs.get_roles_with_permissions()
    return ReturnRolesResponse(roles=roles_data)


# duplicate a role (admin only)
@router.post(
    "/{role_id}/duplicate",
    response_model=RoleSchema,
    dependencies=[Depends(_std_perm(has_permission(PermissionEnum.role_create)))],
    description="Duplicate an existing role with all its permissions. Needs 'admin' role.",
)
async def duplicate_role(
    role_id: int, request: DuplicateRoleRequest, rs: RoleServiceDep
) -> RoleSchema:
    """
    Duplicate a role with all its permissions.

    Raises
    ------
    RoleNotFoundError
        If the source role does not exist (6000).
    RoleAlreadyExistsError
        If the new role name already exists (6001).
    InvalidRequestBodyError
        If body fails validation (3000).
    DBError
        On unexpected failures.
    """
    return await rs.duplicate_role(role_id, request.new_name)
