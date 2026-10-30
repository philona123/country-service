import logging
from typing import Any

from app.cache.connection import get_redis, is_cache_available
from app.cache.serialization import (
    country_document_from_json,
    country_document_to_json,
    missing_country_json,
)
from app.config import settings

logger = logging.getLogger(__name__)


class CacheMiss:
    """Returned when the key is not present in Redis."""


CACHE_MISS = CacheMiss()

QUERY_CACHE_VERSION_KEY = "country:cache:query_version"


def _code_key(code: str) -> str:
    return f"country:code:{code.upper()}"


def _id_key(country_id: str) -> str:
    return f"country:id:{country_id}"


async def _get(key: str) -> dict | None | CacheMiss:
    redis = get_redis()
    if not is_cache_available() or redis is None:
        return CACHE_MISS

    try:
        payload = await redis.get(key)
    except Exception as error:
        logger.warning("Redis GET failed for %s: %s", key, error)
        return CACHE_MISS

    if payload is None:
        return CACHE_MISS

    return country_document_from_json(payload)


async def _set(key: str, payload: str, ttl: int) -> None:
    redis = get_redis()
    if not is_cache_available() or redis is None:
        return

    try:
        await redis.set(key, payload, ex=ttl)
    except Exception as error:
        logger.warning("Redis SET failed for %s: %s", key, error)


async def get_by_code(code: str) -> dict | None | CacheMiss:
    return await _get(_code_key(code))


async def get_by_id(country_id: str) -> dict | None | CacheMiss:
    return await _get(_id_key(country_id))


async def put(country: dict | None, *, code: str | None = None, country_id: str | None = None) -> None:
    if country is None:
        ttl = settings.CACHE_NEGATIVE_TTL_SECONDS
        payload = missing_country_json()
        if code:
            await _set(_code_key(code), payload, ttl)
        if country_id:
            await _set(_id_key(country_id), payload, ttl)
        return

    ttl = settings.CACHE_TTL_SECONDS
    payload = country_document_to_json(country)
    await _set(_code_key(country["code"]), payload, ttl)
    await _set(_id_key(str(country["_id"])), payload, ttl)


async def invalidate_all_country_entities() -> None:
    redis = get_redis()
    if not is_cache_available() or redis is None:
        return

    try:
        async for key in redis.scan_iter(match="country:code:*"):
            await redis.delete(key)
        async for key in redis.scan_iter(match="country:id:*"):
            await redis.delete(key)
        await redis.incr(QUERY_CACHE_VERSION_KEY)
    except Exception as error:
        logger.warning("Redis cache invalidation failed: %s", error)


def is_cache_miss(value: Any) -> bool:
    return isinstance(value, CacheMiss)
