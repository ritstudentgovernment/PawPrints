from datetime import datetime
import enum
from typing import Literal

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field, field_validator

################################################

# General

################################################


class PageInfo(BaseModel):
    """Schema for pagination information.

    Attributes
    ----------
    page : int
        The current page number.
    items : int
        The number of items on the current page.
    total_items : int
        The total number of items across all pages.
    total_pages : int
        The total number of pages.

    """

    page: int
    items: int
    total_items: int
    total_pages: int


class StatusEnumAPI(enum.IntEnum):
    ACTIVE = 0
    CHARGED = 1
    RESPONDED = 2
    EXPIRED = 3


SortField = Literal["rank", "created_at", "total_signatures"]
IncludeField = Literal["committees", "updates", "response"]
TagMatch = Literal["any", "all"]
SortFieldCommon = Literal["created_at", "total_signatures"]
SortFieldSearch = Literal["rank", "created_at", "total_signatures"]


class Success(BaseModel):
    """Schema for a generic success response.

    Attributes
    ----------
    message : str
        A success message.
    status_code : int
        The HTTP status code.

    """

    message: str
    status_code: int


################################################

# User

################################################


class UserSchema(BaseModel):
    """Schema for user data.

    Attributes
    ----------
    username : str
        The user's unique username.
    first_name : str
        The user's first name.
    last_name : str
        The user's last name.
    roles : list[RoleSchema]
        A list of roles assigned to the user.
    rit_edu_account_type : str
        RIT account type from SAML (e.g. "Student", "Faculty").
    rit_edu_campus_u : str | None
        RIT campus (undergraduate) from SAML.
    rit_edu_campus_g : str | None
        RIT campus (graduate) from SAML.
    rit_edu_college_u : str | None
        RIT college (undergraduate) from SAML.
    rit_edu_college_g : str | None
        RIT college (graduate) from SAML.
    """

    username: str
    first_name: str
    last_name: str
    roles: list["RoleSchema"] = []
    rit_edu_account_type: str | None = ""
    rit_edu_campus_u: str | None = None
    rit_edu_campus_g: str | None = None
    rit_edu_college_u: str | None = None
    rit_edu_college_g: str | None = None

    model_config = ConfigDict(from_attributes=True)


class UpdateUserRoleRequest(BaseModel):
    role_id: int


################################################

# Committee

################################################


class CommitteeSchema(BaseModel):
    """Schema for a committee.

    Attributes
    ----------
    name : str
        The name of the committee.
    description : str
        A description of the committee's purpose.
    id : Optional[int]
        The unique identifier for the committee.

    """

    model_config = ConfigDict(from_attributes=True)

    name: str
    description: str
    id: int | None = None


class CommitteeMemberCreateRequest(BaseModel):
    """The data expected in the POST request body."""

    username: str


class CommitteeMemberResponse(BaseModel):
    """The data we will return after successfully creating the membership."""

    model_config = ConfigDict(from_attributes=True)

    user: UserSchema
    committee: CommitteeSchema


class ReturnCommittee(BaseModel):
    """Schema for a paginated list of committees.

    Attributes
    ----------
    page_info : PageInfo
        Pagination details.
    committees : list[CommitteeSchema]
        A list of committee objects.
    """

    page_info: PageInfo
    committees: list[CommitteeSchema]


################################################

# Response and Updates

################################################


class UpdateSchema(BaseModel):
    """Schema for a petition update or response."""

    id: int
    message: str | None = Field(
        ...,
        min_length=10,
        max_length=40000,
        description="Message provided for an update to a petition.",
    )
    created_at: datetime
    author_id: str | None
    approved_by: str | None
    is_draft: bool
    is_approved: bool

    model_config = ConfigDict(from_attributes=True)


class ReviewUpdateRequest(BaseModel):
    """Schema for approving a petition update or response.

    Attributes
    ----------
    update_id : int
        The ID of the update being approved.
    message: Optional[str]
        Optional message from the approver regarding the review.
    approve : bool
        Flag indicating whether the update is approved or rejected.
    """

    update_id: int = Field(
        ...,
        description="The ID of the update being approved.",
    )
    message: str | None = Field(
        None,
        description="Optional message from the approver regarding the review.",
    )
    approve: bool = Field(
        ...,
        description="Flag indicating whether the update is approved or rejected.",
    )


