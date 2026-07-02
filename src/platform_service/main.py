from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from platform_service.api.routes.health import router as health_router
from platform_service.api.routes.v1.example import router as example_router
from platform_service.core.config import settings
from platform_service.core.errors import AppError
from platform_service.core.logging import configure_logging, get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(settings.log_level)
    logger.info(
        "Starting application",
        extra={
            "app_name": settings.app_name,
            "environment": settings.app_env,
            "version": settings.app_version,
        },
    )
    yield
    logger.info("Stopping application")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs" if settings.enable_docs else None,
    redoc_url="/redoc" if settings.enable_docs else None,
    lifespan=lifespan,
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
app.include_router(example_router, prefix="/api/v1/example", tags=["example"])
