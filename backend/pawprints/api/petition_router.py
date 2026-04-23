from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from pawprints.api.service.petition_service import PetitionServiceDep
from pawprints.auth.permission import current_auth_user, has_permission
from pawprints.models.orm import (
    User,
)
from pawprints.models.schema import (
    CommitteeAssignmentCreate,
    CommitteeSchema,
    CreateDraftUpdate,
    CreatePetition,
    PermissionEnum,
    PetitionCreateResponse,
    PetitionDeletionMarkRequest,
    PetitionPageSchema,
    PetitionSearchParams,
    PetitionUpdateSchema,
    ReportCreate,
    ReturnPetition,
    ReviewUpdateRequest,
    ReviewUpdateResponse,
    Success,
    UpdateSchema, PetitionDescriptionSchema,
)

router = APIRouter(tags=["Petitions"])

########################################
# Petition
########################################


def _handle_int(qp, param, field, default, data):
    value = qp.get(param)
    if value is None:
        if default is not None:
            data[field] = default
        return
    try:
        data[field] = int(value)
    except ValueError:
        raise ValueError(f"Invalid {param} value: {value}")


def _handle_int_list(qp, param, field, default, data):
    values = qp.getlist(param)
    if not values:
        return
    parsed = []
    for v in values:
        try:
            parsed.append(int(v))
        except ValueError:
            raise ValueError(f"Invalid {param} value: {v}")
    data[field] = parsed


def _handle_bool(qp, param, field, default, data):
    value = qp.get(param)
    if value is None:
        return
    data[field] = value.lower() in ("1", "true", "yes", "on")


def _handle_string(qp, param, field, default, data):
    value = qp.get(param)
    if value is not None:
        data[field] = value


def _handle_string_list(qp, param, field, default, data):
    values = qp.getlist(param)
    if values:
        data[field] = values


async def get_search_params(request: Request) -> PetitionSearchParams:
    qp = request.query_params
    data: dict = {}

    RULES = [
        ("page", "page", _handle_int, 1),
        ("items_per_page", "per_page", _handle_int, None),
        ("query", "q", _handle_string, None),
        ("status", "status", _handle_int_list, None),
        ("tag_id", "tag_id", _handle_int_list, None),
        ("has_response", "has_response", _handle_bool, None),
        ("is_draft", "is_draft", _handle_bool, None),
        ("signatures", "signatures", _handle_string, None),
        ("created", "created", _handle_string, None),
        ("include", "include", _handle_string_list, None),
        ("sort", "sort", _handle_string_list, None),
    ]

    # Single loop, no branches → C901 approves
    for param, field, handler, default in RULES:
        handler(qp, param, field, default, data)

    model = PetitionSearchParams.model_validate(data)
    model.finalize()
    return model


@router.get("", response_model=ReturnPetition, summary="List Petitions (filters only)")
async def list_petitions(
    ps: PetitionServiceDep,
    p: PetitionSearchParams = Depends(get_search_params),
) -> ReturnPetition:
    return await ps.list_filtered(p=p)


@router.get("/search", response_model=ReturnPetition, summary="Search Petitions")
async def search_petitions(
    ps: PetitionServiceDep,
    p: PetitionSearchParams = Depends(get_search_params),
) -> ReturnPetition:
    ps.logger.debug(f"Search params: {p.model_dump()}")

    return await ps.search(p=p)


@router.get(
    "/{petition_id}/committee",
    response_model=CommitteeSchema | None,
)
async def get_petition_committee(
    petition_id: int,
    ps: PetitionServiceDep,
) -> CommitteeSchema | None:
    return await ps.get_petition_committee(petition_id)


@router.get(
    "/{petition_id}",
    response_model=PetitionPageSchema,
)
async def get_petition_by_id(
    ps: PetitionServiceDep,
    petition_id: int,
) -> PetitionPageSchema:
    """
    Retrieve a petition by its unique identifier.

    Parameters
    ----------
    ps : PetitionServiceDep
        Active database session dependency.
    petition_id : int
        Unique identifier of the petition to retrieve.

    Returns
    -------
    PetitionPageSchema
        Detailed information about the requested petition.

    Raises
    ------
    ServiceError
        Propagates service-layer errors for global handling.
    DBError
        Raised when an unexpected failure occurs while fetching the petition.
    """
    return await ps.get_petition_by_id(petition_id=petition_id)


