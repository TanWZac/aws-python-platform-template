from fastapi import APIRouter

from platform_service.core.config import settings

router = APIRouter()


@router.get("/live")
async def live() -> dict[str, str]:
    return {"status": "live"}


@router.get("/ready")
async def ready() -> dict[str, str]:
    # Extend this with checks for database, vector store, queues, or external services.
    return {
        "status": "ready",
        "app": settings.app_name,
        "environment": settings.app_env,
        "version": settings.app_version,
    }
