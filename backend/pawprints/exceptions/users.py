from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .base import ServiceError


class UserNotFoundError(ServiceError):
    """5000 — User Not Found (HTTP 404)."""

    def __init__(
        self,
        message: str = "The requested user could not be found.",
        *,
        context: Mapping[str, Any] | None = None,
    ):
        super().__init__(code="5000", message=message, status_code=404, context=context)


class CommitteeNotFoundError(ServiceError):
    """5001 — Committee Not Found (HTTP 404)."""

    def __init__(
        self,
        message: str = "The requested committee could not be found.",
        *,
        context: Mapping[str, Any] | None = None,
    ):
        super().__init__(code="5001", message=message, status_code=404, context=context)


class CommitteeMemberNotFoundError(ServiceError):
    """5002 — Committee Member Not Found (HTTP 404)."""

    def __init__(
        self,
        message: str = "No committee members found.",
        *,
        context: Mapping[str, Any] | None = None,
    ):
        super().__init__(code="5002", message=message, status_code=404, context=context)


class UserAlreadyInCommitteeError(ServiceError):
    """5003 — User Already in Committee (HTTP 409)."""

    def __init__(
        self,
        message: str = "User is already a member of this committee.",
        *,
        context: Mapping[str, Any] | None = None,
    ):
        super().__init__(code="5003", message=message, status_code=409, context=context)


class CommitteeAlreadyExistsError(ServiceError):
    """5004 — Committee Already Exists (HTTP 409)."""

    def __init__(
        self,
        message: str = "Committee already exists.",
        *,
        context: Mapping[str, Any] | None = None,
    ):
        super().__init__(code="5004", message=message, status_code=409, context=context)


class UserHasNotSignedPetitionError(ServiceError):
    """5005 — User Has Not Signed Petition (HTTP 400)."""

    def __init__(
        self,
        message: str = "User has not signed this petition.",
        *,
        context: Mapping[str, Any] | None = None,
    ):
        super().__init__(code="5005", message=message, status_code=400, context=context)
