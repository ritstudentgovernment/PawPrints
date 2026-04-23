# routes/auth.py
from __future__ import annotations

from fastapi import APIRouter, Form
from fastapi.responses import RedirectResponse, Response

from config import Config
from pawprints.api.service.auth_service import AuthService
from pawprints.api.utils import DBSessionDep
from pawprints.exceptions import NonStudentError, ServiceError
from pawprints.logger import get_logger

router = APIRouter(tags=["Authentication"])
auth_service = AuthService(config=Config(), logger=get_logger())


@router.get("/metadata")
async def metadata() -> Response:
    content, media_type = await auth_service.get_metadata_xml()
    return Response(content=content, media_type=media_type)


@router.get("/")
async def initiate_login(ref: str = "") -> RedirectResponse:
    target = await auth_service.initiate_login(ref=ref)
    return RedirectResponse(url=target.url, status_code=302)


@router.get("/logout")
async def initiate_logout() -> RedirectResponse:
    target = await auth_service.initiate_logout()
    resp = RedirectResponse(url=target.url, status_code=302)
    resp.delete_cookie(key=target.cookie_name)
    return resp


@router.post("/acs")
async def acs(
    session: DBSessionDep,
    SAMLResponse: str = Form(...),
    relay_state: str = Form(default="", alias="RelayState"),
):
    try:
        result = await auth_service.handle_acs(
            session=session, saml_response=SAMLResponse, relay_state=relay_state
        )
        resp = RedirectResponse(url=result.url, status_code=302)
        resp.set_cookie(**result.cookie.to_set_cookie_kwargs())
        return resp
    except NonStudentError as e:
        auth_service.logger.warning(f"Non-student login attempt blocked [{e.code}]: {e.message}")
        return RedirectResponse(url=auth_service._frontend_url("?non_student=1"), status_code=302)
    except ServiceError as e:
        auth_service.logger.warning(f"ACS login failed [{e.code}]: {e.message}")
        return RedirectResponse(url=auth_service._frontend_url("?login_error=1"), status_code=302)
    except Exception as e:
        auth_service.logger.error(f"Unexpected ACS error: {e}")
        return RedirectResponse(url=auth_service._frontend_url("?login_error=1"), status_code=302)
