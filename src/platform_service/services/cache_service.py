from platform_service.core.cache import redis_client
from platform_service.core.config import settings


class CacheService:
    def __init__(self, default_ttl_seconds: int | None = None) -> None:
        self.default_ttl_seconds = default_ttl_seconds or settings.cache_default_ttl_seconds

    async def get_text(self, key: str) -> str | None:
        return await redis_client.get(key)

    async def set_text(self, key: str, value: str, ttl_seconds: int | None = None) -> None:
        await redis_client.set(key, value, ex=ttl_seconds or self.default_ttl_seconds)

    async def delete(self, key: str) -> None:
        await redis_client.delete(key)

    async def ping(self) -> bool:
        return bool(await redis_client.ping())
