"""
Permission API router
Contains endpoints for managing role.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from pawprints.api.service.permission_service import PermissionServiceDep
from pawprints.api.utils import _std_perm
from pawprints.auth.permission import has_permission
from pawprints.models.schema import PermissionEnum, ReturnPermissions

router = APIRouter(tags=["Permissions"])


# get all permissions (admin only)
@router.get(
    "/",
    response_model=ReturnPermissions,
    dependencies=[Depends(_std_perm(has_permission(PermissionEnum.permission_list)))],
    description="Retrieve all permissions in the system. Needs 'admin' or 'pres' role.",
)
async def get_permissions(ps: PermissionServiceDep) -> ReturnPermissions:
    """
    Retrieve all permissions in the system. Admin only.

    Returns
    -------
    ReturnPermissions
        A Pydantic schema containing a list of all permissions.

    Raises
    ------
    PermissionDeniedError
        Raised by the dependency if the user lacks `permission.list`.
    DBError
        On database/service failures while fetching permissions.
    """
    perms_data = await ps.get_permissions()
    return ReturnPermissions(permissions=perms_data)
