"""
Redis connection pool and helper utilities.
Used for caching (market quotes, tokens), PubSub (market feed relay),
and rate limiting.
"""

import redis.asyncio as aioredis
from typing import Optional, Any
import json

from app.core.config import get_settings

settings = get_settings()

# ── Connection Pool ──────────────────────────────────────────────────────
redis_pool: Optional[aioredis.Redis] = None


async def init_redis() -> aioredis.Redis:
    """Initialize Redis connection pool. Called during app startup and Celery tasks."""
    global redis_pool
    
    # If already initialized, verify the loop is still open
    if redis_pool is not None:
        try:
            await redis_pool.ping()
            return redis_pool
        except RuntimeError:
            # Event loop is likely closed, need to re-initialize
            logger.warning("init_redis :: Existing Redis pool tied to a closed loop. Re-initializing...")
            redis_pool = None

    redis_pool = aioredis.from_url(
        settings.REDIS_URL,
        max_connections=settings.REDIS_MAX_CONNECTIONS,
        decode_responses=True,
        encoding="utf-8",
    )
    # Verify connection
    await redis_pool.ping()
    return redis_pool


async def close_redis() -> None:
    """Close Redis connection pool. Called during app shutdown."""
    global redis_pool
    if redis_pool:
        try:
            await redis_pool.close()
        except Exception as e:
            logger.error(f"close_redis :: Error closing Redis: {e}")
        finally:
            redis_pool = None


def get_redis() -> aioredis.Redis:
    """Get the active Redis client. Raises if not initialized."""
    if redis_pool is None:
        raise RuntimeError("Redis not initialized. Call init_redis() first.")
    return redis_pool


# ── Cache Helpers ────────────────────────────────────────────────────────

async def cache_set(key: str, value: Any, ttl_seconds: int = 60) -> None:
    """Set a JSON-serializable value in Redis with TTL."""
    client = get_redis()
    await client.setex(key, ttl_seconds, json.dumps(value))


async def cache_get(key: str) -> Optional[Any]:
    """Get a cached value from Redis, returns None if not found."""
    client = get_redis()
    data = await client.get(key)
    if data:
        return json.loads(data)
    return None


async def cache_delete(key: str) -> None:
    """Delete a key from Redis cache."""
    client = get_redis()
    await client.delete(key)


# ── PubSub Helpers ───────────────────────────────────────────────────────

def get_pubsub() -> aioredis.client.PubSub:
    """Create a new PubSub instance for subscribing to channels."""
    client = get_redis()
    return client.pubsub()


async def publish(channel: str, message: Any) -> None:
    """Publish a JSON-serializable message to a Redis PubSub channel."""
    client = get_redis()
    await client.publish(channel, json.dumps(message))