class ReviewUpdateResponse(BaseModel):
    """Schema for the response after reviewing a petition update or response.

    Attributes
    ----------
    update_id : int
        The ID of the update that was reviewed.
    is_approved: bool
        Flag indicating whether the update was approved or rejected.
    message : str
        A message providing additional context about the review outcome.
    """

    update_id: int = Field(
        ...,
        description="The ID of the update that was reviewed.",
    )
    reviewer_id: str = Field(
        ...,
        description="The ID of the user who reviewed the update.",
    )
    is_approved: bool = Field(
        ...,
        description="The status of the review, e.g., 'approved' or 'rejected'.",
    )
    message: str = Field(
        ...,
        min_length=10,
        max_length=40000,
        description="A message providing additional context about the review outcome.",
    )
    created_at: datetime = Field(
        ...,
        description="The timestamp when the review was created.",
    )

    model_config = ConfigDict(from_attributes=True)


class PetitionUpdateSchema(BaseModel):
    """
    Used when returning PetitionUpdates
    Each update can be displayed if and only if it's approved
    Each update can be marked as an official response

    Attributes:
    __________

    is_response: bool
        is the update an official response
    update: UpdateSchema:
        update object with all attributes
    review: List[ReviewUpdateResponse]
        any reviews attached to the update
    """

    is_response: bool
    update: UpdateSchema
    review: list[ReviewUpdateResponse] | None

    model_config = ConfigDict(from_attributes=True)


class UpdateTimelineResponse(BaseModel):
    petition_description: str | None
    petition_updates: list[PetitionUpdateSchema]


class CreateDraftUpdate(BaseModel):
    """Schema for a petition update or response.

    Attributes
    ----------
    is_draft: bool
        If the update is still a draft, not out for review
    is_response: bool
        If the update is an official response.
    original_draft_id : Optional[int]
        The ID of the original draft update if this is an edit.
    message : str
        The content of the update or response sent to approver.
    """

    is_draft: bool
    is_response: bool
    original_draft_id: int | None = Field(
        None, description="The ID of the original draft update if this is an edit."
    )

    message: str = Field(
        ...,
        min_length=10,
        max_length=40000,
        description="The content of the update or response set to approver.",
    )


# ---------------------------------------------------------------------
# Tag Schemas
# ---------------------------------------------------------------------


class TagBase(BaseModel):
    """Base schema for tag data."""

    name: str = Field(..., min_length=1, max_length=50, description="Tag name")
    description: str | None = Field(None, max_length=255, description="Tag description")
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$", description="Hex color code")

    model_config = ConfigDict(from_attributes=True)


class TagCreate(TagBase):
    """Schema for creating a new tag."""

    pass


class TagUpdate(BaseModel):
    """Schema for updating a tag."""

    name: str | None = Field(None, min_length=1, max_length=50)
    description: str | None = Field(None, max_length=255)
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")


class TagSchema(TagBase):
    """Schema for returning tag data."""

    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TagListResponse(BaseModel):
    """Schema for paginated list of tags."""

    page_info: PageInfo
    tags: list[TagSchema]


class PetitionTagAssign(BaseModel):
    """Schema for assigning a tag to a petition."""

    tag_ids: list[int] = Field(..., description="ID of the tag to assign")


class PetitionTagResponse(BaseModel):
    """Schema for petition tag assignment response."""

    petition_id: int
    tag: TagSchema
    assigned_at: datetime
    assigned_by: str | None

    model_config = ConfigDict(from_attributes=True)


################################################

# Petition


