"""
Activity-tracking middleware.

On every request it increments the matching row in ``stats_activity_log``:
  - date      → today (UTC)
  - hour      → current UTC hour
  - endpoint_group → first path segment after /api/v1/ (e.g. "petitions")
  - method    → HTTP method

For SAML ACS (login) requests it also increments ``login_count``.

Uses a direct INSERT … ON CONFLICT DO UPDATE so it never blocks the
request and never raises – failures are silently logged.
"""

from __future__ import annotations

from datetime import UTC, datetime
import logging

from sqlalchemy import text
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from pawprints.database.session import sessioncontroller

logger = logging.getLogger("pawprints.activity")

_SKIP_PREFIXES = ("/health", "/docs", "/redoc", "/openapi", "/saml2/metadata")
_API_PREFIX = "/api/v1/"


def _endpoint_group(path: str) -> str:
    """Map a request path to a coarse group name."""
    if path.startswith(_API_PREFIX):
        rest = path[len(_API_PREFIX) :]
        segment = rest.split("/")[0]
        return segment or "root"
    if path.startswith("/saml2"):
        return "auth"
    return "other"


class ActivityTrackingMiddleware(BaseHTTPMiddleware):
    """Async middleware that records per-request activity into stats_activity_log."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        path = request.url.path
        if any(path.startswith(p) for p in _SKIP_PREFIXES):
            return response

        # Fire-and-forget — never block the response
        try:
            await self._record(request, response.status_code)
        except Exception as exc:
            logger.debug("activity tracking write failed: %s", exc)

        return response

    async def _record(self, request: Request, status_code: int) -> None:
        now = datetime.now(UTC)
        today = now.date()
        hour = now.hour
        group = _endpoint_group(request.url.path)
        method = request.method.upper()

        is_login = (
            request.url.path.startswith("/saml2/acs")
            and method == "POST"
            and status_code in (200, 302, 303)
        )

        username: str | None = None
        try:
            from config import Config
            from pawprints.auth.jwt import decode_jwt_token

            cfg = Config()
            token = request.cookies.get(cfg.AUTH_COOKIE_NAME)
            if token:
                payload = decode_jwt_token(token)
                username = payload.get("sub")
        except Exception:
            logger.debug("Could not extract username from JWT for activity tracking")

        unique_users_inc = 1 if username is not None else 0
        login_count_inc = 1 if is_login else 0

        sql = text(
            """
            INSERT INTO stats_activity_log
                (date, hour, endpoint_group, method, request_count, unique_users, login_count, updated_at)
            VALUES
                (:date, :hour, :group, :method, 1, :unique_users_inc, :login_count_inc, NOW())
            ON CONFLICT (date, hour, endpoint_group, method)
            DO UPDATE SET
                request_count = stats_activity_log.request_count + 1,
                unique_users  = stats_activity_log.unique_users + :unique_users_inc,
                updated_at    = NOW(),
                login_count   = stats_activity_log.login_count + :login_count_inc
            """
        )

        if sessioncontroller._engine is None:
            return

        async with sessioncontroller._engine.begin() as conn:
            await conn.execute(
                sql,
                {
                    "date": today,
                    "hour": hour,
                    "group": group,
                    "method": method,
                    "unique_users_inc": unique_users_inc,
                    "login_count_inc": login_count_inc,
                },
            )
