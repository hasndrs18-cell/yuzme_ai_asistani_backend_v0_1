"""Application-scoped Redis connection pool lifecycle."""

from __future__ import annotations

import logging
from typing import Any

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_redis_pool: Any | None = None
_redis_client: Any | None = None


def get_redis_client() -> Any | None:
    """Return the initialized shared Redis client, if Redis is available."""
    return _redis_client


async def init_redis_pool() -> Any | None:
    """Initialize and validate the application-wide Redis connection pool.

    Redis is optional for tests and local development. Connection failures are
    logged and converted to a ``None`` result so callers can use their fallback.
    """
    global _redis_pool, _redis_client

    if _redis_client is not None:
        return _redis_client

    settings = get_settings()
    if settings.environment.lower() in {"test", "testing"}:
        return None

    try:
        import redis.asyncio as aioredis

        _redis_pool = aioredis.ConnectionPool.from_url(
            settings.redis_url,
            max_connections=settings.db_pool_max_size,
            decode_responses=True,
        )
        _redis_client = aioredis.Redis(connection_pool=_redis_pool)
        await _redis_client.ping()
        logger.info("Redis connection pool initialized.")
        return _redis_client
    except Exception as exc:
        logger.warning("Redis pool initialization failed; using fallback: %s", exc)
        await close_redis_pool()
        return None


async def close_redis_pool() -> None:
    """Close the shared Redis client and disconnect all pooled connections."""
    global _redis_pool, _redis_client

    client, pool = _redis_client, _redis_pool
    _redis_client = None
    _redis_pool = None

    if client is not None:
        try:
            await client.aclose()
        except Exception as exc:
            logger.warning("Redis client shutdown failed: %s", exc)

    if pool is not None:
        try:
            await pool.disconnect()
        except Exception as exc:
            logger.warning("Redis pool shutdown failed: %s", exc)