################################################
class PetitionFilterBase(BaseModel):
    # pagination (keep backward-compat with items_per_page)
    model_config = ConfigDict(populate_by_name=True)

    page: int = Field(1, ge=1)
    per_page: int = Field(10, ge=1, le=100, alias="items_per_page")

    # filters
    status: list[int] | None = Query(None, description="Repeatable: status=0&status=2")
    tag_id: list[int] | None = Query(None, description="Repeatable")
    tag_match: TagMatch = "any"
    has_response: bool | None = None
    is_draft: bool = False

    # ranges "min..max" (open ends allowed)
    signatures: str | None = Field(
        None, pattern=r"^\d*\.\.\d*$", description="Format: min..max (e.g., 100.. or ..200)"
    )
    created: str | None = Field(
        None,
        pattern=r"^\d{4}-\d{2}-\d{2}\.\.\d{4}-\d{2}-\d{2}$|^\d{4}-\d{2}-\d{2}\.\.$|^\.\.\d{4}-\d{2}-\d{2}$",
        description="YYYY-MM-DD..YYYY-MM-DD (open ends allowed)",
    )

    # includes & sorting
    include: list[IncludeField] | None = None
    sort: list[str] | None = None  # prefix with '-' for desc

    # derived (excluded in output)
    min_signatures: int | None = Field(default=None, exclude=True)
    max_signatures: int | None = Field(default=None, exclude=True)
    created_from: str | None = Field(default=None, exclude=True)
    created_to: str | None = Field(default=None, exclude=True)

    def finalize(self) -> "PetitionFilterBase":
        if self.signatures:
            left, right = self.signatures.split("..", 1)
            self.min_signatures = int(left) if left else None
            self.max_signatures = int(right) if right else None
        if self.created:
            left, right = self.created.split("..", 1)
            self.created_from = left or None
            self.created_to = right or None
        return self

    def __repr__(self) -> str:
        return (
            f"PetitionFilterBase(page={self.page}, per_page={self.per_page}, "
            f"status={self.status}, committee_id={self.tag_id}, "
            f"tag_match='{self.tag_match}', has_response={self.has_response}, "
            f"is_draft={self.is_draft}, signatures='{self.signatures}', created='{self.created}', "
            f"include={self.include}, sort={self.sort})"
        )


class PetitionFilterParams(PetitionFilterBase):
    """
    Filters only (no text search). Allowed sort keys: created_at, total_signatures.
    """

    @field_validator("sort")
    @classmethod
    def _strip_rank_for_filter(cls, v):
        if not v:
            return v
        allowed: set[str] = {"created_at", "-created_at", "total_signatures", "-total_signatures"}
        return [s for s in v if s in allowed]


class PetitionSearchParams(PetitionFilterBase):
    """
    Filters + optional query. Adds rank sort.
    """

    q: str | None = Field(default=None, alias="query")

    @field_validator("sort")
    @classmethod
    def _validate_sort_for_search(cls, v):
        # pass through; service will ignore rank if q is empty
        return v


class CreatePetition(BaseModel):
    """Schema for creating a new petition.

    Attributes
    ----------
    title : str
        The title of the petition.
    description : Optional[str]
        The detailed description or body of the petition.
    is_draft : Optional[bool]
        Flag indicating if the petition is a draft or in progress.

    """

    title: str
    description: str | None
    is_draft: bool | None
    tags: list[int] | None


class PetitionSignResponse(BaseModel):
    """Schema for petition sign response.
    Attributes
    __________
    success: bool
        if the signature was actually signed of not
    total_signatures: int
        the new count of signatures
    """

    signed: bool
    total_signatures: int


class MediaUploadResponse(BaseModel):
    url: str
    filename: str
    content_type: str


class PetitionSearchRequest(BaseModel):
    """Schema for advanced petition search query parameters.

    Attributes
    ----------
    query : Optional[str]
        The search term for the petition title or description.
    page : int
        The page number for pagination.
    items_per_page : int
        The number of items to return per page.
    status : Optional[int]
        Filter petitions by a specific status ID.
    committee_id : Optional[int]
        Filter petitions by a specific committee ID.
    min_signatures : Optional[int]
        Filter for petitions with at least this many signatures.
    max_signatures : Optional[int]
        Filter for petitions with at most this many signatures.
    has_response : Optional[bool]
        Filter for petitions that have or do not have an official response.
    """

    query: str | None = None
    page: int = 1
    items_per_page: int = 10
    status: int | None = None
    committee_id: int | None = None
    min_signatures: int | None = None
    max_signatures: int | None = None
    has_response: bool | None = None