@router.get("/user/me", response_model=ReturnPetition, summary="List My Petitions")
async def list_my_petitions(
    ps: PetitionServiceDep,
    page: int = 1,
    items_per_page: int = 10,
    current_user: User = Depends(current_auth_user),
) -> ReturnPetition:
    """
    Retrieve petitions created by the currently authenticated user.

    Parameters
    ----------
    ps : PetitionServiceDep
        Active database session dependency.
    page : int
        Page number for pagination (default: 1).
    items_per_page : int
        Number of items per page (default: 10).
    current_user : User
        Authenticated user extracted from the request context.

    Returns
    -------
    ReturnPetition
        Paginated collection of petitions authored by the current user.
    """
    return await ps.get_user_petitions(user=current_user, page=page, items_per_page=items_per_page)


@router.get(
    "/{petition_id}/description",
    response_model=PetitionDescriptionSchema,
)
async def get_petition_description_endpoint(
        ps: PetitionServiceDep,
        petition_id: int,
) -> PetitionDescriptionSchema:
    """
    Get a petition description

    Parameters
    ----------
    petition_id : int

    Returns
    -------
    PetitionDescriptionSchema
        description for the requested petition made by the petition creator.
    """
    return await ps.get_petition_description(petition_id=petition_id)


@router.post(
    "/create",
    response_model=PetitionCreateResponse,
)
async def create_petition_endpoint(
    ps: PetitionServiceDep,
    petition: CreatePetition,
    current_user: User = Depends(has_permission(PermissionEnum.petition_create)),
) -> PetitionCreateResponse:
    """
    Create a new petition.

    Parameters
    ----------
    ps : PetitionServiceDep
        Active database session dependency.
    petition : CreatePetition
        Petition payload supplied by the requester.
    current_user : User
        Authenticated user extracted from the request context.

    Returns
    -------
    Success
        Confirmation message containing the newly created petition ID.

    Raises
    ------
    ServiceError
        Propagates service-layer errors for global handling.
    DBError
        Raised when an unexpected failure occurs while creating the petition.
    """
    # Ensure author is the current user (immutably update the model)
    return await ps.create_petition(petition=petition, user=current_user)


@router.put(
    "/{petition_id}",
    response_model=PetitionCreateResponse,
)
async def edit_petition_endpoint(
    ps: PetitionServiceDep,
    petition_id: int,
    petition: CreatePetition,
    current_user: User = Depends(has_permission(PermissionEnum.petition_create)),
) -> PetitionCreateResponse:
    """
    Create a new petition.

    Parameters
    ----------
    ps : PetitionServiceDep
        Active database session dependency.
    petition_id : int
        Identifier of the petition to edit.
    petition : CreatePetition
        Petition payload supplied by the requester.
    current_user : User
        Authenticated user extracted from the request context.

    Returns
    -------
    Success
        Confirmation message containing the newly created petition ID.

    Raises
    ------
    ServiceError
        Propagates service-layer errors for global handling.
    DBError
        Raised when an unexpected failure occurs while creating the petition.
    """
    # Ensure author is the current user (immutably update the model)
    return await ps.edit_draft_petition(
        petition_id=petition_id, petition=petition, user=current_user
    )


@router.post(
    "/{petition_id}/report",
    response_model=Success,
)
async def report_petition(
    ps: PetitionServiceDep,
    petition_id: int,
    report: ReportCreate,
    current_user: User = Depends(has_permission(PermissionEnum.report_petition_create)),
) -> Success:
    """
    Submit a report for a petition.

    Parameters
    ----------
    ps : PetitionServiceDep
        Active database session dependency.
    petition_id : int
        Identifier of the petition to report.
    report : ReportCreate
        Report payload describing the issue with the petition.
    current_user : User
        Authenticated user submitting the report.

    Returns
    -------
    Success
        Confirmation message that the petition was reported.

    Raises
    ------
    ServiceError
        Propagates service-layer errors for global handling.
    DBError
        Raised when an unexpected failure occurs while reporting the petition.
    """
    await ps.report_petition(petition_id=petition_id, report=report, current_user=current_user)
    return Success(message="Petition reported successfully", status_code=200)


