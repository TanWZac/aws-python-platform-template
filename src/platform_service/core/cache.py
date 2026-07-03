from redis.asyncio import Redis

from platform_service.core.config import settings


def create_redis_client() -> Redis:
    return Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        ssl=settings.redis_ssl,
        socket_timeout=settings.redis_timeout_seconds,
        decode_responses=True,
    )


redis_client = create_redis_client()


async def close_redis_client() -> None:
    await redis_client.aclose()