class PetitionPageSchema(BaseModel):
    """Schema for a single petition on a page.

    Attributes
    ----------
    id : int
        The unique identifier for the petition.
    title : str
        The title of the petition.
    description : Optional[str]
        The detailed description of the petition.
    author : Optional[str]
        The author of the petition.
    total_signatures : Optional[int]
        The current number of signatures.
    created_at : Optional[datetime]
        The timestamp when the petition was created.
    status : Optional[int]
        The current status ID of the petition.
    expires : Optional[datetime]
        The timestamp when the petition signature collection expires.
    has_response : Optional[bool]
        Flag indicating if the petition has an official response.
    is_draft : Optional[bool]
        Flag indicating if the petition is a draft.
    committees : Optional[list[CommitteeSchema]]
        A list of committees associated with the petition.
    updates : Optional[list[Update]]
        A list of updates or responses for the petition.
    """

    id: int
    title: str
    author: UserSchema | None
    total_signatures: int | None = 0
    created_at: datetime | None
    status: int | None
    expires: datetime | None
    has_response: bool | None
    is_draft: bool | None
    tags: list[TagSchema] | None = Field(default_factory=list, validation_alias="petition_tags")
    committee: CommitteeSchema | None = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("tags", mode="before")
    @classmethod
    def extract_tags(cls, v):
        # v is a list of PetitionTag objects
        return [pt.tag for pt in v] if v else []

    @field_validator("committee", mode="before")
    @classmethod
    def extract_committee(cls, v):
        # v is a list of CommitteeAssignment objects
        if v and len(v) > 0:
            return v[0].committee
        return None


class PetitionDescriptionSchema(BaseModel):
    """
    Schema for a petition description, to save on
    response length when searching for petitions.
    """
    petition_description: str | None


class PetitionCreateResponse(BaseModel):
    """
    Schema returned when a petition is first created.
    Contains only the core, non-relational petition fields.
    """

    id: int
    title: str
    description: str | None
    author: UserSchema
    total_signatures: int | None = 0
    created_at: datetime | None
    status: int | None
    expires: datetime | None
    has_response: bool | None
    is_draft: bool | None
    response_id: int | None

    model_config = ConfigDict(from_attributes=True)


class ReturnPetition(BaseModel):
    """Schema for a paginated list of petitions.

    Attributes
    ----------
    page_info : PageInfo
        Pagination details.
    petitions : list[PetitionPageSchema]
        A list of petition objects.
    """

    page_info: PageInfo
    petitions: list[PetitionPageSchema]


class ReturnPetitionResponses(BaseModel):
    """Schema for returning petitions along with their updates.

    Attributes
    ----------
    page_info : PageInfo
        Pagination details.
    petitions : list[PetitionPageSchema]
        A list of petition objects.
    updates : list[UpdateSchema]
        A list of all updates for the returned petitions.
    """

    page_info: PageInfo
    petitions: list[PetitionPageSchema]
    updates: list[UpdateSchema]


class QueryPetition(BaseModel):
    """Schema for a basic petition query.

    Attributes
    ----------
    query : str
        The search term.
    page : Optional[int]
        The page number for pagination.
    items_per_page : Optional[int]
        The number of items to return per page.
    """

    query: str
    page: int | None = 1
    items_per_page: int | None = 10


class CommitteeAssignmentCreate(BaseModel):
    committee_id: int = Field(..., description="The committee ID to assign to the petition.")


################################################

# Filters

################################################


class FilterPetition(BaseModel):
    """Base schema for filtering with pagination.

    Attributes
    ----------
    page : Optional[int]
        The page number for pagination.
    items_per_page : Optional[int]
        The number of items to return per page.
    """

    page: int | None = 1
    items_per_page: int | None = 10


class ByCommittee(FilterPetition):
    """Schema for filtering petitions by committee.

    Attributes
    ----------
    committee : str
        The name of the committee to filter by.
    """

    committee: str


class ByStatus(FilterPetition):
    """Schema for filtering petitions by status.

    Attributes
    ----------
    status : int
        The status ID to filter by.
    """

    status: int


class ReturnAllStatus(BaseModel):
    """Schema for returning all possible petition statuses.

    Attributes
    ----------
    status : dict
        A dictionary mapping status names to their IDs.
    """

    status: dict


########################################
# Permissions
########################################

###############################################
# Permission Enums
###############################################


