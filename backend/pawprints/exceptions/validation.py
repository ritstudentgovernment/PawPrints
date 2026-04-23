from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .base import ServiceError


class InvalidRequestBodyError(ServiceError):
    def __init__(
        self,
        message: str = "The request body is malformed or invalid.",
        *,
        context: Mapping[str, Any] | None = None,
    ):
        detail = message
        if context:
            errors = context.get("errors") or []
            if errors:
                missing: list[str] = []
                other: list[str] = []
                for err in errors:
                    loc = err.get("loc") or ()
                    path_parts = [str(part) for part in loc if part != "body"]
                    path = ".".join(path_parts) or "<root>"
                    err_type = (err.get("type") or "").lower()
                    if err_type in {"missing", "value_error.missing"}:
                        missing.append(path)
                    else:
                        msg = err.get("msg") or "Invalid value."
                        other.append(f"{path}: {msg}" if path != "<root>" else msg)
                if missing:
                    unique_missing = sorted({m for m in missing if m})
                    fields = ", ".join(unique_missing) if unique_missing else "<root>"
                    suffix = "s" if len(unique_missing) != 1 else ""
                    detail = f"Missing required field{suffix}: {fields}."
                elif other:
                    detail = "; ".join(other)
        super().__init__(code="3000", message=detail, status_code=400, context=context)


class InvalidParameterError(ServiceError):
    """3001 — Invalid Parameter (HTTP 400)."""

    def __init__(
        self,
        message: str = "An invalid parameter was provided in the request.",
        *,
        context: Mapping[str, Any] | None = None,
    ):
        super().__init__(code="3001", message=message, status_code=400, context=context)
