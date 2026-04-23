from __future__ import annotations

from collections.abc import Mapping

from .auth import AuthenticationFailedError, PermissionDeniedError
from .base import ServiceError
from .general import InternalServerError, ServiceUnavailableError
from .petitions import PetitionAlreadySignedError, PetitionNotFoundError
from .roles import PermissionNotFoundError, RoleAlreadyExistsError, RoleNotFoundError
from .users import (
    CommitteeAlreadyExistsError,
    CommitteeMemberNotFoundError,
    CommitteeNotFoundError,
    UserAlreadyInCommitteeError,
    UserHasNotSignedPetitionError,
    UserNotFoundError,
)
from .validation import InvalidParameterError, InvalidRequestBodyError

CODE_TO_EXCEPTION: dict[str, type[ServiceError]] = {
    "1000": InternalServerError,
    "1001": ServiceUnavailableError,
    "2000": AuthenticationFailedError,
    "2001": PermissionDeniedError,
    "3000": InvalidRequestBodyError,
    "3001": InvalidParameterError,
    "4000": PetitionNotFoundError,
    "4001": PetitionAlreadySignedError,
    "5000": UserNotFoundError,
    "5001": CommitteeNotFoundError,
    "5002": CommitteeMemberNotFoundError,
    "5003": UserAlreadyInCommitteeError,
    "5004": CommitteeAlreadyExistsError,
    "5005": UserHasNotSignedPetitionError,
    "6000": RoleNotFoundError,
    "6001": RoleAlreadyExistsError,
    "6002": PermissionNotFoundError,
}


def error_from_code(
    code: str, *, message: str | None = None, context: Mapping[str, object] | None = None
) -> ServiceError:
    """
    Instantiate a concrete `ServiceError` subclass by code.

    Parameters
    ----------
    code : str
        Documented error code.
    message : str, optional
        Custom message; defaults to the class's standard message.
    context : dict, optional
        Extra metadata (e.g., ``{"field": "name", "reason": "too short"}``).

    Returns
    -------
    ServiceError

    Raises
    ------
    KeyError
        If `code` is unknown.
    """
    exc_cls = CODE_TO_EXCEPTION.get(code)
    if exc_cls is None:
        raise KeyError(f"Unknown error code: {code}")
    return exc_cls(message=message) if message is not None else exc_cls()
