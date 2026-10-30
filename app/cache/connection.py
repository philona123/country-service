import logging

from redis.asyncio import Redis

from app.config import settings

logger = logging.getLogger(__name__)

_redis: Redis | None = None


def get_redis() -> Redis | None:
    return _redis


def is_cache_available() -> bool:
    return settings.CACHE_ENABLED and _redis is not None


async def connect_to_redis() -> None:
    global _redis

    if not settings.CACHE_ENABLED:
        logger.info("Country cache disabled (CACHE_ENABLED=false)")
        return

    client = Redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
    )
    try:
        await client.ping()
    except Exception as error:
        await client.aclose()
        logger.warning("Redis unavailable; caching disabled: %s", error)
        return

    _redis = client
    logger.info("Connected to Redis")


async def close_redis_connection() -> None:
    global _redis
    if _redis is not None:
        await _redis.aclose()
        _redis = None
        logger.info("Disconnected from Redis")
