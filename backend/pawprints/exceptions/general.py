from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .base import ServiceError


class InternalServerError(ServiceError):
    """1000 — Internal Server Error (HTTP 500)."""

    def __init__(
        self,
        message: str = "An unexpected error occurred on the server.",
        *,
        context: Mapping[str, Any] | None = None,
    ):
        super().__init__(code="1000", message=message, status_code=500, context=context)


class ServiceUnavailableError(ServiceError):
    """1001 — Service Unavailable (HTTP 503)."""

    def __init__(
        self,
        message: str = "The service is temporarily unavailable.",
        *,
        context: Mapping[str, Any] | None = None,
    ):
        super().__init__(code="1001", message=message, status_code=503, context=context)


class DBError(InternalServerError):
    """
    Database execution error (maps to code 1000).
    Alias of :class:`InternalServerError` for backwards compatibility.
    """

    pass
