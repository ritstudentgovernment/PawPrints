from __future__ import annotations

from datetime import UTC, datetime, timedelta
import hashlib
import logging
import math
from typing import Annotated, Any
import uuid

from botocore.client import BaseClient
from fastapi import Depends, UploadFile
from sqlalchemy import and_, delete, distinct, exists, func, literal, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, noload, selectinload
from starlette.concurrency import run_in_threadpool

from config import Config
from pawprints.api.service.auth_service import AuthService
from pawprints.database.media import get_s3_client
from pawprints.database.session import get_async_db_session
from pawprints.exceptions import (
    CommitteeNotFoundError,  # 5001 / 404
    DBError,  # 1000 / 500
    PermissionDeniedError,  # 2001 / 403
    PetitionNotFoundError,  # 4000 / 404
)
from pawprints.exceptions.petitions import (
    PetitionUpdateNotFoundError,
    PetitionUpdateSubmittedAlreadyError,
)
from pawprints.logger import get_logger
from pawprints.models.orm import (
    Committee,
    CommitteeAssignment,
    Petition,
    PetitionReport,
    PetitionTag,
    PetitionUpdate,
    Report,
    Review,
    StatusEnum,
    Tag,
    Update,
    User,
    UserPetition,
)
from pawprints.models.schema import (
    CreatePetition,
    PageInfo,
    PetitionCreateResponse,
    PetitionPageSchema,
    PetitionUpdateSchema,
    ReportCreate,
    ReturnPetition,
    ReviewUpdateRequest,
    ReviewUpdateResponse,
    UpdateSchema,
    UpdateTimelineResponse, PetitionDescriptionSchema,
)


