from fastapi import APIRouter, Depends

from pawprints.api.service.committee_service import CommitteeServiceDep
from pawprints.auth.permission import has_permission
from pawprints.models.schema import (
    CommitteeMemberCreateRequest,
    CommitteeMemberResponse,
    CommitteeSchema,
    PermissionEnum,
    UserSchema,
)

router = APIRouter(tags=["Committees"])


@router.get(
    "/",
    response_model=list[CommitteeSchema],
    status_code=200,
)
async def view_all_committees(cs: CommitteeServiceDep):
    committees_list = await cs.get_all_committees()
    return committees_list


@router.get(
    "/{committee_id}/members",
    response_model=list[UserSchema],
    status_code=200,
    dependencies=[Depends(has_permission(PermissionEnum.committee_member_list))],
)
async def view_committee_members(cs: CommitteeServiceDep, committee_id: int):
    members_list = await cs.get_committee_members(committee_id=committee_id)
    return members_list


@router.post(
    "/{committee_id}/members",
    response_model=CommitteeMemberResponse,
    status_code=201,
    dependencies=[Depends(has_permission(PermissionEnum.committee_member_add))],
)
async def add_committee_member_endpoint(
    committee_id: int, request_data: CommitteeMemberCreateRequest, cs: CommitteeServiceDep
):
    """
    Add user to a specific committee
    """
    # Call the clean service function with the validated data
    new_member = await cs.add_user_to_committee(
        username_to_add=request_data.username, committee_id=committee_id
    )

    return new_member


@router.post(
    "/create",
    response_model=CommitteeSchema,
    status_code=201,
    dependencies=[Depends(has_permission(PermissionEnum.committee_create))],
)
async def create_committee_endpoint(request_data: CommitteeSchema, cs: CommitteeServiceDep):
    """Create a new Committee with name and description"""
    new_committee = await cs.create_committee(committee_to_add=request_data)
    return new_committee


@router.delete(
    "/delete",
    status_code=201,
    dependencies=[Depends(has_permission(PermissionEnum.committee_delete))],
)
async def delete_committee_endpoint(committee_id: int, cs: CommitteeServiceDep):
    """Delete Committee with ID"""
    await cs.delete_committee(committee_id=committee_id)


@router.post(
    "/{committee_id}/members/role/{role_id}",
    status_code=201,
    dependencies=[Depends(has_permission(PermissionEnum.committee_member_add))],
)
async def add_role_to_committee_endpoint(committee_id: int, role_id: int, cs: CommitteeServiceDep):
    """
    Add all users with a specific role to a committee.
    This endpoint adds all users who have the specified role_id to the committee.
    """
    result = await cs.add_role_to_committee(role_id=role_id, committee_id=committee_id)
    return result


@router.post(
    "/members/role/{role_id}/all",
    status_code=201,
    dependencies=[Depends(has_permission(PermissionEnum.committee_member_add))],
)
async def add_role_to_all_committees_endpoint(role_id: int, cs: CommitteeServiceDep):
    """
    Add all users with a specific role to all committees.
    This endpoint adds all users who have the specified role_id to every committee in the system.
    """
    result = await cs.add_role_to_all_committees(role_id=role_id)
    return result
