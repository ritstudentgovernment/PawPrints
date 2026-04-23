"""Service layer for tag operations."""

from datetime import UTC, datetime
import logging
from typing import Annotated

from fastapi import Depends
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from pawprints.database.session import get_async_db_session
from pawprints.exceptions import (
    DBError,
    PetitionNotFoundError,
    TagNotFoundError,
)
from pawprints.logger import get_logger
from pawprints.models.orm import Petition, PetitionTag, Tag, User
from pawprints.models.schema import (
    PageInfo,
    PetitionTagAssign,
    PetitionTagResponse,
    TagCreate,
    TagListResponse,
    TagSchema,
    TagUpdate,
)


class TagService:
    """Service for managing tags and petition tag assignments."""

    def __init__(self, session: AsyncSession, logger: logging.Logger):
        self.session = session
        self.logger = logger

    async def create_tag(self, tag_data: TagCreate) -> TagSchema:
        """
        Create a new tag.

        Parameters
        ----------
        tag_data : TagCreate
            Tag data to create.

        Returns
        -------
        TagSchema
            The created tag.

        Raises
        ------
        DBError
            If tag creation fails (e.g., duplicate name).
        """
        try:
            tag = Tag(**tag_data.model_dump())
            self.session.add(tag)
            await self.session.commit()
            await self.session.refresh(tag)
            return TagSchema.model_validate(tag)
        except IntegrityError as e:
            await self.session.rollback()
            raise DBError(
                message="Tag with this name already exists.",
                context={"op": "tag_create", "error": str(e)},
            ) from e

    async def get_tag(self, tag_id: int) -> TagSchema:
        """
        Get a tag by ID.

        Parameters
        ----------
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
        result = await self.session.execute(select(Tag).where(Tag.id == tag_id))
        tag = result.scalar_one_or_none()
        if not tag:
            raise TagNotFoundError(
                message=f"Tag with ID {tag_id} not found.",
                context={"tag_id": tag_id},
            )
        return TagSchema.model_validate(tag)

    async def list_tags(self, page: int = 1, items_per_page: int = 50) -> TagListResponse:
        """
        List all tags with pagination.

        Parameters
        ----------
        page : int
            Page number (1-indexed).
        items_per_page : int
            Number of items per page.

        Returns
        -------
        TagListResponse
            Paginated list of tags.
        """
        # Get total count
        count_result = await self.session.execute(select(func.count(Tag.id)))
        total_items = count_result.scalar() or 0

        # Calculate pagination
        offset = (page - 1) * items_per_page
        total_pages = (total_items + items_per_page - 1) // items_per_page

        # Get tags
        result = await self.session.execute(
            select(Tag).order_by(Tag.name).offset(offset).limit(items_per_page)
        )
        tags = result.scalars().all()

        return TagListResponse(
            page_info=PageInfo(
                page=page,
                items=len(tags),
                total_items=total_items,
                total_pages=total_pages,
            ),
            tags=[TagSchema.model_validate(tag) for tag in tags],
        )

    async def update_tag(self, tag_id: int, tag_data: TagUpdate) -> TagSchema:
        """
        Update a tag.

        Parameters
        ----------
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
        result = await self.session.execute(select(Tag).where(Tag.id == tag_id))
        tag = result.scalar_one_or_none()
        if not tag:
            raise TagNotFoundError(
                message=f"Tag with ID {tag_id} not found.",
                context={"tag_id": tag_id},
            )

        # Update fields
        update_data = tag_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(tag, field, value)

        try:
            await self.session.commit()
            await self.session.refresh(tag)
            return TagSchema.model_validate(tag)
        except IntegrityError as e:
            await self.session.rollback()
            raise DBError(
                message="Failed to update tag (possibly duplicate name).",
                context={"op": "tag_update", "tag_id": tag_id, "error": str(e)},
            ) from e

    async def delete_tag(self, tag_id: int) -> None:
        """
        Delete a tag.

        Parameters
        ----------
        tag_id : int
            The tag ID.

        Raises
        ------
        TagNotFoundError
            If the tag doesn't exist.
        DBError
            If deletion fails.
        """
        result = await self.session.execute(select(Tag).where(Tag.id == tag_id))
        tag = result.scalar_one_or_none()
        if not tag:
            raise TagNotFoundError(
                message=f"Tag with ID {tag_id} not found.",
                context={"tag_id": tag_id},
            )

        try:
            await self.session.delete(tag)
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise DBError(
                message="Failed to delete tag.",
                context={"op": "tag_delete", "tag_id": tag_id, "error": str(e)},
            ) from e

    async def add_tag_to_petition(
        self, petition_id: int, tag_data: PetitionTagAssign, user: User
    ) -> list[PetitionTagResponse]:
        """
        Add a tag to a petition (replaces existing tag if any).

        Parameters
        ----------
        petition_id : int
            The petition ID.
        tag_data : PetitionTagAssign
            Tag assignment data.
        user : User
            User performing the operation.

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
        # Verify petition exists
        petition_result = await self.session.execute(
            select(Petition).where(Petition.id == petition_id)
        )
        petition = petition_result.unique().scalar_one_or_none()
        if not petition:
            raise PetitionNotFoundError(
                message=f"Petition with ID {petition_id} not found.",
                context={"petition_id": petition_id},
            )

        # Verify tag exists
        tags_result = await self.session.execute(select(Tag.id).where(Tag.id.in_(tag_data.tag_ids)))
        existing_tag_ids = {row[0] for row in tags_result.all()}

        missing_tags = set(tag_data.tag_ids) - existing_tag_ids
        if missing_tags:
            raise TagNotFoundError(message=f"Tags not found: {missing_tags}")

        try:
            await self.session.execute(
                delete(PetitionTag).where(PetitionTag.petition_id == petition_id)
            )

            new_assignments = [
                PetitionTag(
                    petition_id=petition_id,
                    tag_id=tid,
                    assigned_by=user.username,
                    assigned_at=datetime.now(UTC),
                )
                for tid in tag_data.tag_ids
            ]
            self.session.add_all(new_assignments)

            await self.session.commit()

            stmt = (
                select(PetitionTag)
                .where(PetitionTag.petition_id == petition_id)
                .options(selectinload(PetitionTag.tag))
            )
            result = await self.session.execute(stmt)
            loaded_assignments = result.scalars().all()

            # Now Pydantic has everything it needs in memory
            return [PetitionTagResponse.model_validate(t) for t in loaded_assignments]

        except Exception as e:
            await self.session.rollback()
            raise DBError(message="Failed to update tags.", context={"error": str(e)}) from e

    async def remove_tag_from_petition(self, petition_id: int) -> None:
        """
        Remove tag from a petition.

        Parameters
        ----------
        petition_id : int
            The petition ID.

        Raises
        ------
        PetitionNotFoundError
            If no tag is assigned to this petition.
        DBError
            If removal fails.
        """
        result = await self.session.execute(
            select(PetitionTag).where(PetitionTag.petition_id == petition_id)
        )
        petition_tag = result.scalar_one_or_none()
        if not petition_tag:
            raise PetitionNotFoundError(
                message=f"No tag assigned to petition {petition_id}.",
                context={"petition_id": petition_id},
            )

        try:
            await self.session.delete(petition_tag)
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise DBError(
                message="Failed to remove tag from petition.",
                context={"op": "petition_tag_remove", "petition_id": petition_id, "error": str(e)},
            ) from e

    async def get_petition_tag(self, petition_id: int) -> PetitionTagResponse | None:
        """
        Get the tag assigned to a petition.

        Parameters
        ----------
        petition_id : int
            The petition ID.

        Returns
        -------
        PetitionTagResponse | None
            The tag assignment, or None if no tag is assigned.
        """
        result = await self.session.execute(
            select(PetitionTag).where(PetitionTag.petition_id == petition_id)
        )
        petition_tag = result.scalar_one_or_none()
        if not petition_tag:
            return None
        return PetitionTagResponse.model_validate(petition_tag)


# Dependency
def get_tag_service(
    session: Annotated[AsyncSession, Depends(get_async_db_session)],
    logger: Annotated[logging.Logger, Depends(get_logger)],
) -> TagService:
    """Get tag service instance."""
    return TagService(session=session, logger=logger)


TagServiceDep = Annotated[TagService, Depends(get_tag_service)]
