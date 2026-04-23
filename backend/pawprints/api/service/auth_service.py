# services/auth.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import logging
from typing import Any, ClassVar, Literal

from pydantic import BaseModel, EmailStr, Field, ValidationError
from saml2.client import Saml2Client
import saml2.entity
from sqlalchemy.ext.asyncio import AsyncSession

from config import Config
from pawprints.auth.jwt import create_jwt_token
from pawprints.exceptions import (
    AuthenticationFailedError,  # 2000 / 401
    DBError,  # 1000 / 500
    InternalServerError,  # 1000 / 500
    NonStudentError,  # 2002 / 403
    ServiceError,
    ServiceUnavailableError,  # 1001 / 503
)
from pawprints.models.orm import User

# ----------------------------- Pydantic models -------------------------------


class SAMLIdentity(BaseModel):
    """
    Normalises SAML assertion attributes into a typed flat structure.

    ``username``, ``first_name``, ``last_name``, and ``email`` are required —
    authentication fails if the IdP omits any of them.
    All ``rit_edu_*`` fields are optional; RIT's Shibboleth IdP may send them
    as OID URNs or friendly names depending on attribute-release configuration.
    """

    username: str = Field(..., description="SAML uid")
    first_name: str = Field(..., description="SAML givenName")
    last_name: str = Field(..., description="SAML sn")
    email: EmailStr = Field(..., description="SAML mail")
    rit_edu_account_type: str | None = Field(
        None, description="RIT account type (e.g. Student, Faculty)"
    )
    rit_edu_campus_u: str | None = Field(None, description="RIT campus (undergrad)")
    rit_edu_campus_g: str | None = Field(None, description="RIT campus (grad)")
    rit_edu_college_u: str | None = Field(None, description="RIT college (undergrad)")
    rit_edu_college_g: str | None = Field(None, description="RIT college (grad)")

    # Shibboleth may send RIT-specific attributes under OID URNs instead of
    # friendly names depending on IdP attribute release configuration.
    # Map friendly name → OID so we can fall back automatically.
    _OID_ALIASES: ClassVar[dict[str, str]] = {
        "ritEduAccountType": "urn:oid:1.3.6.1.4.1.4447.1.59",
        "ritEduCampusU": "urn:oid:1.3.6.1.4.1.4447.1.122",
        "ritEduCampusG": "urn:oid:1.3.6.1.4.1.4447.1.123",
        "ritEduCollegeU": "urn:oid:1.3.6.1.4.1.4447.1.112",
        "ritEduCollegeG": "urn:oid:1.3.6.1.4.1.4447.1.115",
    }

    @classmethod
    def from_saml_dict(cls, identity: dict[str, list[str]]) -> SAMLIdentity:
        _log = logging.getLogger("pawprints.saml")

        def first(k: str) -> str | None:
            """Return the first value for key k, falling back to its OID alias."""
            v = identity.get(k) or identity.get(cls._OID_ALIASES.get(k, ""))
            result = v[0] if isinstance(v, list) and v else None
            return result if result else None

        raw_uid = first("uid")
        username = raw_uid.split("@")[0] if raw_uid else None

        # Full attribute values only at DEBUG — not leaked in INFO/WARNING/prod logs.
        _log.debug(
            "SAML assertion attributes: %s",
            {k: (v[0] if isinstance(v, list) and v else v) for k, v in identity.items()},
        )

        data = dict(
            username=username,
            first_name=first("givenName"),
            last_name=first("sn"),
            email=first("mail"),
            rit_edu_account_type=first("ritEduAccountType"),
            rit_edu_campus_u=first("ritEduCampusU"),
            rit_edu_campus_g=first("ritEduCampusG"),
            rit_edu_college_u=first("ritEduCollegeU"),
            rit_edu_college_g=first("ritEduCollegeG"),
        )
        try:
            return cls.model_validate(data)  # Pydantic v2
        except ValidationError as e:
            # Log received keys (not values) at WARNING so it's visible without DEBUG.
            _log.warning(
                "SAML attribute validation failed — received keys: %s | errors: %s",
                list(identity.keys()),
                e.errors(),
            )
            # Full mapped values (contains PII) only at DEBUG.
            _log.debug("SAML mapped values: %s", data)
            raise AuthenticationFailedError(
                message="Missing or invalid SAML attributes.",
                context={"received_keys": list(identity.keys()), "errors": e.errors()},
            ) from e


class CookieSpec(BaseModel):
    name: str
    value: str
    httponly: bool = True
    secure: bool = False
    samesite: Literal["lax", "none", "strict"] = "lax"
    max_age: int = 28800  # seconds

    def to_set_cookie_kwargs(self) -> dict[str, Any]:
        return dict(
            key=self.name,
            value=self.value,
            httponly=self.httponly,
            secure=self.secure,
            samesite=self.samesite,
            max_age=self.max_age,
        )


class RedirectInfo(BaseModel):
    url: str


