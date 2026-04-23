from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .base import ServiceError


class AuthenticationFailedError(ServiceError):
    """2000 — Authentication Failed (HTTP 401)."""

    def __init__(
        self,
        message: str = "Authentication failed. Invalid credentials provided.",
        *,
        context: Mapping[str, Any] | None = None,
    ):
        super().__init__(code="2000", message=message, status_code=401, context=context)


class PermissionDeniedError(ServiceError):
    """2001 — Permission Denied (HTTP 403)."""

    def __init__(
        self,
        message: str = "You do not have permission to perform this action.",
        *,
        context: Mapping[str, Any] | None = None,
    ):
        super().__init__(code="2001", message=message, status_code=403, context=context)


class NonStudentError(ServiceError):
    """2002 — Non-student login attempt (HTTP 403).

    Raised when a user authenticates via SAML but their ``rit_edu_account_type``
    is not ``student``.  The router redirects them to the frontend root with
    ``?non_student=1`` and does **not** issue a session cookie.
    """

    def __init__(
        self,
        account_type: str | None = None,
        *,
        context: Mapping[str, Any] | None = None,
    ):
        ctx = dict(context or {})
        if account_type is not None:
            ctx["account_type"] = account_type
        super().__init__(
            code="2002",
            message="Only current RIT students are permitted to use this service.",
            status_code=403,
            context=ctx or None,
        )
