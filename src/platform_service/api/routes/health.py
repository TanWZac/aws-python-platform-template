from typing import Any

from fastapi import APIRouter, Request, Response, status

from platform_service.core.config import settings
from platform_service.core.readiness import evaluate_readiness

router = APIRouter()


@router.get("/live")
async def live() -> dict[str, str]:
    return {"status": "live"}


@router.get("/ready")
async def ready(request: Request, response: Response) -> dict[str, Any]:
    if getattr(request.app.state, "is_shutting_down", False):
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "not_ready",
            "app": settings.app_name,
            "environment": settings.app_env,
            "version": settings.app_version,
            "dependencies": [],
        }

    readiness_report = await evaluate_readiness(
        dependency_urls=settings.readiness_check_urls_list,
        timeout_seconds=settings.readiness_timeout_seconds,
    )

    if readiness_report["status"] != "ready":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": readiness_report["status"],
        "app": settings.app_name,
        "environment": settings.app_env,
        "version": settings.app_version,
        "dependencies": readiness_report["dependencies"],
    }