class LogoutResult(RedirectInfo):
    cookie_name: str


class AuthFinalizeResult(RedirectInfo):
    """
    Returned by handle_acs(). Router sets the cookie and performs the redirect.
    """

    cookie: CookieSpec
    token: str
    expiry: datetime


# ------------------------------- AuthService ---------------------------------


@dataclass
class AuthService:
    """
    Business logic for auth flows (SAML + DEV shortcuts).
    HTTP-free: returns data the router can turn into a Response.
    """

    config: Config
    logger: logging.Logger

    # ---------- env helpers ----------
    def _is_dev(self) -> bool:
        return (self.config.MODE or "").upper() == "DEV"

    def _is_prod(self) -> bool:
        return (self.config.MODE or "").upper() == "PROD"

    def _cookie_name(self) -> str:
        return self.config.AUTH_COOKIE_NAME

    def _cookie_params_for_env(self) -> dict[str, Any]:
        max_age = self.config.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        if self._is_dev():
            return dict(httponly=True, secure=False, samesite="lax", max_age=max_age)
        return dict(httponly=True, secure=True, samesite="none", max_age=max_age)

    def _frontend_url(self, path: str = "") -> str:
        base = self.config.FRONTEND_URL.rstrip("/")
        sub = path.lstrip("/")

        if not sub:
            return base

        if "=" in sub and "?" not in sub and "/" not in sub:
            return f"{base}/?{sub}"

        return f"{base}/{sub}"

    # ---------- SAML client ----------
    def _get_saml_client(self) -> Saml2Client:
        if not self._is_prod():
            raise ServiceUnavailableError("SAML client requested outside PROD mode.")
        # Late import avoids errors in DEV
        from pawprints.auth.saml_config import saml_config

        return Saml2Client(config=saml_config)

    # ---------- metadata ----------
    async def get_metadata_xml(self) -> tuple[str, str]:
        """
        Returns (content, media_type) as SP metadata XML.
        """
        if self._is_dev():
            return ("DEV MODE", "text/plain")

        try:
            from pawprints.auth.saml_config import generate_sp_metadata, raw_config

            xml = generate_sp_metadata(raw_config)
            return (xml, "text/xml")
        except Exception as e:
            self.logger.error("Error generating SAML metadata: %s", repr(e))
            raise InternalServerError(
                message="Error generating SAML metadata.",
                context={"reason": "saml_metadata_error", "error": repr(e)},
            ) from e

    # ---------- login initiation ----------
    async def initiate_login(self, ref: str = "") -> RedirectInfo:
        """
        DEV: bypass SAML → send user to a landing/profile page.
        PROD: returns IdP redirect location from SAML client.
        """
        if self._is_dev():
            url = self._frontend_url(ref) if ref else self._frontend_url("profile")
            return RedirectInfo(url=url)

        try:
            c = self._get_saml_client()
            _, auth_info = c.prepare_for_authenticate(relay_state=ref)
            redirect_url = dict(auth_info["headers"]).pop("Location")
            return RedirectInfo(url=redirect_url)
        except Exception as e:
            raise InternalServerError(
                message="Failed to initiate SAML login.",
                context={"reason": "saml_prepare_authenticate_failed", "error": repr(e)},
            ) from e

    async def initiate_logout(self) -> LogoutResult:
        """
        DEV: bypass SAML → send user to a landing/profile page.
        PROD: Redirects to Official RIT logout.html page for Shibboleth
        (deletes Shibboleth headers after).
        """
        if self._is_dev():
            return LogoutResult(url=self._frontend_url("profile/"), cookie_name="")

        try:
            from pawprints.auth.saml_config import get_logout_url

            return LogoutResult(url=get_logout_url(), cookie_name=self._cookie_name())
        except Exception as e:
            raise InternalServerError(
                message="Failed to initiate logout.",
                context={"reason": "saml_logout_endpoint_failed", "error": repr(e)},
            )

    async def parse_saml_response(self, saml_response: str) -> SAMLIdentity:
        """
        Parse the SAMLResponse and return the identity.
        """
        if not self._is_prod():
            raise ServiceUnavailableError("SAML parsing is not available in DEV mode.")

        try:
            c = self._get_saml_client()
            authn_response = c.parse_authn_request_response(
                saml_response, saml2.entity.BINDING_HTTP_POST
            )
            if not authn_response:
                raise AuthenticationFailedError("No authentication response returned.")

            identity_raw = authn_response.get_identity()
            if not identity_raw:
                raise AuthenticationFailedError("No identity found in SAML response.")

            self.logger.debug("Identity Raw: %s", identity_raw)

            identity = SAMLIdentity.from_saml_dict(identity_raw)
            return identity
        except ServiceError:
            raise
        except Exception as e:
            raise AuthenticationFailedError(
                message="Invalid SAML response.",
                context={"error": repr(e)},
            ) from e

    def _create_user_from_identity(self, identity: SAMLIdentity) -> User:
        """Create a new User instance from SAMLIdentity."""
        return User(
            username=identity.username,
            first_name=identity.first_name,
            last_name=identity.last_name,
            email=identity.email,
            rit_edu_account_type=identity.rit_edu_account_type,
            rit_edu_campus_u=identity.rit_edu_campus_u,
            rit_edu_campus_g=identity.rit_edu_campus_g,
            rit_edu_college_u=identity.rit_edu_college_u,
            rit_edu_college_g=identity.rit_edu_college_g,
        )

    def _update_basic_profile(self, user: User, identity: SAMLIdentity) -> bool:
        """Update basic profile fields (name, email). Returns True if any changes made."""
        updated = False
        if user.first_name != identity.first_name:
            user.first_name = identity.first_name
            updated = True
        if user.last_name != identity.last_name:
            user.last_name = identity.last_name
            updated = True
        if user.email != identity.email:
            user.email = identity.email
            updated = True
        return updated

    def _update_rit_edu_fields(self, user: User, identity: SAMLIdentity) -> bool:
        """
        Update RIT edu fields only when SAML provides a non-None value that differs
        from what is already stored. This preserves existing DB values when the IdP
        omits an attribute (common for campus/college on grad-only accounts).
        Returns True if any field was changed.
        """
        updated = False

        fields = (
            ("rit_edu_account_type", identity.rit_edu_account_type),
            ("rit_edu_campus_u", identity.rit_edu_campus_u),
            ("rit_edu_campus_g", identity.rit_edu_campus_g),
            ("rit_edu_college_u", identity.rit_edu_college_u),
            ("rit_edu_college_g", identity.rit_edu_college_g),
        )
        for attr, saml_value in fields:
            if saml_value is not None and getattr(user, attr) != saml_value:
                setattr(user, attr, saml_value)
                updated = True

        return updated

    async def upsert_user_from_identity(
        self, *, session: AsyncSession, identity: SAMLIdentity
    ) -> None:
        """Upsert a User based on the provided SAMLIdentity."""
        try:
            user = await session.get(User, identity.username)

            if not user:
                user = self._create_user_from_identity(identity)
                session.add(user)
                await session.commit()
                await session.refresh(user)
                return

            changed = self._update_basic_profile(user, identity)
            changed |= self._update_rit_edu_fields(user, identity)
            if changed:
                try:
                    await session.commit()
                except Exception as e:
                    await session.rollback()
                    self.logger.warning(
                        "Could not persist updated profile for %s: %s",
                        identity.username,
                        repr(e),
                    )

        except Exception as e:
            raise DBError(
                message="Database error while upserting user from SAML identity.",
                context={"op": "user_upsert", "username": identity.username, "error": repr(e)},
            ) from e

    async def create_cookie(self, token: str) -> CookieSpec:
        """
        Create a CookieSpec for the auth token.
        """
        return CookieSpec(name=self._cookie_name(), value=token, **self._cookie_params_for_env())

    # ---------- ACS handling ----------
    async def handle_acs(
        self, *, session: AsyncSession, saml_response: str, relay_state: str = ""
    ) -> AuthFinalizeResult:
        """
        Parse the SAMLResponse, validate identity, upsert user, mint JWT, and
        return a cookie spec + frontend redirect target.

        Raises ``NonStudentError`` if the authenticated account is not a student,
        so the router can redirect without issuing any session cookie.
        """
        identity = await self.parse_saml_response(saml_response)

        # Always upsert so the DB stays current with the latest Shibboleth data,
        # regardless of account type.
        await self.upsert_user_from_identity(session=session, identity=identity)

        # Gate token/session on account type from the SAML assertion (not the DB),
        # since the DB may not yet have complete data for all users.
        # Student Government staff accounts (e.g. sgstaff@rit.edu) bypass the
        # student-only check — their email username ends with "sg" before @rit.edu.
        email = (identity.email or "").strip().lower()
        is_sg_staff = email.endswith("sg@rit.edu")

        account_type = (identity.rit_edu_account_type or "").strip().lower()
        if account_type != "student" and not is_sg_staff:
            self.logger.warning(
                "Non-student login blocked: username=%s account_type=%r",
                identity.username,
                identity.rit_edu_account_type,
            )
            raise NonStudentError(account_type=identity.rit_edu_account_type)

        if is_sg_staff and account_type != "student":
            self.logger.info(
                "SG staff login allowed via email bypass: username=%s account_type=%r",
                identity.username,
                identity.rit_edu_account_type,
            )

        try:
            token, expiry = create_jwt_token(identity.model_dump())
            cookie = await self.create_cookie(token=token)
            return AuthFinalizeResult(
                url=self._frontend_url(relay_state), cookie=cookie, token=token, expiry=expiry
            )
        except Exception as e:
            raise InternalServerError(
                message="Failed to finalize login.",
                context={"reason": "jwt_or_cookie_failed", "error": repr(e)},
            ) from e