class PermissionEnum(enum.StrEnum):
    # --- Roles ---
    role_create = "role.create"
    role_update = "role.update"
    role_delete = "role.delete"
    role_list = "role.list"
    role_read = "role.read"

    # ---Permissions ---
    permission_list = "permission.list"
    permission_read = "permission.read"

    # Role ↔ Permission bindings
    role_permission_assign = "role.permission.assign"
    role_permission_remove = "role.permission.remove"

    # --- Users ---
    user_create = "user.create"
    user_update = "user.update"
    user_list = "user.list"
    user_read = "user.read"

    # User ↔ Role bindings
    user_role_assign = "user.role.assign"
    user_role_remove = "user.role.remove"

    # --- Committees ---
    committee_create = "committee.create"
    committee_update = "committee.update"
    committee_delete = "committee.delete"
    committee_list = "committee.list"
    committee_read = "committee.read"

    # Committee members (subresource)
    committee_member_add = "committee.member.add"
    committee_member_remove = "committee.member.remove"
    committee_member_list = "committee.member.list"  # list members of a committee
    committee_member_list_all = "committee.member.list.all"  # list membership across committees

    # --- Petitions ---
    petition_create = "petition.create"
    petition_update_any = "petition.update.any"
    petition_update_own = "petition.update.own"
    petition_delete_any = "petition.delete.any"
    petition_delete_own = "petition.delete.own"
    petition_list = "petition.list"
    petition_list_own = "petition.list.own"
    petition_read = "petition.read"

    # Petition signatures
    petition_sign = "petition.sign"
    petition_unsign = "petition.unsign"
    petition_signature_list_any = "petition.signature.list.any"  # view who signed (moderators)
    petition_signature_list_own = "petition.signature.list.own"  # author can see signers

    # Petition ↔ Committee assignments
    petition_committee_charge = "petition.committee.charge"
    petition_committee_unassign = "petition.committee.unassign"
    petition_read_assigned = (
        "petition.read.assigned"  # committee members can read assigned petitions
    )

    # Updates & Responses
    petition_update_create = "petition.update.create"
    petition_update_delete = "petition.update.delete"
    petition_update_review = "petition.update.review"
    petition_update_list = "petition.update.list"

    petition_response_create = "petition.response.create"
    petition_response_read = "petition.response.read"
    petition_response_update = "petition.response.update"
    petition_response_delete = "petition.response.delete"

    # --- Reports ---
    report_list = "report.list"
    report_read = "report.read"

    # Petition reports
    report_petition_create = "report.petition.create"
    report_petition_list = "report.petition.list"
    report_petition_delete = "report.petition.delete"

    # --- Tags ---
    tag_create = "tag.create"
    tag_update = "tag.update"
    tag_delete = "tag.delete"
    tag_list = "tag.list"
    tag_read = "tag.read"

    # Petition tags
    petition_tag_add = "petition.tag.add"
    petition_tag_remove = "petition.tag.remove"

    # --- Statistics ---
    stats_read = "stats.read"
    stats_refresh = "stats.refresh"


