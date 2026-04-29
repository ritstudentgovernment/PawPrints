from __future__ import annotations

from datetime import UTC, datetime, timedelta
import enum

import sqlalchemy as sa
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Computed,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    event,
    func,
)
from sqlalchemy.orm import DeclarativeBase, relationship, validates
from sqlalchemy_utils.types.ts_vector import TSVectorType

# ---------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


# ---------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------


# TODO: Add more statuses (THRESHOLD_REACHED, etc.) as needed
class StatusEnum(enum.IntEnum):
    """
    Petition lifecycle status.

    Attributes
    ----------
    ACTIVE : int
        Petition is open for signatures.
    CHARGED : int
        Petition has been assigned to a committee.
    RESPONDED : int
        Petition has a final response.
    EXPIRED : int
        Petition automatically closed after ~7 months.
    """

    ACTIVE = 0
    CHARGED = 1
    RESPONDED = 2
    EXPIRED = 3


# ---------------------------------------------------------------------
# RBAC: Roles & Permissions
# ---------------------------------------------------------------------


class Role(Base):
    """
    Application role (e.g., petitioner, official, admin).

    Columns
    -------
    id : int
        Primary key.
    name : str
        Unique role name.
    """

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(200), nullable=True)

    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name={self.name!r}, description={self.description!r})>"


class Permission(Base):
    """
    Permission primitive (e.g., view, create, delete, update).

    Columns
    -------
    id : int
        Primary key.
    name : str
        Unique permission name.
    """

    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)

    def __repr__(self) -> str:
        return f"<Permission(id={self.id}, name={self.name!r})>"