@router.post(
    "/{petition_id}/charge",
    response_model=Success,
    dependencies=[Depends(has_permission(PermissionEnum.petition_committee_charge))],
)
async def charge_petition_endpoint(
    ps: PetitionServiceDep, petition_id: int, assignment: CommitteeAssignmentCreate
) -> Success:
    """
    Assign a petition to a committee. Replaces any existing committee assignment.

    Parameters
    ----------
    ps : PetitionServiceDep
        Active database session dependency.
    petition_id : int
        Identifier of the petition to assign.
    assignment : CommitteeAssignmentCreate
        Committee identifier to associate with the petition.

    Returns
    -------
    Success
        Confirmation message that the petition was charged.

    Raises
    ------
    ServiceError
        Propagates service-layer errors for global handling.
    DBError
        Raised when an unexpected failure occurs while charging the petition.
    """
    await ps.charge_petition(petition_id=petition_id, committee_id=assignment.committee_id)
    return Success(message="Petition charged successfully", status_code=200)


@router.delete(
    "/{petition_id}/unassign",
    response_model=Success,
    dependencies=[Depends(has_permission(PermissionEnum.petition_committee_charge))],
)
async def unassign_petition_endpoint(
    ps: PetitionServiceDep, petition_id: int, assignment: CommitteeAssignmentCreate
) -> Success:
    """
    Remove committee assignment from a petition.

    Parameters
    ----------
    ps : PetitionServiceDep
        Active database session dependency.
    petition_id : int
        Identifier of the petition to unassign.
    assignment : CommitteeAssignmentCreate
        Committee identifier to detach from the petition.

    Returns
    -------
    Success
        Confirmation message that the petition was unassigned.

    Raises
    ------
    ServiceError
        Propagates service-layer errors for global handling.
    DBError
        Raised when an unexpected failure occurs while unassigning the petition.
    """
    await ps.unassign_petition(petition_id=petition_id, committee_id=assignment.committee_id)
    return Success(message="Petition untagged successfully", status_code=200)


@router.post(
    "/{petition_id}/draft_update",
    response_model=PetitionUpdateSchema,
)
async def add_petition_draft_update_endpoint(
    ps: PetitionServiceDep,
    petition_id: int,
    draft_update: CreateDraftUpdate,
    user: User = Depends(has_permission(PermissionEnum.petition_update_create)),
) -> PetitionUpdateSchema:
    """
    Add a draft update to a petition.

    Parameters
    ----------
    ps : PetitionServiceDep
        Active database session dependency.
    petition_id : int
        Identifier of the petition to update.
    draft_update : CreateDraftUpdate
        Payload containing the draft update message and optional parent draft ID.
    user : User
        Authenticated user creating the draft update.

    Returns
    -------
    PetitionUpdateSchema
        Updated PetitionUpdate object

    Raises
    ------
    ServiceError
        Propagates service-layer errors for global handling.
    DBError
        Raised when an unexpected failure occurs while adding the draft update.
    """
    return await ps.add_petition_update(
        petition_id=petition_id,
        draft_creator_username=user.username,
        update_message=draft_update.message,
        original_draft_id=draft_update.original_draft_id,
        is_draft=draft_update.is_draft,
        is_response=draft_update.is_response,
    )


@router.put("/{petition_id}/draft_update", response_model=PetitionUpdateSchema)
async def edit_petition_draft_update_endpoint(
    ps: PetitionServiceDep,
    petition_id: int,
    details: UpdateSchema,
    user: User = Depends(has_permission(PermissionEnum.petition_update_create)),
) -> PetitionUpdateSchema:
    """
    Edit a draft update to a petition.

    Parameters
    ----------
    ps : PetitionServiceDep
        Active database session dependency.
    petition_id : int
        Identifier of the petition to update.
    details : PetitionUpdateSchema
        Payload containing the draft update object as well as is_response.
    user : User
        Authenticated user creating the draft update.

    Returns
    -------
    PetitionUpdateSchema
        Updated PetitionUpdate Object

    Raises
    ------
    ServiceError
        Propagates service-layer errors for global handling.
    DBError
        Raised when an unexpected failure occurs while adding the draft update.

    """

    return await ps.edit_draft_update(
        draft_username=user.username, petition_id=petition_id, details=details
    )