class PermissionSchema(BaseModel):
    """Schema for a permission.

    Attributes
    ----------
    id : Optional[int]
        The unique identifier for the permission.
    name : str
        The name of the permission.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int | None
    name: str


class ReturnPermissions(BaseModel):
    """Schema for a paginated list of permissions.

    Attributes
    ----------
    page_info : PageInfo
        Pagination details.
    permissions : list[PermissionSchema]
        A list of permission objects.
    """

    permissions: list["PermissionSchema"]  # Forward reference


class ReportCreate(BaseModel):
    """
    Schema for the request body when creating a new petition report.
    """

    reason: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="The detailed reason for filing the report against the petition.",
    )

    class Config:
        # an example for API documentation
        json_report_example = {
            "example": {"reason": "This petition contains spam links and inappropriate language."}
        }


########################################
# Roles
########################################


class RoleSchema(BaseModel):
    """Schema for a role.

    Attributes
    ----------
    id : Optional[int]
        The unique identifier for the role.
    name : str
        The name of the role.
    description : Optional[str]
        A description of the role's purpose.
    permissions : Optional[list[Permissions]]
        A list of permissions associated with the role.

    """

    id: int | None = None
    name: str
    description: str | None = None
    permissions: list[PermissionSchema] | None = None


class UpdateRolePermissionsRequest(BaseModel):
    permission_ids: list[int]


class DuplicateRoleRequest(BaseModel):
    """Schema for duplicating a role.

    Attributes
    ----------
    new_name : str
        The name for the duplicated role.
    """

    new_name: str


class RoleCreateRequest(BaseModel):
    """Schema for creating a new role.

    Attributes
    ----------
    name : str
        The name of the role.
    description : Optional[str]
        A description of the role's purpose.
    permissions : Optional[list[Permissions]]
        A list of permissions to associate with the role.
    """

    name: str
    description: str | None = None
    permissions: list[PermissionSchema] | None = None


class RoleUpdateRequest(BaseModel):
    """Schema for updating an existing role.

    Attributes
    ----------
    name : Optional[str]
        The new name of the role.
    description : Optional[str]
        A new description of the role's purpose.
    permissions : Optional[list[Permissions]]
        A new list of permissions to associate with the role.
    """

    name: str | None = None
    description: str | None = None
    permissions: list[PermissionSchema] | None = None


class DeleteRoleRequest(BaseModel):
    """Schema for deleting a role.

    Attributes
    ----------
    role_id : int
        The unique identifier of the role to delete.
    """

    role_id: int


class ReturnRolesResponse(BaseModel):
    """Schema for a paginated list of roles.

    Attributes
    ----------
    page_info : PageInfo
        Pagination details.
    roles : list[RoleSchema]
        A list of role objects.
    """

    roles: list["RoleSchema"]  # Forward reference


class ReturnUserProfile(BaseModel):
    """Schema for returning a user's profile information.

    Attributes
    ----------
    username : str
        The user's unique username.
    first_name : str
        The user's first name.
    last_name : str
        The user's last name.
    roles : list[str]
        A list of role names assigned to the user.
    committees : list[str]
        A list of committee names the user is a member of.
    rit_edu_account_type : str
        RIT account type from SAML (e.g. "Student", "Faculty").
    rit_edu_campus_u : str | None
        RIT campus (undergraduate) from SAML.
    rit_edu_campus_g : str | None
        RIT campus (graduate) from SAML.
    rit_edu_college_u : str | None
        RIT college (undergraduate) from SAML.
    rit_edu_college_g : str | None
        RIT college (graduate) from SAML.
    """

    username: str
    first_name: str
    last_name: str
    roles: list["RoleSchema"]  # Forward reference
    committees: list["CommitteeSchema"] | None  # Forward reference
    rit_edu_account_type: str | None = None
    rit_edu_campus_u: str | None = None
    rit_edu_campus_g: str | None = None
    rit_edu_college_u: str | None = None
    rit_edu_college_g: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ReturnUsers(BaseModel):
    """Schema for a paginated list of users.

    Attributes
    ----------
    page_info : PageInfo
        Pagination details.
    users : list[UserSchema]
        A list of user objects.
    """

    page_info: PageInfo
    users: list[UserSchema]


class ReturnImageURI(BaseModel):
    """Schema for returning an image URI."""

    uri: str


# ====================================================================
# Petition Deletion Schemas (Soft Delete)
# ====================================================================


class PetitionDeletionMarkRequest(BaseModel):
    """Schema for marking a petition for deletion.

    Attributes
    ----------
    reason : str | None
        Optional reason for marking the petition for deletion.
    """

    reason: str | None = Field(None, max_length=500, description="Reason for deletion")


class PetitionDeletionSchema(BaseModel):
    """Schema for returning petition deletion data.

    Attributes
    ----------
    id : int
        Deletion record ID.
    petition_id : int
        ID of the petition marked for deletion.
    marked_at : datetime
        When the petition was marked for deletion.
    marked_by : str | None
        Username of admin who marked it.
    deletion_scheduled_at : datetime
        When the petition will be automatically deleted.
    reason : str | None
        Reason for deletion.
    """

    id: int
    petition_id: int
    marked_at: datetime
    marked_by: str | None
    deletion_scheduled_at: datetime
    reason: str | None

    model_config = ConfigDict(from_attributes=True)


class PetitionDeletionListItem(PetitionDeletionSchema):
    """Schema for deletion list with petition details.

    Extends PetitionDeletionSchema with petition information.
    """

    petition_title: str
    days_until_deletion: int


########################################
# Statistics
########################################


class StatsOverview(BaseModel):
    """High-level headline numbers across the platform."""

    total_petitions: int
    active_petitions: int
    charged_petitions: int
    responded_petitions: int
    expired_petitions: int
    total_signatures: int
    total_users: int
    total_committees: int
    total_tags: int
    petitions_with_response_pct: float


class PetitionTimelinePoint(BaseModel):
    """A single bucket in the petition activity timeline."""

    period: str
    created: int
    responded: int
    expired: int
    charged: int
    signatures: int


class PetitionTimeline(BaseModel):
    """Petition activity grouped by time period."""

    granularity: str
    data: list[PetitionTimelinePoint]


class StatusBreakdown(BaseModel):
    """Petition count for a single status."""

    status: str
    count: int
    percentage: float


class StatusBreakdownResponse(BaseModel):
    """Petition counts broken down by lifecycle status."""

    total: int
    breakdown: list[StatusBreakdown]


class TagStats(BaseModel):
    """Petition count for a single tag."""

    tag_id: int
    tag_name: str
    color: str | None
    petition_count: int
    percentage: float


class TagBreakdownResponse(BaseModel):
    """Petition distribution across tags."""

    total_tagged_petitions: int
    breakdown: list[TagStats]


class ResponseTimeStats(BaseModel):
    """Response-time statistics for one committee (or overall)."""

    committee_id: int | None
    committee_name: str | None
    avg_days_to_response: float | None
    min_days: float | None
    max_days: float | None
    sample_size: int


class ResponseTimeResponse(BaseModel):
    """Platform-wide and per-committee response-time stats."""

    overall_avg_days: float | None
    by_committee: list[ResponseTimeStats]


class SignatureVelocityItem(BaseModel):
    """Signature velocity data for a single petition."""

    petition_id: int
    petition_title: str
    total_signatures: int
    first_signature_at: datetime | None
    latest_signature_at: datetime | None
    peak_daily_signatures: int | None
    peak_day: str | None  # ISO date string


class SignatureVelocityResponse(BaseModel):
    """Top petitions ranked by signature count with velocity metrics."""

    petitions: list[SignatureVelocityItem]


class UserGrowthPoint(BaseModel):
    """New and cumulative users for a single time bucket."""

    period: str
    new_users: int
    total_users: int


class UserGrowthResponse(BaseModel):
    """User registration growth over time."""

    granularity: str
    data: list[UserGrowthPoint]


class UserBreakdownByCollege(BaseModel):
    """User count for a single RIT college."""

    college: str | None
    user_count: int
    percentage: float


class UserBreakdownByAccountType(BaseModel):
    """User count for a single RIT account type."""

    account_type: str | None
    user_count: int
    percentage: float


class UserBreakdownResponse(BaseModel):
    """User distribution by college and account type."""

    total_users: int
    by_college: list[UserBreakdownByCollege]
    by_account_type: list[UserBreakdownByAccountType]


class CommitteePerformanceStats(BaseModel):
    """Response and throughput metrics for one committee."""

    committee_id: int
    committee_name: str
    petitions_assigned: int
    petitions_responded: int
    response_rate_pct: float
    avg_response_days: float | None
    pending_count: int


class CommitteePerformanceResponse(BaseModel):
    """Performance metrics for all committees."""

    committees: list[CommitteePerformanceStats]


class StatsRefreshResult(BaseModel):
    """Result of a stats refresh operation."""

    refreshed_tables: list[str]
    target_date: str


class ActivityHourSlot(BaseModel):
    """Request count for a single hour."""

    hour: int
    request_count: int
    unique_users: int
    login_count: int


class ActivityEndpointGroup(BaseModel):
    """Daily activity for one endpoint group."""

    endpoint_group: str
    method: str
    request_count: int
    unique_users: int
    login_count: int
    by_hour: list[ActivityHourSlot] = []


class ActivityDayResponse(BaseModel):
    """Full activity breakdown for a single day."""

    date: str
    total_requests: int
    total_unique_users: int
    total_logins: int
    by_endpoint: list[ActivityEndpointGroup]


class ActivityTrendPoint(BaseModel):
    """Activity totals for a single date in a trend series."""

    date: str
    total_requests: int
    total_unique_users: int
    total_logins: int


class ActivityTrendResponse(BaseModel):
    """Daily activity trend over a date range."""

    data: list[ActivityTrendPoint]
