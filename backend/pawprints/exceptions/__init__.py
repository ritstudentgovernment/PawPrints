"""
Exceptions package for standardized API errors (NumPy-style docs).
"""

from .auth import AuthenticationFailedError, NonStudentError, PermissionDeniedError
from .base import ServiceError
from .general import DBError, InternalServerError, ServiceUnavailableError
from .generic import ConflictError, NotFoundError
from .petitions import PetitionAlreadySignedError, PetitionNotFoundError
from .registry import CODE_TO_EXCEPTION, error_from_code
from .roles import PermissionNotFoundError, RoleAlreadyExistsError, RoleNotFoundError
from .tags import TagAlreadyExistsError, TagNotFoundError
from .users import (
    CommitteeAlreadyExistsError,
    CommitteeMemberNotFoundError,
    CommitteeNotFoundError,
    UserAlreadyInCommitteeError,
    UserHasNotSignedPetitionError,
    UserNotFoundError,
)
from .validation import InvalidParameterError, InvalidRequestBodyError

__all__ = [
    # base
    "ServiceError",
    # general
    "InternalServerError",
    "ServiceUnavailableError",
    "DBError",
    # auth
    "AuthenticationFailedError",
    "PermissionDeniedError",
    "NonStudentError",
    # validation
    "InvalidRequestBodyError",
    "InvalidParameterError",
    # petitions
    "PetitionNotFoundError",
    "PetitionAlreadySignedError",
    # users/committees
    "UserNotFoundError",
    "CommitteeNotFoundError",
    "CommitteeMemberNotFoundError",
    "UserAlreadyInCommitteeError",
    "CommitteeAlreadyExistsError",
    "UserHasNotSignedPetitionError",
    # roles/permissions
    "RoleNotFoundError",
    "RoleAlreadyExistsError",
    "PermissionNotFoundError",
    # tags
    "TagNotFoundError",
    "TagAlreadyExistsError",
    # generic
    "NotFoundError",
    "ConflictError",
    # registry
    "CODE_TO_EXCEPTION",
    "error_from_code",
]
