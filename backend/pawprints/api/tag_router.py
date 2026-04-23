"""
Tag management router.
"""

from fastapi import APIRouter, Depends, Query

from pawprints.api.service.tag_service import TagServiceDep
from pawprints.auth.permission import has_permission
from pawprints.models.orm import User
from pawprints.models.schema import (
    PermissionEnum,
    PetitionTagAssign,
    PetitionTagResponse,
    TagCreate,
    TagListResponse,
    TagSchema,
    TagUpdate,
)

router = APIRouter(tags=["Tags"])


@router.post(
    "",
    response_model=TagSchema,
    dependencies=[Depends(has_permission(PermissionEnum.tag_create))],
    status_code=201,
)
async def create_tag_endpoint(
    ts: TagServiceDep,
    tag_data: TagCreate,
) -> TagSchema:
    """
    Create a new tag.

    Parameters
    ----------
    ts : TagService
        Tag service dependency.
    tag_data : TagCreate
        Tag data.

    Returns
    -------
    TagSchema
        The created tag.

    Raises
    ------
    DBError
        If tag with this name already exists or creation fails.
    """
    return await ts.create_tag(tag_data)


@router.get(
    "",
    response_model=TagListResponse,
)
async def list_tags_endpoint(
    ts: TagServiceDep,
    page: int = Query(1, ge=1),
    items_per_page: int = Query(50, ge=1, le=100),
) -> TagListResponse:
    """
    List all tags with pagination.

    Parameters
    ----------
    ts : TagService
        Tag service dependency.
    page : int
        Page number (1-indexed).
    items_per_page : int
        Number of items per page.

    Returns
    -------
    TagListResponse
        Paginated list of tags.
    """
    return await ts.list_tags(page=page, items_per_page=items_per_page)


@router.get(
    "/{tag_id}",
    response_model=TagSchema,
)
async def get_tag_endpoint(
    ts: TagServiceDep,
    tag_id: int,
) -> TagSchema:
    """
    Get a tag by ID.

    Parameters
    ----------
    ts : TagService
        Tag service dependency.
    tag_id : int
        The tag ID.

    Returns
    -------
    TagSchema
        The tag.

    Raises
    ------
    TagNotFoundError
        If the tag doesn't exist.
    """
    return await ts.get_tag(tag_id)


@router.put(
    "/{tag_id}",
    dependencies=[Depends(has_permission(PermissionEnum.tag_update))],
    response_model=TagSchema,
)
async def update_tag_endpoint(
    ts: TagServiceDep,
    tag_id: int,
    tag_data: TagUpdate,
) -> TagSchema:
    """
    Update a tag.

    Parameters
    ----------
    ts : TagService
        Tag service dependency.
    tag_id : int
        The tag ID.
    tag_data : TagUpdate
        Tag data to update.

    Returns
    -------
    TagSchema
        The updated tag.

    Raises
    ------
    TagNotFoundError
        If the tag doesn't exist.
    DBError
        If update fails.
    """
    return await ts.update_tag(tag_id, tag_data)


@router.delete(
    "/{tag_id}",
    dependencies=[Depends(has_permission(PermissionEnum.tag_delete))],
    status_code=204,
)
async def delete_tag_endpoint(
    ts: TagServiceDep,
    tag_id: int,
) -> None:
    """
    Delete a tag.

    Parameters
    ----------
    ts : TagService
        Tag service dependency.
    tag_id : int
        The tag ID.

    Raises
    ------
    TagNotFoundError
        If the tag doesn't exist.
    DBError
        If deletion fails.
    """
    await ts.delete_tag(tag_id)


@router.post(
    "/petition/{petition_id}",
    response_model=PetitionTagResponse,
)
async def add_tag_to_petition_endpoint(
    ts: TagServiceDep,
    petition_id: int,
    tag_data: PetitionTagAssign,
    current_user: User = Depends(has_permission(PermissionEnum.petition_tag_add)),
) -> PetitionTagResponse:
    """
    Add a tag to a petition (replaces existing tag if any).

    Parameters
    ----------
    ts : TagService
        Tag service dependency.
    petition_id : int
        The petition ID.
    tag_data : PetitionTagAssign
        Tag assignment data.
    current_user : User
        Current authenticated user with petition.tag.add permission.

    Returns
    -------
    PetitionTagResponse
        The tag assignment.

    Raises
    ------
    PetitionNotFoundError
        If the petition doesn't exist.
    TagNotFoundError
        If the tag doesn't exist.
    DBError
        If assignment fails.
    """
    return await ts.add_tag_to_petition(petition_id, tag_data, current_user)


@router.delete(
    "/petition/{petition_id}",
    dependencies=[Depends(has_permission(PermissionEnum.tag_delete))],
    status_code=204,
)
async def remove_tag_from_petition_endpoint(
    ts: TagServiceDep,
    petition_id: int,
) -> None:
    """
    Remove tag from a petition.

    Parameters
    ----------
    ts : TagService
        Tag service dependency.
    petition_id : int
        The petition ID.

    Raises
    ------
    PetitionNotFoundError
        If no tag is assigned to this petition.
    DBError
        If removal fails.
    """
    await ts.remove_tag_from_petition(petition_id)


@router.get(
    "/petition/{petition_id}",
    response_model=PetitionTagResponse | None,
)
async def get_petition_tag_endpoint(
    ts: TagServiceDep,
    petition_id: int,
) -> PetitionTagResponse | None:
    """
    Get the tag assigned to a petition.

    Parameters
    ----------
    ts : TagService
        Tag service dependency.
    petition_id : int
        The petition ID.

    Returns
    -------
    PetitionTagResponse | None
        The tag assignment, or None if no tag is assigned.
    """
    return await ts.get_petition_tag(petition_id)