class PetitionService:
    def __init__(self, session: AsyncSession, s3_client: BaseClient, logger: logging.Logger):
        self.session = session
        self.s3_client = s3_client
        self.logger = logger

    async def list_filtered(self, *, p) -> ReturnPetition:
        """Filters only (used by GET /api/v1/petitions)."""
        return await self._run_query(p=p, allow_text=False)

    async def search(self, *, p) -> ReturnPetition:
        """Text search + filters (used by GET /api/v1/petitions/search)."""
        return await self._run_query(p=p, allow_text=True)

    def _finalize_params(self, p, *, allow_text: bool):
        """Normalize/derive fields from query params."""
        p = p.finalize()
        qtext = getattr(p, "q", None)
        return p, (qtext if (allow_text and qtext) else None)

    def _base_filters(self, p) -> list:
        """Filters that don't depend on committees/search/sort."""
        self.logger.debug("Petition Status Filter Applied: %s", p)
        filters = [Petition.is_draft.is_(p.is_draft if p.is_draft else False)]

        if p.status:
            filters.append(Petition.status.in_([StatusEnum(s) for s in p.status]))
            self.logger.debug("Petition Status Filter Applied: %s", p.status)
        if p.has_response is not None:
            filters.append(Petition.has_response == p.has_response)
        if p.min_signatures is not None:
            filters.append(Petition.total_signatures >= p.min_signatures)
        if p.max_signatures is not None:
            filters.append(Petition.total_signatures <= p.max_signatures)

        # Dates come in as YYYY-MM-DD (string) → compare using datetimes
        if p.created_from:
            filters.append(Petition.created_at >= datetime.fromisoformat(p.created_from))
        if p.created_to:
            filters.append(Petition.created_at <= datetime.fromisoformat(p.created_to))

        return filters

    def _tag_filters(self, p) -> list:
        """Build EXISTS/ALL tag filters."""
        # Return empty if no tags are provided to filter by
        if not p.tag_id:
            return []

        # "any" — requires the petition to have AT LEAST ONE of the listed tags
        if p.tag_match == "any":
            return [
                exists(
                    select(1).where(
                        PetitionTag.petition_id == Petition.id,
                        PetitionTag.tag_id.in_(p.tag_id),
                    )
                )
            ]

        # "all" — requires the petition to have ALL of the listed tags
        have_all = (
            select(func.count(distinct(PetitionTag.tag_id)))
            .where(
                PetitionTag.petition_id == Petition.id,
                PetitionTag.tag_id.in_(p.tag_id),
            )
            .correlate(Petition)
            .scalar_subquery()
        )

        return [have_all == len(p.tag_id)]

    def _search_and_sort(self, *, qtext: str | None, p) -> tuple[list, Any, list]:
        """
        Return (extra_filters, rank_expr, order_exprs)

        - Adds FTS filter when qtext present
        - Applies requested sorting; ignores 'rank' if qtext is None
        - Provides default ordering when none specified
        - For search queries with no explicit sort, ranks by relevance first,
          then created_at; explicit sort parameters override this default
        """
        extra_filters: list = []
        rank_expr = literal(0)
        order_exprs: list = []

        if qtext:
            tsquery = func.websearch_to_tsquery("english", qtext)
            extra_filters.append(Petition.search_tsv.op("@@")(tsquery))
            rank_expr = func.ts_rank_cd(Petition.search_tsv, tsquery)
            order_exprs.append(rank_expr.desc().nulls_last())
            order_exprs.append(Petition.created_at.desc().nulls_last())

        sortable = {
            "rank": rank_expr,
            "created_at": Petition.created_at,
            "total_signatures": Petition.total_signatures,
        }

        if p.sort:
            order_exprs = []
            for s in p.sort:
                desc = s.startswith("-")
                key = s[1:] if desc else s
                if key not in sortable:
                    continue
                if key == "rank" and not qtext:
                    # ignore rank when no text query
                    continue
                col = sortable[key]
                order_exprs.append(col.desc().nulls_last() if desc else col.asc().nulls_last())
            if "created_at" not in [s.lstrip("-") for s in p.sort]:
                order_exprs.append(Petition.created_at.desc().nulls_last())

        if not order_exprs:
            order_exprs = [Petition.created_at.desc()]

        return extra_filters, rank_expr, order_exprs

    def _loader_options(self, p) -> list:
        """Relationship loading to avoid lazy IO (MissingGreenlet)."""
        load_opts = [
            noload("*"),
            selectinload(Petition.author),
            selectinload(Petition.petition_tags).selectinload(PetitionTag.tag),
        ]
        if p.include:
            if "petition_tags" in p.include:
                load_opts.append(selectinload(Petition.petition_tags).selectinload(PetitionTag.tag))
            if "response" in p.include:
                load_opts.append(selectinload(Petition.response))
            if "updates" in p.include:
                load_opts.append(selectinload(Petition.updates).selectinload(PetitionUpdate.update))
        return load_opts

    def _build_statements(self, *, filters: list, order_exprs: list, p, load_opts: list):
        """Construct main SELECT and COUNT statements (no I/O)."""
        stmt = (
            select(Petition)
            .where(and_(*filters))
            .order_by(*order_exprs)
            .limit(p.per_page)
            .offset((p.page - 1) * p.per_page)
            .options(*load_opts)
        )
        count_stmt = select(func.count()).select_from(
            select(Petition.id).where(and_(*filters)).subquery()
        )
        return stmt, count_stmt

    async def _execute_and_serialize(self, *, stmt, count_stmt, p) -> ReturnPetition:
        """Run queries, map to schemas, build PageInfo."""
        result = await self.session.execute(stmt)
        rows = result.scalars().unique().all()

        total_result = await self.session.execute(count_stmt)
        total_items = int(total_result.scalar() or 0)

        if not rows:
            raise PetitionNotFoundError(message="No petitions found for the given criteria.")

        petitions = [PetitionPageSchema.model_validate(r, from_attributes=True) for r in rows]
        page_info = PageInfo(
            page=p.page,
            items=len(petitions),
            total_items=total_items,
            total_pages=(total_items + p.per_page - 1) // p.per_page,
        )
        return ReturnPetition(page_info=page_info, petitions=petitions)

    # -------------------------------------------------------------------------
    # REFACTORED: orchestrator that uses the helpers above
    # -------------------------------------------------------------------------
    async def _run_query(self, *, p, allow_text: bool) -> ReturnPetition:
        # 1) finalize & prep query text
        p, qtext = self._finalize_params(p, allow_text=allow_text)

        # 2) filters
        filters = []
        filters += self._base_filters(p)
        filters += self._tag_filters(p)

        # 3) search + sort
        extra_filters, _rank_expr, order_exprs = self._search_and_sort(qtext=qtext, p=p)
        filters += extra_filters

        # 4) loading options
        load_opts = self._loader_options(p)

        # 5) statements
        stmt, count_stmt = self._build_statements(
            filters=filters, order_exprs=order_exprs, p=p, load_opts=load_opts
        )

        # 6) execute & serialize
        return await self._execute_and_serialize(stmt=stmt, count_stmt=count_stmt, p=p)

    async def get_latest_petitions(
        self, *, page: int = 1, items_per_page: int = 10
    ) -> ReturnPetition:
        """
        Fetch the latest petitions with pagination.

        Parameters
        ----------
        page : int, optional
            Current page index (1-based), by default 1.
        items_per_page : int, optional
            Number of petitions to return per page, by default 10.

        Returns
        -------
        ReturnPetition
            Collection of petition records alongside pagination metadata.
        """
        base_stmt = select(Petition).where(Petition.is_draft.is_(False))

        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total_items_result = await self.session.execute(count_stmt)
        total_items = total_items_result.scalar_one()

        total_pages = math.ceil(total_items / items_per_page) if total_items > 0 else 1

        start_idx = (page - 1) * items_per_page
        paginated_stmt = (
            base_stmt.order_by(Petition.created_at.desc())
            .offset(start_idx)
            .limit(items_per_page)
            .options(
                joinedload(Petition.author),
                selectinload(Petition.petition_tags).selectinload(PetitionTag.tag),
            )
        )
        petitions_result = await self.session.execute(paginated_stmt)
        petitions = petitions_result.scalars().all()

        petitions_for_response = [PetitionPageSchema.model_validate(p) for p in petitions]

        return ReturnPetition(
            page_info=PageInfo(
                page=page,
                items=items_per_page,
                total_items=total_items,
                total_pages=total_pages,
            ),
            petitions=petitions_for_response,
        )

    async def get_petition_by_id(self, *, petition_id: int) -> PetitionPageSchema:
        """
        Fetch a petition by its ID.

        Parameters
        ----------
        petition_id : int
            Identifier of the petition to retrieve.

        Returns
        -------
        PetitionPageSchema
            The petition data.

        Raises
        ------
        PetitionNotFoundError
            Raised when the petition cannot be located.
        """
        stmt = (
            select(Petition)
            .where(Petition.id == petition_id)
            .options(
                selectinload(Petition.author),
                selectinload(Petition.committees).joinedload(CommitteeAssignment.committee),
                selectinload(Petition.updates).joinedload(PetitionUpdate.update),
                joinedload(Petition.response),
                selectinload(Petition.petition_tags).selectinload(PetitionTag.tag),
            )
        )

        result = await self.session.execute(stmt)
        petition = result.scalars().first()

        if not petition:
            raise PetitionNotFoundError(message=f"Petition with ID {petition_id} not found.")

        return PetitionPageSchema.model_validate(petition)

    async def get_user_petitions(
        self, *, user: User, page: int = 1, items_per_page: int = 10
    ) -> ReturnPetition:
        """
        Fetch all petitions created by a specific user with pagination.

        Parameters
        ----------
        user: User
            The petition author.
        page : int, optional
            Current page index (1-based), by default 1.
        items_per_page : int, optional
            Number of petitions to return per page, by default 10.

        Returns
        -------
        ReturnPetition
            Paginated collection of petitions authored by the specified user.

        Raises
        ------
        PetitionNotFoundError
            Raised when no petitions are found for the given user.
        """
        # Base query
        base_stmt = (
            select(Petition)
            .join(Petition.author)
            .where(User.username == user.username)
            .order_by(Petition.created_at.desc())
        )

        # Count total items
        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total_items_result = await self.session.execute(count_stmt)
        total_items = total_items_result.scalar_one()

        if total_items == 0:
            raise PetitionNotFoundError(message=f"No petitions found for user '{user.username}'.")

        # Calculate pagination
        total_pages = math.ceil(total_items / items_per_page) if total_items > 0 else 1
        start_idx = (page - 1) * items_per_page

        # Paginated query with eager loading
        paginated_stmt = (
            base_stmt.offset(start_idx)
            .limit(items_per_page)
            .options(
                selectinload(Petition.author),
                selectinload(Petition.petition_tags).selectinload(PetitionTag.tag),
            )
        )

        result = await self.session.execute(paginated_stmt)
        petitions = result.scalars().unique().all()

        petitions_for_response = [PetitionPageSchema.model_validate(p) for p in petitions]

        return ReturnPetition(
            page_info=PageInfo(
                page=page,
                items=len(petitions_for_response),
                total_items=total_items,
                total_pages=total_pages,
            ),
            petitions=petitions_for_response,
        )

    async def get_petition_description(self, petition_id: int) -> PetitionDescriptionSchema:
        """
        Got rid of descriptions from the search endpoint because of site slowing down
        from response length. Descriptions will need to be queried if not received from
        timeline endpoint
        """
        petition = await self.session.get(Petition, petition_id)
        if not petition:
            raise PetitionNotFoundError(message=f"Petition with ID {petition_id} not found.")

        return PetitionDescriptionSchema(petition_description=petition.description)


    async def upload_petition_image(self, file: UploadFile, bucket: str = "images"):
        original_ext = file.filename.split(".")[-1] if "." in file.filename else "png"

        # generate secure hashed filename
        random_suffix = str(uuid.uuid4())
        hashed_name = f"{hashlib.md5(random_suffix.encode()).hexdigest()}.{original_ext}"

        await run_in_threadpool(
            self.s3_client.upload_fileobj,
            file.file,
            "images",
            hashed_name,
            ExtraArgs={"ContentType": file.content_type},
        )
        auth_service = AuthService(config=Config())

        base = "http://localhost:9000" if auth_service.is_dev() else auth_service.frontend_url()

        return f"{base}/{bucket}/{hashed_name}"

    async def create_petition(
        self, *, petition: CreatePetition, user: User
    ) -> PetitionCreateResponse:
        """
        Create a new petition.

        Parameters
        ----------
        petition : CreatePetition
            Petition payload validated at the API layer.
        user: User
            Current user that is creating the petition.

        Returns
        -------
        int
            Identifier of the newly created petition.

        Raises
        ------
        DBError
            Raised when the petition cannot be persisted because of a database failure.
        """

        petition_data = petition.model_dump()

        raw_tag_ids = petition_data.pop("tags", []) or []
        valid_tag_ids = []

        if raw_tag_ids:
            result = await self.session.execute(select(Tag.id).where(Tag.id.in_(raw_tag_ids)))
            valid_tag_ids = result.scalars().all()
            if len(valid_tag_ids) < len(set(raw_tag_ids)):
                self.logger.warning(
                    f"Dropped invalid tag IDs: {set(raw_tag_ids) - set(valid_tag_ids)}"
                )

        max_id_result = await self.session.execute(select(func.max(Petition.id)))
        current_id = (max_id_result.scalar() or 0) + 1

        max_retries = 100
        attempt = 0

        while attempt < max_retries:
            try:
                new_petition = Petition(**petition_data)
                new_petition.id = current_id
                new_petition.created_at = datetime.now(UTC)
                new_petition.expires = new_petition.created_at + timedelta(days=210)
                new_petition.author = user

                self.session.add(new_petition)
                await self.session.flush()

                if valid_tag_ids:
                    for tid in valid_tag_ids:
                        self.session.add(
                            PetitionTag(
                                tag_id=tid, petition_id=new_petition.id, assigned_by=user.username
                            )
                        )

                from sqlalchemy import text

                await self.session.execute(
                    text(f"SELECT setval('petitions_id_seq', {current_id}, true)")
                )

                await self.session.commit()
                await self.session.refresh(new_petition)
                return PetitionCreateResponse.model_validate(new_petition)

            except IntegrityError as e:
                await self.session.rollback()
                error_str = str(e)
                if "petitions_pkey" in error_str or "duplicate key" in error_str.lower():
                    current_id += 1
                    attempt += 1
                    continue
                raise DBError(
                    message="Error creating new petition.",
                    context={"op": "petition_create", "error": repr(e)},
                ) from e

        raise DBError(
            message="Error creating new petition after multiple retries.",
            context={"op": "petition_create", "retries": max_retries, "last_tried_id": current_id},
        )

    async def edit_draft_petition(
        self, *, petition_id: int, petition: CreatePetition, user: User
    ) -> PetitionCreateResponse:
        """
        Edit an existing draft petition.

        Parameters
        ----------
        petition_id: int
            The id related to the petition to edit
        petition : CreatePetition
            Petition payload validated at the API layer.
        user: User
            The user that is updating the draft

        Returns
        -------
        PetitionCreateResponse
            The updated petition.

        Raises
        ------
        PetitionNotFoundError
            Raised when the petition cannot be located.
        DBError
            Raised when the petition cannot be persisted because of a database failure.
        """
        stmt = select(UserPetition).where(
            UserPetition.author_id == user.username, UserPetition.petition_id == petition_id
        )

        result = await self.session.execute(stmt)
        user_petition = result.scalars().first()
        if not user_petition:
            raise PermissionDeniedError(
                message="You do not have permission to edit this petition. Only the author can edit their own draft petitions."
            )

        stmt = (
            select(Petition)
            .where(Petition.id == petition_id)
            .options(selectinload(Petition.petition_tags))
        )
        result = await self.session.execute(stmt)

        existing_petition = result.scalars().first()
        if not existing_petition or not existing_petition.is_draft:
            raise PetitionNotFoundError(message=f"Draft petition with ID {petition_id} not found.")

        existing_petition.title = petition.title
        existing_petition.description = petition.description
        existing_petition.is_draft = petition.is_draft
        existing_petition.created_at = datetime.now(UTC)
        existing_petition.expires = existing_petition.created_at + timedelta(days=210)
        existing_petition.petition_tags = [PetitionTag(tag_id=tag_id, petition_id=petition_id)
                                              for tag_id in petition.tags]

        try:
            await self.session.commit()
            await self.session.refresh(existing_petition)
            return PetitionCreateResponse.model_validate(existing_petition)

        except IntegrityError as e:
            await self.session.rollback()
            raise DBError(
                message="Error editing draft petition.",
                context={"op": "petition_edit_draft", "petition_id": petition_id, "error": repr(e)},
            ) from e


    async def report_petition(
        self, *, report: ReportCreate, petition_id: int, current_user: User
    ) -> None:
        """
        Generate a report for a specific petition.

        Parameters
        ----------
        report : ReportCreate
            Report payload provided by the API layer.
        petition_id : int
            Identifier of the petition being reported.
        current_user : User
            Authenticated user submitting the report.

        Raises
        ------
        PetitionNotFoundError
            Raised when the petition cannot be located.
        DBError
            Raised when the report cannot be persisted because of a database failure.
        """
        # Ensure petition exists (was missing before)
        petition = await self.session.get(Petition, petition_id)
        if not petition:
            raise PetitionNotFoundError(message=f"Petition with ID {petition_id} not found.")

        new_report = Report(
            reported_for=report.reason,
            reported_at=datetime.now(UTC),
        )

        try:
            self.session.add(new_report)
            await self.session.flush()  # get new_report.id
            await self.session.refresh(new_report)

            petition_report_assoc = PetitionReport(
                petition_id=petition_id, report_id=new_report.id, reporter_id=current_user.username
            )

            self.session.add(petition_report_assoc)
            await self.session.commit()

        except IntegrityError as e:
            await self.session.rollback()
            raise DBError(
                message="Error reporting petition.",
                context={
                    "op": "petition_report",
                    "petition_id": petition_id,
                    "user": current_user.username,
                    "error": repr(e),
                },
            ) from e

    async def charge_petition(self, *, petition_id: int, committee_id: int) -> None:
        """
        Assign a petition to a committee. Replaces any existing assignment.

        Parameters
        ----------
        petition_id : int
            Identifier of the petition to assign.
        committee_id : int
            Committee identifier to associate with the petition.

        Returns
        -------
        None

        Raises
        ------
        PetitionNotFoundError
            Raised when the petition cannot be located.
        CommitteeNotFoundError
            Raised when the requested committee does not exist.
        DBError
            Raised when the committee assignment cannot be persisted because of a database failure.
        """
        petition = await self.session.get(Petition, petition_id)
        if not petition:
            raise PetitionNotFoundError(message=f"Petition with ID {petition_id} not found.")

        committee = await self.session.get(Committee, committee_id)
        if not committee:
            raise CommitteeNotFoundError(
                message=f"Committee with ID {committee_id} not found.",
            )

        # Check if there's an existing assignment
        existing_assignment = await self.session.execute(
            select(CommitteeAssignment).where(CommitteeAssignment.petition_id == petition_id)
        )
        existing = existing_assignment.scalars().first()

        if existing:
            # Update the existing assignment to the new committee
            existing.committee_id = committee_id
            existing.assigned_at = datetime.now(UTC)
        else:
            # Create a new assignment
            self.session.add(
                CommitteeAssignment(
                    petition_id=petition_id,
                    committee_id=committee_id,
                    assigned_at=datetime.now(UTC),
                )
            )

        petition.status = StatusEnum.CHARGED

        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise DBError(
                message="Error charging petition to committee.",
                context={
                    "op": "petition_charge",
                    "petition_id": petition_id,
                    "committee_id": committee_id,
                    "error": repr(e),
                },
            ) from e

    async def unassign_petition(self, *, petition_id: int, committee_id: int) -> None:
        """
        Remove committee assignment from a petition.

        Parameters
        ----------
        petition_id : int
            Identifier of the petition to unassign.
        committee_id : int
            Committee identifier to detach from the petition.

        Returns
        -------
        None

        Raises
        ------
        PetitionNotFoundError
            Raised when the petition cannot be located.
        CommitteeNotFoundError
            Raised when there is no matching committee assignment to remove.
        DBError
            Raised when the unassignment cannot be persisted because of a database failure.
        """
        petition = await self.session.get(Petition, petition_id)
        if not petition:
            raise PetitionNotFoundError(message=f"Petition with ID {petition_id} not found.")

        stmt = delete(CommitteeAssignment).where(
            CommitteeAssignment.petition_id == petition_id,
            CommitteeAssignment.committee_id == committee_id,
        )
        result = await self.session.execute(stmt)

        # If no rows were affected, there were no such assignments
        if result.rowcount == 0:
            raise CommitteeNotFoundError(
                message=f"No committee assignment found for petition ID {petition_id} with committee ID {committee_id}.",
            )

        # After unassignment, adjust petition status
        if not petition.has_response and petition.expires > datetime.now(UTC):
            petition.status = StatusEnum.ACTIVE
        else:
            petition.status = StatusEnum.EXPIRED

        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise DBError(
                message="Error unassigning petition from committee.",
                context={
                    "op": "petition_unassign",
                    "petition_id": petition_id,
                    "committee_id": committee_id,
                    "error": repr(e),
                },
            ) from e

    async def add_petition_update(
        self,
        *,
        petition_id: int,
        draft_creator_username: str,
        update_message: str,
        original_draft_id: int | None = None,
        is_draft: bool,
        is_response: bool,
    ) -> PetitionUpdateSchema:
        """
        Add a draft update to a petition.

        Parameters
        ----------
        petition_id : int
            Identifier of the petition to update.
        draft_creator_username : str
            Username of the user authoring the draft update.
        update_message : str
            Content of the draft update.
        original_draft_id : int | None, optional
            Identifier of the original draft to thread under, by default None.
        is_draft:
            flag whether an update should be saved as a draft or not
        is_response: bool
            flag whether an update is an official response from SG

        Returns
        -------
        Update
            Newly created draft update instance.

        Raises
        ------
        PetitionNotFoundError
            Raised when the petition or referenced draft cannot be located.
        CommitteeNotFoundError
            Raised when the author is not a member of an assigned committee.
        DBError
            Raised when the draft update cannot be persisted because of a database failure.
        """
        petition = await self.session.get(Petition, petition_id)
        if not petition:
            raise PetitionNotFoundError(message=f"Petition with ID {petition_id} not found.")

        # Ensure creator is in at least one assigned committee
        stmt = select(CommitteeAssignment).where(
            CommitteeAssignment.petition_id == petition_id,
            CommitteeAssignment.committee.has(
                Committee.members.any(User.username == draft_creator_username)
            ),
        )
        result = await self.session.execute(stmt)
        assignment = result.scalars().first()
        if not assignment:
            raise CommitteeNotFoundError(
                message=(
                    f"User '{draft_creator_username}' is not a member of any committee assigned to petition ID {petition_id}."
                ),
            )

        thread_id = None
        if original_draft_id:
            original_draft = await self.session.get(Update, original_draft_id)
            if not original_draft:
                raise PetitionNotFoundError(
                    message=f"Original draft with ID {original_draft_id} not found."
                )
            thread_id = original_draft.submission_thread_id or original_draft.id

        update = Update(
            author_id=draft_creator_username,
            message=update_message,
            created_at=datetime.now(UTC),
            is_draft=is_draft,
            is_approved=is_response,
            submission_thread_id=thread_id,
            approved_by=draft_creator_username if is_response else None,
        )

        try:
            self.session.add(update)
            await self.session.flush()

            pu = PetitionUpdate(
                petition_id=petition_id, update_id=update.id, is_response=is_response
            )

            if is_response:
                petition.has_response = True
                petition.response_id = update.id
                petition.status = StatusEnum.RESPONDED
            else:
                petition.status = StatusEnum.CHARGED

            self.session.add(pu)

            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise DBError(
                message="Error adding draft update.",
                context={
                    "op": "petition_add_draft_update",
                    "petition_id": petition_id,
                    "author": draft_creator_username,
                    "original_draft_id": original_draft_id,
                    "error": repr(e),
                },
            ) from e

        return PetitionUpdateSchema(
            is_response=is_response, update=UpdateSchema.model_validate(update), review=None
        )

    async def edit_draft_update(
        self, *, draft_username: str, petition_id: int, details: UpdateSchema
    ) -> PetitionUpdateSchema:
        stmt = (
            select(PetitionUpdate)
            .join(PetitionUpdate.update)
            .where(
                PetitionUpdate.petition_id == petition_id,
                PetitionUpdate.update_id == details.id,
                Update.author_id == draft_username,
            )
            .options(selectinload(PetitionUpdate.update))
        )
        result = await self.session.execute(stmt)
        pu = result.scalar_one_or_none()

        if not pu:
            raise PetitionUpdateNotFoundError(
                message=f"Update with ID {details.id} and author {draft_username} not found."
            )

        if not pu.update.is_draft:
            raise PetitionUpdateSubmittedAlreadyError(
                message=f"Update with ID {pu.update.id} cannot be updated; already submitted."
            )

        pu.update.message = details.message
        pu.update.created_at = datetime.now(UTC)
        pu.update.is_draft = details.is_draft

        try:
            await self.session.commit()
            await self.session.refresh(pu)
        except IntegrityError as e:
            await self.session.rollback()
            raise DBError(
                message="Error editing update.",
                context={
                    "op": "edit_draft_update",
                    "author": draft_username,
                    "update_id": details.id,
                    "error": repr(e),
                },
            ) from e

        return PetitionUpdateSchema(
            is_response=pu.is_response, update=UpdateSchema.model_validate(pu.update), review=None
        )

    async def delete_draft_update(self, *, petition_id: int, update_id: int, username: str) -> None:
        stmt = (
            select(PetitionUpdate)
            .join(PetitionUpdate.update)
            .where(
                PetitionUpdate.petition_id == petition_id,
                PetitionUpdate.update_id == update_id,
                Update.author_id == username,
            )
            .options(selectinload(PetitionUpdate.update))
        )
        result = await self.session.execute(stmt)
        pu = result.scalar_one_or_none()

        if not pu:
            raise PetitionUpdateNotFoundError(
                message=f"Update with ID {update_id} and author {username} not found."
            )

        if not pu.update.is_draft:
            raise PetitionUpdateSubmittedAlreadyError(message="Cannot delete published updates.")

        try:
            await self.session.delete(pu)
            await self.session.delete(pu.update)
            await self.session.commit()

        except IntegrityError as e:
            await self.session.rollback()
            raise DBError(
                message="Error deleting update.",
                context={
                    "op": "delete_draft_update",
                    "author": username,
                    "update_id": update_id,
                    "error": repr(e),
                },
            ) from e

    async def review_petition_draft_update(
        self, *, petition_id: int, review: ReviewUpdateRequest, reviewer_username: str
    ) -> ReviewUpdateResponse:
        """
        Approve or reject a draft update for a petition.

        Parameters
        ----------
        petition_id : int
            Identifier of the petition containing the draft update.
        review: ReviewUpdateRequest
            Review payload containing approval decision and message.
        reviewer_username: str
            The username of the reviewer performing the action.

        Returns
        -------
        ReviewUpdateResponse

        Raises
        ------
        PetitionNotFoundError
            Raised when the draft update cannot be located for the petition.
        DBError
            Raised when the review cannot be persisted because of a database failure.
        """
        stmt = (
            select(Update)
            .join(PetitionUpdate, Update.id == PetitionUpdate.update_id)
            .where(Update.id == review.update_id, Update.is_draft.is_(True))
        )
        result = await self.session.execute(stmt)
        update = result.scalars().first()
        if not update:
            raise PetitionNotFoundError(
                message=f"Draft update with ID {review.update_id} not found for petition ID {petition_id}."
            )

        petition = await self.session.get(Petition, petition_id)
        if not petition:
            raise PetitionNotFoundError(message=f"Petition with ID {petition_id} not found.")

        new_review = Review(
            update_id=review.update_id,
            reviewer_id=reviewer_username,
            is_approved=review.approve,
            message=review.message,
            created_at=datetime.now(UTC),
        )

        update.is_draft = not review.approve
        update.is_approved = review.approve

        if review.approve:
            petition.status = StatusEnum.CHARGED
            petition.is_draft = False

            update.approved_by = reviewer_username
            update.is_approved = True
            update.is_draft = False

        self.session.add(new_review)

        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise DBError(
                message="Error reviewing draft update.",
                context={
                    "op": "petition_review_draft_update",
                    "petition_id": petition_id,
                    "update_id": review.update_id,
                    "error": repr(e),
                },
            ) from e

        return ReviewUpdateResponse.model_validate(new_review)

    async def get_petition_timeline(
        self, *, petition_id: int, admin_view: bool
    ) -> UpdateTimelineResponse:

        petition = await self.session.get(Petition, petition_id)
        if not petition:
            raise PetitionNotFoundError(message=f"Petition with ID {petition_id} not found.")

        query = (
            select(PetitionUpdate)
            .join(Update, PetitionUpdate.update_id == Update.id)
            .where(PetitionUpdate.petition_id == petition_id)
            .options(selectinload(PetitionUpdate.update))
            .order_by(Update.created_at.asc())
        )

        if admin_view:
            query = query.options(selectinload(PetitionUpdate.update).selectinload(Update.reviews))
        else:
            query = query.where(
                or_(
                    PetitionUpdate.is_response.is_(True),
                    and_(Update.is_draft.is_(False), Update.is_approved.is_(True)),
                )
            )

        result = await self.session.execute(query)
        timeline_items = result.scalars().all()
        timeline_items = [
            PetitionUpdateSchema(
                is_response=item.is_response,
                update=item.update,
                review=item.update.reviews if admin_view else None,
            )
            for item in timeline_items
        ]

        return UpdateTimelineResponse(
            petition_description=petition.description,
            petition_updates=timeline_items
        )


    # TODO: throwing 500 for some reason
    async def get_petition_committee(self, petition_id: int):
        result = await self.session.execute(
            select(CommitteeAssignment)
            .where(CommitteeAssignment.petition_id == petition_id)
            .options(selectinload(CommitteeAssignment.committee))
        )
        assignment = result.scalars().first()
        if assignment is None:
            return None
        return assignment.committee


def get_petition_service(
    session: Annotated[AsyncSession, Depends(get_async_db_session)],
    s3_client: Annotated[BaseClient, Depends(get_s3_client)],
    logger: Annotated[logging.Logger, Depends(get_logger)],
) -> PetitionService:
    """Factory function to obtain a PetitionService instance."""
    return PetitionService(session=session, s3_client=s3_client, logger=logger)


PetitionServiceDep = Annotated[PetitionService, Depends(get_petition_service)]