@router.delete(
    "/{petition_id}/draft_update/{update_id}",
    response_model=Success,
)
async def delete_petition_draft_update_endpoint(
    ps: PetitionServiceDep,
    petition_id: int,
    update_id: int,
    user: User = Depends(has_permission(PermissionEnum.petition_update_delete)),
) -> Success:
    """
    Delete a draft update from a petition

    Parameters
    ----------
    ps : PetitionServiceDep
        Active database session dependency.
    petition_id : int
        Identifier of the petition to update.
    update_id : int
        ID of update to delete.
    user : User
        Authenticated user creating the draft update.

    Returns
    -------
    Success
        Confirmation message that the draft update was deleted.

    Raises
    ------
    ServiceError
        Propagates service-layer errors for global handling.
    DBError
        Raised when an unexpected failure occurs while adding the draft update.

    """

    await ps.delete_draft_update(
        petition_id=petition_id, update_id=update_id, username=user.username
    )

    return Success(message="Update deleted successfully", status_code=204)


@router.post(
    "/{petition_id}/review",
    response_model=ReviewUpdateResponse,
)
async def add_petition_review_endpoint(
    ps: PetitionServiceDep,
    petition_id: int,
    review: ReviewUpdateRequest,
    reviewer_user: User = Depends(has_permission(PermissionEnum.petition_update_review)),
) -> ReviewUpdateResponse:
    """
    Review a petition draft update.

    Parameters
    ----------
    ps : PetitionServiceDep
        Active database session dependency.
    petition_id : int
        Identifier of the petition containing the draft update.
    review: ReviewUpdateRequest
        Payload containing the draft update ID, approval decision, and optional review message.
    reviewer_user : User
        Authenticated user performing the review.

    Returns
    -------
    Success
        Confirmation message that the draft update was reviewed.

    Raises
    ------
    ServiceError
        Propagates service-layer errors for global handling.
    DBError
        Raised when an unexpected failure occurs while reviewing the draft update.
    """

    return await ps.review_petition_draft_update(
        petition_id=petition_id,
        review=review,
        reviewer_username=reviewer_user.username,
    )


@router.get(
    "/{petition_id}/admin/timeline",
    dependencies=[Depends(has_permission(PermissionEnum.petition_update_review))],
)
async def get_petition_timeline_admin_view(
    ps: PetitionServiceDep,
    petition_id: int,
):
    """
    get the timeline of updates and reviews based if you are in the admin view or not
    """
    return await ps.get_petition_timeline(petition_id=petition_id, admin_view=True)


@router.get(
    "/{petition_id}/timeline",
)
async def get_petition_timeline_user_view(
    ps: PetitionServiceDep,
    petition_id: int,
):
    """
    get the timeline of updates and reviews based if you are in the admin view or not
    """
    return await ps.get_petition_timeline(petition_id=petition_id, admin_view=False)


########################################
# Petition Soft Delete (Admin only)
########################################


@router.post(
    "/{petition_id}/mark-for-deletion",
    dependencies=[Depends(has_permission(PermissionEnum.petition_delete_any))],
    status_code=200,
)
async def mark_petition_for_deletion_endpoint(
    ps: PetitionServiceDep,
    petition_id: int,
    request_data: PetitionDeletionMarkRequest,
    user: User = Depends(current_auth_user),
):
    """
    Mark a petition for deletion (soft delete).

    The petition will be hidden from public view and automatically
    deleted after 60 days.

    Parameters
    ----------
    ps : PetitionServiceDep
        Petition service dependency.
    petition_id : int
        ID of the petition to mark for deletion.
    request_data : PetitionDeletionMarkRequest
        Deletion request data (reason).
    user : User
        Current authenticated admin user.

    Returns
    -------
    PetitionDeletionSchema
        The deletion record.

    Raises
    ------
    PetitionNotFoundError
        If petition doesn't exist.
    DBError
        If deletion marking fails.
    """
    return await ps.mark_petition_for_deletion(
        petition_id=petition_id,
        marked_by=user.username,
        reason=request_data.reason,
    )


@router.delete(
    "/{petition_id}/cancel-deletion",
    dependencies=[Depends(has_permission(PermissionEnum.petition_delete_any))],
    status_code=204,
)
async def cancel_petition_deletion_endpoint(
    ps: PetitionServiceDep,
    petition_id: int,
) -> None:
    """
    Cancel a petition's scheduled deletion.

    Parameters
    ----------
    ps : PetitionServiceDep
        Petition service dependency.
    petition_id : int
        ID of the petition to unmark.

    Raises
    ------
    PetitionNotFoundError
        If petition or deletion mark doesn't exist.
    DBError
        If cancellation fails.
    """
    await ps.cancel_petition_deletion(petition_id)
