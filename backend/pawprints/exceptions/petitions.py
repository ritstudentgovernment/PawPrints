from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .base import ServiceError


class PetitionNotFoundError(ServiceError):
    """4000 — Petition Not Found (HTTP 404)."""

    def __init__(
        self,
        message: str = "The requested petition could not be found.",
        *,
        context: Mapping[str, Any] | None = None,
    ):
        super().__init__(code="4000", message=message, status_code=404, context=context)


class PetitionAlreadySignedError(ServiceError):
    """4001 — Petition Already Signed (HTTP 409)."""

    def __init__(
        self,
        message: str = "You have already signed this petition.",
        *,
        context: Mapping[str, Any] | None = None,
    ):
        super().__init__(code="4001", message=message, status_code=409, context=context)


class PetitionSubmittedAlreadyError(ServiceError):
    """4002 — Petition Already Submitted (HTTP 409)."""

    def __init__(
        self,
        message: str = "This petition has already been submitted.",
        *,
        context: Mapping[str, Any] | None = None,
    ):
        super().__init__(code="4002", message=message, status_code=409, context=context)


class PetitionUpdateNotFoundError(ServiceError):
    """4003 — Petition Update Not Found (HTTP 404)."""

    def __init__(
        self,
        message: str = "The requested petition update could not be found.",
        *,
        context: Mapping[str, Any] | None = None,
    ):
        super().__init__(code="4003", message=message, status_code=404, context=context)


class PetitionUpdateSubmittedAlreadyError(ServiceError):
    """4004 - Petition Update Submitted Already (HTTP 409)."""

    def __init__(
        self,
        message: str = "The requested petition update could not be edited.",
        *,
        context: Mapping[str, Any] | None = None,
    ):
        super().__init__(code="4004", message=message, status_code=409, context=context)


class OwnPetitionError(ServiceError):
    """4001 — Error when user is attempting to sign their own petition (HTTP 423)"""

    def __init__(
        self,
        message: str = "Cannot sign/unsign your own petition",
        *,
        context: Mapping[str, Any] | None = None,
    ):
        super().__init__(code="4005", message=message, status_code=423, context=context)


class PetitionClosedError(ServiceError):
    """4001 — Petition Closed (HTTP 404)."""

    def __init__(
        self,
        message: str = "No more signatures for this petition allowed.",
        *,
        context: Mapping[str, Any] | None = None,
    ):
        super().__init__(code="4006", message=message, status_code=404, context=context)
