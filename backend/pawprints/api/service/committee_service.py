from __future__ import annotations

from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from pawprints.database.session import get_async_db_session
from pawprints.exceptions import (
    CommitteeAlreadyExistsError,  # 5004 / 409
    CommitteeMemberNotFoundError,  # 5002 / 404
    CommitteeNotFoundError,  # 5001 / 404
    DBError,  # 1000 / 500
    UserAlreadyInCommitteeError,  # 5003 / 409
    UserNotFoundError,  # 5000 / 404
)
from pawprints.models.orm import Committee, User, UserCommitteeAssociation, UserRole
from pawprints.models.schema import CommitteeMemberResponse, CommitteeSchema, UserSchema


class CommitteeService:
    """Service class for committee-related operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_committee_members(self, *, committee_id: int) -> list[UserSchema]:
        stmt = (
            select(Committee)
            .where(Committee.id == committee_id)
            .options(
                # eager load the 'members' association + the related 'user'
                selectinload(Committee.members).selectinload(UserCommitteeAssociation.user)
            )
        )
        result = await self.session.execute(stmt)
        committee = result.scalars().first()

        if not committee:
            raise CommitteeNotFoundError(message=f"Committee with ID {committee_id} not found.")

        all_committee_members = [
            UserSchema.model_validate(member.user) for member in committee.members
        ]

        if len(all_committee_members) == 0:
            raise CommitteeMemberNotFoundError(message="No committee members found.")

        return all_committee_members

    async def add_user_to_committee(
        self, *, username_to_add: str, committee_id: int
    ) -> CommitteeMemberResponse:
        """Add a member to a committee given a committee id and username."""
        stmt = (
            select(Committee)
            .where(Committee.id == committee_id)
            .options(selectinload(Committee.members).selectinload(UserCommitteeAssociation.user))
        )
        result = await self.session.execute(stmt)
        committee = result.scalars().first()
        if not committee:
            raise CommitteeNotFoundError(message=f"Committee with ID {committee_id} not found.")

        # get the user you want to add
        user = await self.session.get(User, username_to_add)
        if not user:
            raise UserNotFoundError(message=f"User '{username_to_add}' not found.")

        # check if user is already in committee
        if any(member.user.username == user.username for member in committee.members):
            raise UserAlreadyInCommitteeError(message="User is already a member of this committee.")

        new_member = UserCommitteeAssociation()
        new_member.user = user
        new_member.committee = committee
        committee.members.append(new_member)

        self.session.add(new_member)

        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise DBError(
                message="Error creating new user-committee association.",
                context={
                    "op": "committee_add_user",
                    "committee_id": committee_id,
                    "username": username_to_add,
                    "error": repr(e),
                },
            ) from e

        user_schema = UserSchema.model_validate(user)
        committee_schema = CommitteeSchema.model_validate(committee)
        return CommitteeMemberResponse(user=user_schema, committee=committee_schema)

    async def remove_user_from_committee(self, *, username_to_remove: str, committee_id: int):
        """Remove a member from a committee given a committee id and username."""
        committee = await self.session.get(Committee, committee_id)
        if not committee:
            raise CommitteeNotFoundError(message=f"Committee with ID {committee_id} not found.")

        user = await self.session.get(User, username_to_remove)
        if not user:
            raise UserNotFoundError(message=f"User '{username_to_remove}' not found.")

        # Use SQLAlchemy boolean '&' instead of Python 'and'
        stmt = select(UserCommitteeAssociation).where(
            (UserCommitteeAssociation.committee_id == committee.id)
            & (UserCommitteeAssociation.username == user.username)
        )
        result = await self.session.execute(stmt)
        assoc = result.scalars().first()

        # If not present, nothing to do (idempotent)
        if assoc is None:
            return

        await self.session.delete(assoc)
        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise DBError(
                message="Error deleting user-committee association.",
                context={
                    "op": "committee_remove_user",
                    "committee_id": committee_id,
                    "username": username_to_remove,
                    "error": repr(e),
                },
            ) from e

    async def create_committee(
        self,
        *,
        committee_to_add: CommitteeSchema,
    ) -> Committee:
        # Uniqueness check by name
        stmt = select(Committee).where(Committee.name == committee_to_add.name)
        result = await self.session.execute(stmt)
        existing = result.scalars().first()
        if existing:
            raise CommitteeAlreadyExistsError(
                message=f"Committee '{committee_to_add.name}' already exists."
            )

        try:
            new_committee = Committee(
                name=committee_to_add.name, description=committee_to_add.description
            )
            self.session.add(new_committee)
            await self.session.flush()
            await self.session.refresh(new_committee)

        except IntegrityError as e:
            await self.session.rollback()
            raise DBError(
                message="Error creating new committee.",
                context={"op": "committee_create", "name": committee_to_add.name, "error": repr(e)},
            ) from e

        return new_committee

    async def delete_committee(
        self,
        *,
        committee_id: int,
    ):
        c = await self.session.get(Committee, committee_id)
        if not c:
            raise CommitteeNotFoundError(message=f"Committee with ID {committee_id} not found.")

        await self.session.delete(c)
        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise DBError(
                message="Error deleting committee.",
                context={"op": "committee_delete", "committee_id": committee_id, "error": repr(e)},
            ) from e

    async def get_all_committees(self) -> list[Committee]:
        """Get all committees."""
        stmt = select(Committee)
        result = await self.session.execute(stmt)
        committees = result.scalars().all()
        if not committees:
            # No specific code for "no committees at all"—use 5001 category with a clear message
            raise CommitteeNotFoundError(message="No committees found.")
        return list(committees)

    async def add_role_to_committee(self, *, role_id: int, committee_id: int) -> dict[str, Any]:
        """Add all users of a specific role to a specific committee."""
        committee = await self.session.get(Committee, committee_id)
        if not committee:
            raise CommitteeNotFoundError(message=f"Committee with ID {committee_id} not found.")

        # Get all users with the specified role
        stmt = (
            select(User)
            .join(UserRole, UserRole.username == User.username)
            .where(UserRole.role_id == role_id)
        )
        result = await self.session.execute(stmt)
        users = result.unique().scalars().all()

        if not users:
            raise UserNotFoundError(message=f"No users found with role ID {role_id}.")

        # Get existing committee members to avoid duplicates
        existing_stmt = select(UserCommitteeAssociation.username).where(
            UserCommitteeAssociation.committee_id == committee_id
        )
        existing_result = await self.session.execute(existing_stmt)
        existing_usernames = {row[0] for row in existing_result.all()}

        added_count = 0
        skipped_count = 0

        for user in users:
            if user.username in existing_usernames:
                skipped_count += 1
                continue

            new_member = UserCommitteeAssociation()
            new_member.user = user
            new_member.committee = committee
            self.session.add(new_member)
            added_count += 1

        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise DBError(
                message="Error adding role members to committee.",
                context={
                    "op": "committee_add_role",
                    "committee_id": committee_id,
                    "role_id": role_id,
                    "error": repr(e),
                },
            ) from e

        return {
            "committee_id": committee_id,
            "committee_name": committee.name,
            "role_id": role_id,
            "added_count": added_count,
            "skipped_count": skipped_count,
        }

    async def add_role_to_all_committees(self, *, role_id: int) -> dict[str, Any]:
        """Add all users of a specific role to all committees."""
        # Get all committees
        committees_stmt = select(Committee)
        committees_result = await self.session.execute(committees_stmt)
        committees = committees_result.scalars().all()

        if not committees:
            raise CommitteeNotFoundError(message="No committees found.")

        # Get all users with the specified role
        users_stmt = (
            select(User)
            .join(UserRole, UserRole.username == User.username)
            .where(UserRole.role_id == role_id)
        )
        users_result = await self.session.execute(users_stmt)
        users = users_result.unique().scalars().all()

        if not users:
            raise UserNotFoundError(message=f"No users found with role ID {role_id}.")

        # Get all existing committee memberships to avoid duplicates
        existing_stmt = select(
            UserCommitteeAssociation.username,
            UserCommitteeAssociation.committee_id,
        )
        existing_result = await self.session.execute(existing_stmt)
        existing_pairs = {(row.username, row.committee_id) for row in existing_result.all()}

        total_added = 0
        total_skipped = 0
        committee_details = []

        for committee in committees:
            added_count = 0
            skipped_count = 0

            for user in users:
                if (user.username, committee.id) in existing_pairs:
                    skipped_count += 1
                    continue

                new_member = UserCommitteeAssociation()
                new_member.user = user
                new_member.committee = committee
                self.session.add(new_member)
                added_count += 1

            total_added += added_count
            total_skipped += skipped_count
            committee_details.append(
                {
                    "committee_id": committee.id,
                    "committee_name": committee.name,
                    "added": added_count,
                    "skipped": skipped_count,
                }
            )

        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise DBError(
                message="Error adding role members to all committees.",
                context={
                    "op": "committee_add_role_to_all",
                    "role_id": role_id,
                    "error": repr(e),
                },
            ) from e

        return {
            "role_id": role_id,
            "total_added": total_added,
            "total_skipped": total_skipped,
            "committees": committee_details,
        }


def get_committee_service(
    session: Annotated[AsyncSession, Depends(get_async_db_session)],
) -> CommitteeService:
    """
    Dependency factory for CommitteeService.
    FastAPI will call this function to create the service.
    """
    return CommitteeService(session=session)


CommitteeServiceDep = Annotated[CommitteeService, Depends(get_committee_service)]
