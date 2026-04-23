import functools
import inspect
import math
from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from pawprints.database.session import get_async_db_session as get_db_session
from pawprints.exceptions import (
    PermissionDeniedError,  # 2001 / 403
)
from pawprints.models.schema import (
    PageInfo,
)

DBSessionDep = Annotated[AsyncSession, Depends(get_db_session)]


def paginate(query, page: int, items_per_page: int):
    """Paginates a list of records.

    This function takes a list of records and returns a subset based on the
    requested page number and items per page, along with pagination metadata.

    Parameters
    ----------
    query : list
        The full list of records to be paginated.
    page : int
        The current page number (1-indexed).
    items_per_page : int
        The maximum number of items to include on a single page.

    Returns
    -------
    list
        A list containing two elements: a `PageInfo` object with pagination details,
        and a list of records for the current page.
    """
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    data = query[start_idx:end_idx]
    paginate_info = {
        "page": page,
        "items": len(data),
        "total_items": len(query),
        "total_pages": math.ceil(len(query) / items_per_page),
    }
    paginate_info = PageInfo(**paginate_info)
    return [paginate_info, data]


# TODO: Optimize with fewer queries, not needed tbh
#  Petition already stores all the info, just need to join and load it in
# async def attach_committees(session: DBSessionDep, records: list):
#     """Attaches additional related information (committees, authors, updates) to petition records.
#
#     This asynchronous function iterates through a list of petition records,
#     fetches their associated committees, authors, and updates from the database,
#     and then constructs a new list of `Petition` Pydantic models with this
#     enriched data.
#
#     Parameters
#     ----------
#     session : DBSessionDep
#         The database session dependency.
#     records : list
#         A list containing two elements:
#         - `records[0]` (PageInfo): Pagination metadata.
#         - `records[1]` (list of ORM Petition objects): The raw petition records
#           to be enriched.
#
#     Returns
#     -------
#     list
#         A list containing two elements:
#         - `records[0]` (PageInfo): The original pagination metadata.
#         - `list of Petition`: A list of `Petition` Pydantic models, each
#           including its associated committees, author's username, and updates.
#     """
#     petitions = []
#     petition_records = records[1]
#     for record in petition_records:
#         if record:
#             # get userid
#             stmt = select(UserPetition).where(UserPetition.petition_id == record.id)
#             user = await session.execute(stmt)
#             user = user.scalars().first()
#             user_id = user.author_id
#             author = select(User).where(User.username == user_id)
#             author = await session.execute(author)
#             author = author.scalars().first()
#             user_name = author.username
#
#             # get all updates
#             stmt = select(PetitionUpdate).where(PetitionUpdate.petition_id == record.id)
#             updates = await session.execute(stmt)
#             updates = updates.scalars().all()
#             update_list = []
#             for pu in updates:
#                 is_response = pu.is_response
#
#                 # Fetch the actual Update record
#                 update_stmt = select(Update).where(Update.id == pu.update_id)
#                 update_result = await session.execute(update_stmt)
#                 update_obj = update_result.scalars().first()
#
#                 if update_obj is None:
#                     continue  # skip if update not found
#
#                 # Resolve author
#                 if update_obj.author_id == user_id:
#                     update_author = user_name
#                 else:
#                     author_stmt = select(User).where(User.username == update_obj.author_id)
#                     author_result = await session.execute(author_stmt)
#                     author = author_result.scalars().first()
#                     update_author = (
#                         "RIT STUDENT GOVERNMENT" if author is None else author.first_name
#                     )
#
#                 # Now build the Pydantic object
#                 update_list.append(
#                     PetitionUpdateSchema(
#                         message=update_obj.message,
#                         created_at=update_obj.created_at,
#                         author=update_author,
#                         is_response=is_response,
#                     )
#                 )
#
#             stmt = select(CommitteeAssignment).where(CommitteeAssignment.petition_id == record.id)
#             committees = await session.execute(stmt)
#             committees = committees.scalars().all()
#             committee_list = []
#             for comm in committees:
#                 committee_id = comm.committee_id
#                 stmt = select(Committee).where(Committee.id == committee_id)
#                 committee = await session.execute(stmt)
#                 committee = committee.scalars().first()
#                 committee_list.append(
#                     CommitteeSchema(
#                         name=committee.name, description=committee.description, id=committee.id
#                     )
#                 )
#
#             petitions.append(
#                 PetitionPageSchema(
#                     **record.__dict__,
#                     committees=committee_list,
#                     author=user_name,
#                     updates=update_list,
#                 )
#             )
#     return [records[0], petitions]


def _std_perm(dep_func):
    if inspect.iscoroutinefunction(dep_func):

        @functools.wraps(dep_func)
        async def _wrapper(*args, **kwargs):
            try:
                return await dep_func(*args, **kwargs)
            except HTTPException as e:
                if e.status_code == 403:
                    raise PermissionDeniedError() from e
                raise

        return _wrapper
    else:

        @functools.wraps(dep_func)
        def _wrapper(*args, **kwargs):
            try:
                return dep_func(*args, **kwargs)
            except HTTPException as e:
                if e.status_code == 403:
                    raise PermissionDeniedError() from e
                raise

        return _wrapper
