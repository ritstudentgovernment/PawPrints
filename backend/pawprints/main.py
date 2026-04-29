import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
import logging
import os
from zoneinfo import ZoneInfo

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from starlette.middleware.sessions import SessionMiddleware

from config import Config
from pawprints.api import (
    admin_petition_router,
    auth_router,
    committee_router,
    image_router,
    permission_router,
    petition_router,
    role_router,
    settings_router,
    stats_router,
    tag_router,
    user_router,
)
from pawprints.api.service.image_service import ImageService
from pawprints.database.media import ensure_bucket_exists, get_s3_client
from pawprints.database.session import get_async_db_session, sessioncontroller
from pawprints.exceptions import ServiceError
from pawprints.exceptions.error_responses import ErrorDetail, ErrorResponse
from pawprints.logger import get_logger, setup_logging
from pawprints.middleware.activity import ActivityTrackingMiddleware
from pawprints.models.orm import Base

security = HTTPBearer()
config = Config()


async def gc_cronjob():

    tz = ZoneInfo("America/New_York")
    while True:
        try:
            async for session in get_async_db_session():
                s3_client = next(get_s3_client())
                log = get_logger()

                image_service = ImageService(session=session, s3_client=s3_client, logger=log)
                await image_service.run_garbage_collection()

                break

        except Exception as e:
            logger.error("Background GC failed: %s", e)

        now = datetime.now(tz)
        # Target cronjob for 3:00 AM EST
        target = now.replace(hour=3, minute=0, second=0, microsecond=0)

        # If it's already past 3:00 AM today, set the target to 3:00 AM tomorrow
        if now >= target:
            target += timedelta(days=1)

        # seconds until the target time
        sleep_seconds = (target - now).total_seconds()
        await asyncio.sleep(sleep_seconds)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()

    root_logger = logging.getLogger("pawprints")
    root_logger.info("Logging configured successfully via dictConfig.")
    ensure_bucket_exists("images")

    # In DEV mode: auto-create all tables (including stats_* and new columns)
    # so a fresh local DB needs no manual SQL.
    if config.MODE == "DEV":
        root_logger.info("DEV mode: running create_all to ensure all tables exist...")
        async with sessioncontroller._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        root_logger.info("DEV mode: table creation complete.")

    yield

    if sessioncontroller._engine is not None:
        root_logger.info("Closing database connection...")
        await sessioncontroller.close()


if config.MODE == "PROD":
    app = FastAPI(
        lifespan=lifespan,
        title="Pawprints API",
        doc_url=None,
        redoc_url=None,
        openapi_url=None,
    )
else:
    app = FastAPI(
        lifespan=lifespan,
        title="Pawprints API",
        doc_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

# -----------------------------
# Exception Handlers (standard)
# -----------------------------


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Spec: 3000 - Invalid Request Body (HTTP 400)
    payload = ErrorResponse(
        detail=ErrorDetail(
            code="3000",
            message="The request body is malformed or invalid.",
            context={"errors": exc.errors()},
        )
    ).model_dump()
    return JSONResponse(status_code=400, content=payload)


@app.exception_handler(ServiceError)
async def service_error_exception_handler(request: Request, exc: ServiceError):
    # Support both .message and .detail (depending on your base class)
    msg = getattr(exc, "message", None) or getattr(exc, "detail", "")
    ctx = getattr(exc, "context", None)
    code = str(getattr(exc, "code", "1000"))
    payload = ErrorResponse(detail=ErrorDetail(code=code, message=msg, context=ctx)).model_dump()
    return JSONResponse(status_code=getattr(exc, "status_code", 500), content=payload)


# Optional but recommended: a catch-all to keep responses consistent
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Spec: 1000 - Internal Server Error (HTTP 500)
    # Avoid leaking internals; log the error and return standardized payload.
    payload = ErrorResponse(
        detail=ErrorDetail(
            code="1000",
            message="An unexpected error occurred on the server.",
            context=None,
        )
    ).model_dump()
    return JSONResponse(status_code=500, content=payload)


# -------------
# Middleware
# -------------
if config.MODE == "DEV":
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ]
else:
    allowed_origins = [
        "https://pawprints.rit.edu",
        "https://pawprints2.rit.edu",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Track per-request activity for stats (must come after CORS)
app.add_middleware(ActivityTrackingMiddleware)

###################
# Logger
###################

logger = logging.getLogger("pawprints.main")
logger.info("API is starting up")

if config.MODE == "PROD":
    app.add_middleware(
        SessionMiddleware,
        secret_key=os.getenv("SESSION_SECRET"),
        session_cookie="pawprints_session",
        https_only=True,
        max_age=86400,
    )
else:
    logger.warning("Running in %s mode: SessionMiddleware is DISABLED", config.MODE)

# -------------
# Routers
# -------------
app.include_router(auth_router, prefix="/saml2")
# app.include_router(general_router, prefix="/api/v1/general")
app.include_router(user_router, prefix="/api/v1/users")
app.include_router(permission_router, prefix="/api/v1/permissions")
app.include_router(role_router, prefix="/api/v1/roles")
app.include_router(committee_router, prefix="/api/v1/committees")
app.include_router(petition_router, prefix="/api/v1/petitions")
app.include_router(image_router, prefix="/api/v1/images")
app.include_router(tag_router, prefix="/api/v1/tags")
app.include_router(stats_router, prefix="/api/v1/stats")
app.include_router(settings_router, prefix="/api/v1/settings")
app.include_router(
    admin_petition_router, prefix="/api/v1/admin/petitions"
)  # Admin endpoints for petition management


@app.get("/")
async def root():
    logger.info("API is running")
    return {"message": "Hello World"}


@app.get("/health")
async def health():
    return {"status": "ok"}
