from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .base import ServiceError


class RoleNotFoundError(ServiceError):
    """6000 — Role Not Found (HTTP 404)."""

    def __init__(
        self,
        message: str = "The requested role could not be found.",
        *,
        context: Mapping[str, Any] | None = None,
    ):
        super().__init__(code="6000", message=message, status_code=404, context=context)


class RoleAlreadyExistsError(ServiceError):
    """6001 — Role Already Exists (HTTP 409)."""

    def __init__(
        self, message: str = "Role already exists.", *, context: Mapping[str, Any] | None = None
    ):
        super().__init__(code="6001", message=message, status_code=409, context=context)


class PermissionNotFoundError(ServiceError):
    """6002 — Permission Not Found (HTTP 404)."""

    def __init__(
        self,
        message: str = "The requested permission could not be found.",
        *,
        context: Mapping[str, Any] | None = None,
    ):
        super().__init__(code="6002", message=message, status_code=404, context=context)