class RolePermission(Base):
    """
    Mapping of roles to permissions (many-to-many).

    Composite Primary Key
    ---------------------
    (role_id, permission_id)
    """

    __tablename__ = "role_permissions"

    role_id = Column(
        Integer,
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    permission_id = Column(
        Integer,
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )

    role = relationship("Role", lazy="joined")
    permission = relationship("Permission", lazy="joined")

    __table_args__ = (sa.PrimaryKeyConstraint("role_id", "permission_id"),)

    def __repr__(self) -> str:
        return f"<RolePermission(role_id={self.role_id}, permission_id={self.permission_id})>"


# ---------------------------------------------------------------------
# Petitions
# ---------------------------------------------------------------------


class Petition(Base):
    """
    A petition authored by a user and optionally processed by committees.

    Columns
    -------
    id : int
        Primary key (autoincrement).
    title : str
        Petition title (<= 80 chars).
    description : str
        Petition description (unbounded string).
    total_signatures : int
        Count of signatures (non-negative).
    created_at : datetime
        Creation timestamp (server default NOW()).
    status : StatusEnum
        Petition status (see :class:`StatusEnum`), defaults to ACTIVE.
    expires : datetime
        Expiration timestamp (auto-set ~7 months after creation).
    has_response : bool
        Whether a final response exists.
    is_draft : bool
        If True, petition is hidden from public lists/search.
    response_id : int | None
        FK to ``updates.id`` that represents the final response.

    Relationships
    -------------
    signatures : list[PetitionSignature]
        Signatures attached to this petition.
    reports : list[PetitionReport]
        Reports filed against this petition.
    committees : list[CommitteeAssignment]
        Committee assignments for this petition.
    response : Update | None
        The final response (if any).

    Notes
    -----
    - A computed ``search_tsv`` column (GIN-indexed) supports full-text search
      over title and description.
    """

    __tablename__ = "petitions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(80), index=True, nullable=False)
    description = Column(String, nullable=True)
    # updating default signatures to 1
    total_signatures = Column(Integer, nullable=False, default=1, server_default="0")
    created_at = Column(
        DateTime(timezone=True),
        index=True,
        nullable=False,
        server_default=func.now(),
    )
    status = Column(
        sa.Enum(StatusEnum, native_enum=False),  # store as int-text mapping portable across DBs
        default=StatusEnum.ACTIVE,
        nullable=False,
        server_default=str(StatusEnum.ACTIVE.value),
    )
    expires = Column(DateTime(timezone=True), nullable=True)
    has_response = Column(Boolean, default=False, nullable=False, server_default=sa.text("false"))
    is_draft = Column(Boolean, nullable=False, default=False, server_default=sa.text("false"))
    response_id = Column(Integer, ForeignKey("updates.id", ondelete="SET NULL"), nullable=True)

    author = relationship(
        "User",
        secondary="user_petitions",  # <--- The name of your connecting table
        back_populates="authored_petitions",
        lazy="joined",
        uselist=False,
    )

    # Relationships
    signatures = relationship(
        "PetitionSignature",
        back_populates="petition",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    reports = relationship(
        "PetitionReport",
        back_populates="petition",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    committees = relationship(
        "CommitteeAssignment",
        back_populates="petition",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    response = relationship("Update", foreign_keys=[response_id], lazy="joined")

    updates = relationship("PetitionUpdate", back_populates="petition")

    petition_tags = relationship(
        "PetitionTag",
        back_populates="petition",
        cascade="all, delete-orphan",  # If petition is deleted, delete the links
        passive_deletes=True,
    )

    deletion_mark = relationship(
        "PetitionDeletion",
        back_populates="petition",
        uselist=False,  # One-to-one relationship
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # Full-text search
    search_tsv = Column(
        TSVectorType(
            "title",
            "description",
            weights={"title": "A", "description": "B"},
            reconfig="english",
        ),
        Computed(
            "to_tsvector('english', coalesce(title,'')) || to_tsvector('english', coalesce(description,''))",
            persisted=True,
        ),
    )

    __table_args__ = (
        Index("ix_petitions_search_tsv", search_tsv, postgresql_using="gin"),
        CheckConstraint("total_signatures >= 0", name="ck_petitions_total_signatures_nonneg"),
    )

    @property
    def author_display_name(self) -> str:
        """Returns the author's username or a placeholder if deleted."""
        if self.author:
            return self.author.username
        return "[Deleted User]"

    # ---- Validators ----

    @validates("status")
    def _validate_status(self, key, value):
        if not isinstance(value, StatusEnum):
            # Allow int assignment by casting to StatusEnum
            if isinstance(value, int):
                value = StatusEnum(value)
            else:
                raise ValueError("Status must be a StatusEnum or int convertible to StatusEnum")
        return value

    @validates("has_response", "is_draft")
    def _validate_bools(self, key, value):
        if value is not None and not isinstance(value, bool):
            raise ValueError(f"{key} must be a boolean")
        return value

    def __repr__(self) -> str:
        return f"<Petition(id={self.id}, title={self.title!r}, status={self.status.name})>"


def set_expires_date(mapper, connection, target: Petition) -> None:
    """
    Set ``expires`` to ~7 months after ``created_at`` if not already set.

    Notes
    -----
    Uses 210 days (~7 months).
    """
    if target.expires is None and target.created_at is not None and not target.is_draft:
        # Ensure aware datetimes
        created = target.created_at
        if created.tzinfo is None:
            created = datetime.now(UTC)
        target.expires = created + timedelta(days=210)


def update_petition_status(mapper, connection, target: Petition) -> None:
    """
    Update ``status`` according to business rules.

    Rules
    -----
    - If manually set to CHARGED, keep CHARGED.
    - Else if ``has_response`` is True → RESPONDED.
    - Else if older than 210 days → EXPIRED.
    - Else → ACTIVE.
    """
    # Current moment in UTC (aware)
    if target.is_draft:
        return

    now = datetime.now(UTC)

    # Respect manual CHARGED status
    if target.status == StatusEnum.CHARGED:
        return

    # Normalize created_at to aware UTC
    created = target.created_at
    if created is None:
        created = now
    elif created.tzinfo is None:
        # If 'created' is naive, assume it's UTC and make it aware
        created = created.replace(tzinfo=UTC)

    if target.has_response:
        target.status = StatusEnum.RESPONDED
    elif (created + timedelta(days=210)) < now:
        target.status = StatusEnum.EXPIRED
    else:
        target.status = StatusEnum.ACTIVE


def before_petition_insert(mapper, connection, target: Petition) -> None:
    """listener to set initial petition state."""
    set_expires_date(mapper, connection, target)
    update_petition_status(mapper, connection, target)


event.listen(Petition, "before_insert", before_petition_insert)
event.listen(Petition, "before_update", update_petition_status)


# ---------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------


class Report(Base):
    """
    A report filed against a petition.

    Columns
    -------
    id : int
        Primary key.
    reported_at : datetime
        Timestamp the report was created.
    reported_for : str
        Reason/details for the report.
    """

    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    reported_at = Column(
        DateTime(timezone=True), index=True, nullable=False, server_default=func.now()
    )
    reported_for = Column(Text, nullable=False)

    def __repr__(self) -> str:
        return f"<Report(id={self.id}, reported_at={self.reported_at})>"


class PetitionReport(Base):
    """
    Association between petitions and reports, with the reporting user.

    Composite Primary Key
    ---------------------
    (petition_id, report_id)
    """

    __tablename__ = "petition_reports"

    petition_id = Column(
        Integer,
        ForeignKey("petitions.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    report_id = Column(
        Integer,
        ForeignKey("reports.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    reporter_id = Column(String, ForeignKey("users.username", ondelete="SET NULL"), nullable=True)

    report = relationship("Report", lazy="joined")
    petition = relationship("Petition", back_populates="reports")
    reporter = relationship("User", lazy="joined")

    __table_args__ = (sa.PrimaryKeyConstraint("petition_id", "report_id"),)

    def __repr__(self) -> str:
        return f"<PetitionReport(petition_id={self.petition_id}, report_id={self.report_id})>"


# ---------------------------------------------------------------------
# Committees
# ---------------------------------------------------------------------


class Committee(Base):
    """
    Committee that may be assigned to petitions.

    Columns
    -------
    id : int
        Primary key.
    name : str
        Unique committee name.
    description : str
        Committee description.
    """

    __tablename__ = "committees"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String, nullable=True, index=True)

    assignments = relationship(
        "CommitteeAssignment",
        back_populates="committee",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    members = relationship(
        "UserCommitteeAssociation", back_populates="committee", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Committee(id={self.id}, name={self.name!r})>"


class UserCommitteeAssociation(Base):
    """
    Association between Committee and Users within a specific Committee
    Essentially Committee Members Table
    Users can be added or removed to a certain committee

    Composite Primary Key
    ---------------------
    (username, committee_id)
    """

    __tablename__ = "user_committee_association"

    username = Column(
        String, ForeignKey("users.username", ondelete="CASCADE"), primary_key=True, nullable=False
    )
    committee_id = Column(Integer, ForeignKey("committees.id"), primary_key=True, nullable=False)

    user = relationship("User", back_populates="committee_memberships")
    committee = relationship("Committee", back_populates="members")


class CommitteeAssignment(Base):
    """
    Association between petitions and committees.

    Composite Primary Key
    ---------------------
    (petition_id, committee_id)
    """

    __tablename__ = "committee_assignments"

    petition_id = Column(
        Integer,
        ForeignKey("petitions.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    committee_id = Column(
        Integer,
        ForeignKey("committees.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    assigned_at = Column(
        DateTime(timezone=True), index=True, nullable=False, server_default=func.now()
    )

    petition = relationship("Petition", back_populates="committees")
    committee = relationship("Committee", back_populates="assignments")

    __table_args__ = (sa.PrimaryKeyConstraint("petition_id", "committee_id"),)

    def __repr__(self) -> str:
        return f"<CommitteeAssignment(petition_id={self.petition_id}, committee_id={self.committee_id})>"


@event.listens_for(CommitteeAssignment, "after_insert")
def change_petition_status_assign(mapper, connection, target: CommitteeAssignment):
    """Increment the total_signatures count on the parent petition."""
    petition_table = Petition.__table__
    connection.execute(
        petition_table.update()
        .where(
            petition_table.c.id == target.petition_id,
            petition_table.c.has_response,
            petition_table.c.status != StatusEnum.EXPIRED,
        )
        .values(status=StatusEnum.CHARGED)
    )


# ---------------------------------------------------------------------
# Signatures
# ---------------------------------------------------------------------


class PetitionSignature(Base):
    """
    Signature by a user on a petition.

    Composite Primary Key
    ---------------------
    (petition_id, user_id)
    """

    __tablename__ = "petition_signatures"

    petition_id = Column(
        Integer,
        ForeignKey("petitions.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    user_id = Column(
        String,
        ForeignKey("users.username", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    signed_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )

    petition = relationship("Petition", back_populates="signatures")
    user = relationship("User", back_populates="signatures")

    __table_args__ = (sa.PrimaryKeyConstraint("petition_id", "user_id"),)

    def __repr__(self) -> str:
        return f"<PetitionSignature(petition_id={self.petition_id}, user_id={self.user_id})>"


# ---------------------------------------------------------------------
# Updates & Petition Updates
# ---------------------------------------------------------------------


# TODO: think about a message history of drafts until an approved update is made
# TODO: change this to DraftUpdate and make a separate FinalUpdate class, can
#  have multiple drafts that can be sent to approver but only one final update.
#  The FinalUpdate will be linked to the petition as the response
class Update(Base):
    """
    An update posted by an official,  linked to a petition.
    This also holds the draft response created by a committee chair.


    Columns
    -------
    id : int
        Primary key.
    message : str
        Update message.
    created_at : datetime
        Timestamp the update was created.
    author_id : str | None
        FK to ``users.username`` of the author (nullable if user deleted).
    approved_by : str | None
        FK to ``users.username`` of the approver (nullable if user deleted).
    is_draft : bool
        If True, the update is a draft and not publicly visible.
    is_approved : bool
        If True, the update has been approved for public viewing.
    """

    __tablename__ = "updates"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=True), index=True, nullable=False, server_default=func.now()
    )

    # Two distinct FKs to users.username
    author_id = Column(String, ForeignKey("users.username", ondelete="SET NULL"), nullable=True)
    approved_by = Column(String, ForeignKey("users.username", ondelete="SET NULL"), nullable=True)

    is_draft = Column(Boolean, nullable=False, default=True, server_default=sa.text("true"))
    is_approved = Column(Boolean, nullable=False, default=False, server_default=sa.text("false"))
    submission_thread_id = Column(Integer, ForeignKey("updates.id"), nullable=True)

    # author of update
    author = relationship(
        "User",
        back_populates="updates",
        foreign_keys=[author_id],  # <— tells SQLAlchemy which FK to use
    )

    # Staff/President/Admin who approved the update
    approver = relationship(
        "User",
        back_populates="approved_updates",
        foreign_keys=[approved_by],  # <— the other FK
    )

    petition_associations = relationship("PetitionUpdate", back_populates="update")

    reviews = relationship("Review", back_populates="update", cascade="all, delete-orphan")

    # This relationship can find the original draft in a thread
    original_draft = relationship("Update", remote_side=[id])

    def __repr__(self) -> str:
        return f"<Update(id={self.id}, author_id={self.author_id!r})>"


class PetitionUpdate(Base):
    """
    Association between petitions and updates.

    Composite Primary Key
    ---------------------
    (petition_id, update_id)
    """

    __tablename__ = "petition_updates"

    petition_id = Column(
        Integer,
        ForeignKey("petitions.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    update_id = Column(
        Integer,
        ForeignKey("updates.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    is_response = Column(Boolean, default=False, nullable=False, server_default=sa.text("false"))

    petition = relationship("Petition", back_populates="updates")
    update = relationship("Update", back_populates="petition_associations")

    __table_args__ = (sa.PrimaryKeyConstraint("petition_id", "update_id"),)

    def __repr__(self) -> str:
        return f"<PetitionUpdate(petition_id={self.petition_id}, update_id={self.update_id}, is_response={self.is_response})>"


class Review(Base):
    """
    A review of an update by a user with authority to approve/reject it.
    """

    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True)

    # The update that was reviewed
    update_id = Column(Integer, ForeignKey("updates.id"), nullable=False)

    reviewer_id = Column(String, ForeignKey("users.username"), nullable=False)

    is_approved = Column(Boolean, nullable=False)
    message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    update = relationship("Update", back_populates="reviews")
    reviewer = relationship("User", back_populates="reviews")


# ---------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------


class User(Base):
    """
    A user of the system.
    Columns
    -------
    username : str
        Unique username
    first_name : str
        User's first name.
    last_name : str
        User's last name.
    email : str
        User's email address.
    rit_edu_account_type : str
        RIT edu account type (e.g., "Student", "Faculty", "Staff"). Required.
    rit_edu_campus_u : str | None
        RIT edu campus (undergraduate).
    rit_edu_campus_g : str | None
        RIT edu campus (graduate).
    rit_edu_college_u : str | None
        RIT edu college (undergraduate).
    rit_edu_college_g : str | None
        RIT edu college (graduate).
    """

    __tablename__ = "users"

    username = Column(String, primary_key=True, unique=True, index=True, nullable=False)
    first_name = Column(String(50), index=True, nullable=False)
    last_name = Column(String(50), index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        index=True,
        nullable=False,
        server_default=func.now(),
    )

    rit_edu_account_type = Column(String, nullable=True)  # urn:oid:1.3.6.1.4.1.4447.1.59
    rit_edu_campus_u = Column(String, nullable=True)  # urn:oid:1.3.6.1.4.1.4447.1.122
    rit_edu_campus_g = Column(String, nullable=True)  # urn:oid:1.3.6.1.4.1.4447.1.123
    rit_edu_college_u = Column(String, nullable=True)  # urn:oid:1.3.6.1.4.1.4447.1.112
    rit_edu_college_g = Column(String, nullable=True)  # urn:oid:1.3.6.1.4.1.4447.1.115

    authored_petitions = relationship(
        "Petition",
        secondary="user_petitions",  # <--- The name of your connecting table
        back_populates="author",
        lazy="joined",  # Async-friendly loading
    )

    signatures = relationship(
        "PetitionSignature",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # Updates this user authored
    updates = relationship(
        "Update",
        back_populates="author",
        cascade="all, delete-orphan",
        passive_deletes=True,
        foreign_keys=lambda: [Update.author_id],  # <— disambiguate
    )

    # Updates this user approved (separate relationship; no delete-orphan)
    approved_updates = relationship(
        "Update",
        back_populates="approver",
        foreign_keys=lambda: [Update.approved_by],  # <— disambiguate
        viewonly=True,  # optional: keeps this side read-only to avoid confusion
    )
    committee_memberships = relationship(
        "UserCommitteeAssociation",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    reviews = relationship("Review", back_populates="reviewer", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(username={self.username!r}, first_name={self.first_name!r})>"


class UserPetition(Base):
    """
    Association of a user (author) to a petition.

    Composite Primary Key
    ---------------------
    (author_id, petition_id)
    """

    __tablename__ = "user_petitions"

    author_id = Column(
        String,
        ForeignKey("users.username", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    petition_id = Column(
        Integer,
        ForeignKey("petitions.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )

    __table_args__ = (sa.PrimaryKeyConstraint("author_id", "petition_id"),)

    def __repr__(self) -> str:
        return f"<UserPetition(author_id={self.author_id}, petition_id={self.petition_id})>"


class UserRole(Base):
    """
    Association of a user to a role.

    Composite Primary Key
    ---------------------
    (username, role_id)
    """

    __tablename__ = "user_roles"

    username = Column(
        String,
        ForeignKey("users.username", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    role_id = Column(
        Integer,
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )

    user = relationship("User", lazy="joined")
    role = relationship("Role", lazy="joined")

    __table_args__ = (sa.PrimaryKeyConstraint("username", "role_id"),)

    def __repr__(self) -> str:
        return f"<UserRole(username={self.username}, role_id={self.role_id})>"


# ---------------------------------------------------------------------
# Tag Models
# ---------------------------------------------------------------------


class Tag(Base):
    """
    Tag that can be assigned to petitions.

    Columns
    -------
    id : int
        Primary key (autoincrement).
    name : str
        Unique tag name (e.g., "Academics", "Campus Life").
    description : str | None
        Optional description of what this tag represents.
    color : str | None
        Optional color code for UI display (e.g., "#FF5733").
    created_at : datetime
        Creation timestamp.

    Relationships
    -------------
    petition_tags : list[PetitionTag]
        Petitions that have this tag.
    """

    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    color = Column(String(7), nullable=True)  # Hex color code
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    petition_tags = relationship(
        "PetitionTag",
        back_populates="tag",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<Tag(id={self.id}, name={self.name})>"


class PetitionTag(Base):
    __tablename__ = "petition_tags"

    petition_id = Column(
        Integer,
        ForeignKey("petitions.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    tag_id = Column(
        Integer,
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        index=True,
    )

    # Metadata columns
    assigned_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    assigned_by = Column(String, ForeignKey("users.username", ondelete="SET NULL"), nullable=True)

    # Relationships
    petition = relationship("Petition", back_populates="petition_tags")
    tag = relationship("Tag", back_populates="petition_tags", lazy="joined")
    assigner = relationship("User")

    __table_args__ = (
        # --- CHANGE 4: Ensure Composite Primary Key ---
        sa.PrimaryKeyConstraint("petition_id", "tag_id"),
        # Index created by index=True on tag_id column (line 934)
    )

    def __repr__(self) -> str:
        return f"<PetitionTag(petition_id={self.petition_id}, tag_id={self.tag_id})>"


class PetitionDeletion(Base):
    """
    Tracks petitions marked for deletion (soft delete).

    Petitions marked for deletion are hidden from public view
    and automatically deleted after the scheduled date (60 days).

    Columns
    -------
    id : int
        Primary key.
    petition_id : int
        FK to petition being marked for deletion (unique).
    marked_at : datetime
        When the petition was marked for deletion.
    marked_by : str | None
        Username of admin who marked it (nullable if user deleted).
    deletion_scheduled_at : datetime
        When the petition should be automatically deleted.
    reason : str | None
        Optional reason for deletion.

    Relationships
    -------------
    petition : Petition
        The petition being marked for deletion.
    admin : User
        The admin who marked it for deletion.
    """

    __tablename__ = "petition_deletions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    petition_id = Column(
        Integer,
        ForeignKey("petitions.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    marked_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    marked_by = Column(
        String,
        ForeignKey("users.username", ondelete="SET NULL"),
        nullable=True,
    )
    deletion_scheduled_at = Column(
        DateTime(timezone=True),
        nullable=False,
    )
    reason = Column(Text, nullable=True)

    # Relationships
    petition = relationship("Petition", back_populates="deletion_mark")
    admin = relationship("User", foreign_keys=[marked_by])

    def __repr__(self) -> str:
        return f"<PetitionDeletion(petition_id={self.petition_id}, scheduled={self.deletion_scheduled_at})>"


# ---------------------------------------------------------------------
# Statistics tables  (stats_*)
# ---------------------------------------------------------------------


class StatsPetitionDaily(Base):
    """
    Pre-aggregated daily petition and signature activity.

    Populated by the stats refresh job; one row per calendar date.

    Columns
    -------
    date : date
        The calendar date this row covers (primary key).
    petitions_created : int
        Non-draft petitions whose ``created_at`` falls on this date.
    petitions_expired : int
        Petitions whose ``expires`` date is this date.
    petitions_responded : int
        Petitions that transitioned to RESPONDED status on this date.
    petitions_charged : int
        Petitions assigned to a committee on this date.
    signatures_cast : int
        Total signature events (``petition_signatures.signed_at``) on this date.
    unique_signers : int
        Distinct users who signed on this date.
    reports_filed : int
        Reports created on this date.
    updated_at : datetime
        When this row was last refreshed.
    """

    __tablename__ = "stats_petition_daily"

    date = Column(sa.Date, primary_key=True, nullable=False)
    petitions_created = Column(Integer, nullable=False, default=0, server_default="0")
    petitions_expired = Column(Integer, nullable=False, default=0, server_default="0")
    petitions_responded = Column(Integer, nullable=False, default=0, server_default="0")
    petitions_charged = Column(Integer, nullable=False, default=0, server_default="0")
    signatures_cast = Column(Integer, nullable=False, default=0, server_default="0")
    unique_signers = Column(Integer, nullable=False, default=0, server_default="0")
    reports_filed = Column(Integer, nullable=False, default=0, server_default="0")
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    def __repr__(self) -> str:
        return f"<StatsPetitionDaily(date={self.date}, created={self.petitions_created})>"


class StatsUserSnapshot(Base):
    """
    Point-in-time snapshot of user counts, segmented by RIT account type.

    One row per calendar day (unique on snapshot_date).

    Columns
    -------
    id : int
        Surrogate primary key.
    snapshot_date : date
        Calendar date of the snapshot (unique – one row per day).
    snapshot_at : datetime
        Exact timestamp when the snapshot was taken.
    total_users : int
        Total registered users at snapshot time.
    new_users : int
        Users whose ``created_at`` is today.
    account_type_student : int
        Users with ``rit_edu_account_type = 'student'``.
    account_type_faculty : int
        Users with ``rit_edu_account_type = 'faculty'``.
    account_type_staff : int
        Users with ``rit_edu_account_type = 'staff'``.
    account_type_other : int
        All remaining account types (including NULL).
    """

    __tablename__ = "stats_user_snapshot"

    id = Column(Integer, primary_key=True, autoincrement=True)
    snapshot_date = Column(sa.Date, nullable=False, unique=True)
    snapshot_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    total_users = Column(Integer, nullable=False, default=0, server_default="0")
    new_users = Column(Integer, nullable=False, default=0, server_default="0")
    account_type_student = Column(Integer, nullable=False, default=0, server_default="0")
    account_type_faculty = Column(Integer, nullable=False, default=0, server_default="0")
    account_type_staff = Column(Integer, nullable=False, default=0, server_default="0")
    account_type_other = Column(Integer, nullable=False, default=0, server_default="0")

    __table_args__ = (sa.UniqueConstraint("snapshot_date", name="uq_stats_user_snapshot_date"),)

    def __repr__(self) -> str:
        return f"<StatsUserSnapshot(snapshot_date={self.snapshot_date}, total={self.total_users})>"


class StatsPetitionSignatureVelocity(Base):
    """
    Per-petition signature velocity metrics.

    One row per petition, updated on refresh.

    Columns
    -------
    petition_id : int
        FK to petitions (primary key).
    first_signature_at : datetime | None
        Timestamp of the very first signature.
    latest_signature_at : datetime | None
        Timestamp of the most recent signature.
    peak_daily_signatures : int
        Highest number of signatures received on any single day.
    peak_day : date | None
        The date on which ``peak_daily_signatures`` was reached.
    total_signatures_snapshot : int
        Total signature count at last refresh (cross-check with petitions.total_signatures).
    updated_at : datetime
        When this row was last refreshed.
    """

    __tablename__ = "stats_petition_signature_velocity"

    petition_id = Column(
        Integer,
        ForeignKey("petitions.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    first_signature_at = Column(DateTime(timezone=True), nullable=True)
    latest_signature_at = Column(DateTime(timezone=True), nullable=True)
    peak_daily_signatures = Column(Integer, nullable=False, default=0, server_default="0")
    peak_day = Column(sa.Date, nullable=True)
    total_signatures_snapshot = Column(Integer, nullable=False, default=0, server_default="0")
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    petition = relationship("Petition", lazy="joined")

    def __repr__(self) -> str:
        return f"<StatsPetitionSignatureVelocity(petition_id={self.petition_id}, peak={self.peak_daily_signatures})>"


class StatsCommitteePerformance(Base):
    """
    Periodic committee response-time snapshots.

    Each row covers one committee over one date range.

    Columns
    -------
    id : int
        Surrogate primary key.
    committee_id : int
        FK to committees.
    period_start : date
        Start of the reporting period.
    period_end : date
        End of the reporting period.
    petitions_assigned : int
        Petitions assigned to the committee during this period.
    petitions_responded : int
        Of those, how many received a final response.
    avg_response_days : Decimal | None
        Average calendar days from petition creation to final response.
    pending_count : int
        Petitions still active / without a response at period_end.
    updated_at : datetime
        When this row was last refreshed.
    """

    __tablename__ = "stats_committee_performance"

    id = Column(Integer, primary_key=True, autoincrement=True)
    committee_id = Column(
        Integer,
        ForeignKey("committees.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    period_start = Column(sa.Date, nullable=False)
    period_end = Column(sa.Date, nullable=False)
    petitions_assigned = Column(Integer, nullable=False, default=0, server_default="0")
    petitions_responded = Column(Integer, nullable=False, default=0, server_default="0")
    avg_response_days = Column(sa.Numeric(10, 2), nullable=True)
    pending_count = Column(Integer, nullable=False, default=0, server_default="0")
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    committee = relationship("Committee", lazy="joined")

    __table_args__ = (
        sa.UniqueConstraint(
            "committee_id", "period_start", "period_end", name="uq_committee_perf_period"
        ),
    )

    def __repr__(self) -> str:
        return f"<StatsCommitteePerformance(committee_id={self.committee_id}, period={self.period_start}..{self.period_end})>"


class StatsTagUsage(Base):
    """
    Daily cumulative tag→petition counts.

    Each row represents how many non-draft petitions carried a given tag
    up to and including ``date``.

    Columns
    -------
    tag_id : int
        FK to tags (part of composite PK).
    date : date
        The date this snapshot covers (part of composite PK).
    petition_count : int
        Cumulative petition count with this tag as of ``date``.
    """

    __tablename__ = "stats_tag_usage"

    tag_id = Column(
        Integer,
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    date = Column(sa.Date, primary_key=True, nullable=False)
    petition_count = Column(Integer, nullable=False, default=0, server_default="0")

    tag = relationship("Tag", lazy="joined")

    __table_args__ = (sa.PrimaryKeyConstraint("tag_id", "date"),)

    def __repr__(self) -> str:
        return (
            f"<StatsTagUsage(tag_id={self.tag_id}, date={self.date}, count={self.petition_count})>"
        )


class StatsActivityLog(Base):
    """
    Per-day / per-hour API activity: request counts and login events.

    Populated by the activity-tracking middleware on every request.
    One row per (date, hour, endpoint_group, method).

    Columns
    -------
    id : int
        Surrogate primary key.
    date : date
        Calendar date of the activity bucket (indexed).
    hour : int | None
        Hour of day (0–23). NULL for daily rollup rows.
    endpoint_group : str
        Coarse route group, e.g. ``petitions``, ``users``, ``auth``.
    method : str
        HTTP method (GET, POST, PUT, DELETE, …).
    request_count : int
        Number of requests in this bucket.
    unique_users : int
        Distinct authenticated users in this bucket.
    login_count : int
        Number of successful SAML login events in this bucket.
    updated_at : datetime
        When this row was last written.
    """

    __tablename__ = "stats_activity_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(sa.Date, nullable=False, index=True)
    hour = Column(Integer, nullable=True)
    endpoint_group = Column(String(100), nullable=False)
    method = Column(String(10), nullable=False, server_default="GET")
    request_count = Column(Integer, nullable=False, default=0, server_default="0")
    unique_users = Column(Integer, nullable=False, default=0, server_default="0")
    login_count = Column(Integer, nullable=False, default=0, server_default="0")
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        sa.UniqueConstraint(
            "date",
            "hour",
            "endpoint_group",
            "method",
            name="uq_activity_log_slot",
        ),
        Index("ix_stats_activity_log_date_endpoint", "date", "endpoint_group"),
    )

    def __repr__(self) -> str:
        return f"<StatsActivityLog(date={self.date}, hour={self.hour}, endpoint={self.endpoint_group})>"


# ---------------------------------------------------------------------
# Site Settings (singleton row, id=1)
# ---------------------------------------------------------------------


class SiteSettings(Base):
    """
    Singleton settings row for site-wide configuration.

    Only one row with id=1 is expected to exist.
    """

    __tablename__ = "site_settings"

    id = Column(Integer, primary_key=True, default=1)
    alert_enabled = Column(Boolean, nullable=False, default=False, server_default=sa.text("false"))
    alert_message = Column(Text, nullable=False, default="", server_default="''")
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    def __repr__(self) -> str:
        return f"<SiteSettings(alert_enabled={self.alert_enabled})>"
