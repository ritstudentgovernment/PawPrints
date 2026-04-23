from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .base import ServiceError


class NotFoundError(ServiceError):
    """
    Generic 404 Not Found.

    Notes
    -----
    Must be instantiated with a documented `code` (e.g., "5000", "6000").
    """

    def __init__(
        self,
        *,
        code: str,
        message: str = "Resource not found.",
        context: Mapping[str, Any] | None = None,
    ):
        super().__init__(code=code, message=message, status_code=404, context=context)


class ConflictError(ServiceError):
    """
    Generic 409 Conflict.

    Notes
    -----
    Must be instantiated with a documented `code` (e.g., "4001", "5003", "5004").
    """

    def __init__(
        self, *, code: str, message: str = "Conflict.", context: Mapping[str, Any] | None = None
    ):
        super().__init__(code=code, message=message, status_code=409, context=context)
