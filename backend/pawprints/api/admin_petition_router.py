"""
Admin-only routes for petition deletion management.
"""

from fastapi import APIRouter, Depends, Query

from pawprints.api.service.petition_service import PetitionServiceDep
from pawprints.auth.permission import has_permission
from pawprints.models.schema import PermissionEnum, PetitionDeletionListItem

router = APIRouter(tags=["Admin-Petitions"])


@router.get(
    "/marked-for-deletion",
    response_model=list[PetitionDeletionListItem],
    dependencies=[Depends(has_permission(PermissionEnum.petition_delete_any))],
)
async def list_marked_petitions_endpoint(
    ps: PetitionServiceDep,
    include_expired: bool = Query(False, description="Include petitions ready for deletion"),
) -> list[PetitionDeletionListItem]:
    """
    List all petitions marked for deletion.

    Parameters
    ----------
    ps : PetitionServiceDep
        Petition service dependency.
    include_expired : bool
        Whether to include petitions past their scheduled deletion date.

    Returns
    -------
    list[PetitionDeletionListItem]
        List of marked petitions with metadata.
    """
    return await ps.list_marked_petitions(include_expired=include_expired)
