from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any


@dataclass(eq=False)
class ServiceError(Exception):
    """
    Base API exception with standardized payload.

    Parameters
    ----------
    code : str
        Stable application error code (e.g., "1000", "2001").
    message : str
        Human-readable error message.
    status_code : int
        HTTP status code to return (e.g., 400, 404, 500).
    context : dict, optional
        Additional machine-readable metadata (e.g., field, reason).

    Notes
    -----
    Serializes to:

    .. code-block:: json

        {
          "detail": {
            "code": "<error_code>",
            "message": "<error_message>",
            "context": { ... }  # optional
          }
        }
    """

    code: str
    message: str
    status_code: int
    context: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        super().__init__(self.message)

    # Serialization helpers
    def detail_payload(self) -> dict[str, Any]:
        """Return the `detail` dictionary payload."""
        payload: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.context:
            payload["context"] = dict(self.context)
        return payload

    def to_response(self) -> dict[str, Any]:
        """Return the full error response body."""
        return {"detail": self.detail_payload()}

    # Friendly representations
    def __str__(self) -> str:  # pragma: no cover
        try:
            phrase = HTTPStatus(self.status_code).phrase
        except ValueError:
            phrase = "Unknown Status"
        return f"{self.code} {phrase}: {self.message}"

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"{self.__class__.__name__}(code={self.code!r}, "
            f"message={self.message!r}, status_code={self.status_code!r}, "
            f"context={dict(self.context) if self.context else None!r})"
        )
