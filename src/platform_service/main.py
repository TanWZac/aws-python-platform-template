from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from platform_service.api.routes.health import router as health_router
from platform_service.api.routes.v1.cache import router as cache_router
from platform_service.api.routes.v1.example import router as example_router
from platform_service.core.auth import require_api_key
from platform_service.core.cache import close_redis_client
from platform_service.core.config import settings
from platform_service.core.errors import AppError
from platform_service.core.logging import configure_logging, get_logger
from platform_service.core.middleware import (
    CorrelationIdMiddleware,
    SecurityHeadersMiddleware,
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(settings.log_level)
    app.state.is_shutting_down = False
    logger.info(
        "Starting application",
        extra={
            "app_name": settings.app_name,
            "environment": settings.app_env,
            "version": settings.app_version,
        },
    )

    if settings.authentication_enabled and not settings.api_keys_set:
        logger.warning(
            "Authentication is enabled but API_KEYS is empty; protected endpoints will reject all requests"
        )

    yield
    app.state.is_shutting_down = True
    await close_redis_client()
    logger.info("Stopping application")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs" if settings.docs_enabled else None,
    redoc_url="/redoc" if settings.docs_enabled else None,
    lifespan=lifespan,
)

app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

if settings.cors_allow_origins_list:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins_list,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-API-Key", "X-Request-ID"],
    )


@app.exception_handler(AppError)
async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
            }
        },
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        "Unhandled application error",
        extra={
            "path": request.url.path,
            "method": request.method,
        },
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "internal_server_error",
                "message": "An unexpected error occurred.",
            }
        },
    )


app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(
    example_router,
    prefix="/api/v1/example",
    tags=["example"],
    dependencies=[Depends(require_api_key)],
)
app.include_router(
    cache_router,
    prefix="/api/v1/cache",
    tags=["cache"],
    dependencies=[Depends(require_api_key)],
)
