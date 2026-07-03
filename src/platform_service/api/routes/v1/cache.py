from fastapi import APIRouter

from platform_service.services.cache_service import CacheService

router = APIRouter()


@router.get("/ping")
async def cache_ping() -> dict[str, bool]:
    cache = CacheService()
    return {"ok": await cache.ping()}


@router.get("/example")
async def cache_example() -> dict[str, str]:
    cache = CacheService()
    key = "example:greeting"
    cached_value = await cache.get_text(key)

    if cached_value is not None:
        return {"source": "redis", "message": cached_value}

    value = "Hello from Redis cache"
    await cache.set_text(key, value)
    return {"source": "application", "message": value}
