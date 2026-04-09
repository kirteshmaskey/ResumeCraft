"""
Redis-based sliding-window rate limiter for Upstox API calls.
Enforces per-user, per-category limits:
  - 50 requests/second
  - 500 requests/minute
  - 2,000 requests/30 minutes
"""

import time
from uuid import uuid4

from app.core.redis import get_redis
from app.core.config import get_settings

settings = get_settings()

# ── Rate Limit Windows ───────────────────────────────────────────────────
RATE_LIMITS = {
    "standard": {
        "per_second": {"limit": settings.RATE_LIMIT_PER_SECOND, "window": 1},
        "per_minute": {"limit": settings.RATE_LIMIT_PER_MINUTE, "window": 60},
        "per_30_min": {"limit": settings.RATE_LIMIT_PER_30_MIN, "window": 1800},
    },
    "multi_order": {
        "per_second": {"limit": 4, "window": 1},
        "per_minute": {"limit": 40, "window": 60},
        "per_30_min": {"limit": 160, "window": 1800},
    },
}


class RateLimitExceeded(Exception):
    """Raised when a rate limit is exceeded."""

    def __init__(self, category: str, window: str, retry_after: float):
        self.category = category
        self.window = window
        self.retry_after = retry_after
        super().__init__(
            f"Rate limit exceeded for '{category}' ({window}). "
            f"Retry after {retry_after:.1f}s"
        )


async def check_rate_limit(
    user_id: str,
    category: str = "standard",
) -> bool:
    """
    Check if the request is within rate limits using Redis sorted sets.
    Uses sliding-window counter pattern.

    Args:
        user_id: Upstox user ID for per-user limiting.
        category: 'standard' or 'multi_order'.

    Returns:
        True if within limits.

    Raises:
        RateLimitExceeded: If any window limit is breached.
    """
    redis = get_redis()
    now = time.time()
    limits = RATE_LIMITS.get(category, RATE_LIMITS["standard"])

    for window_name, config in limits.items():
        key = f"rate:{user_id}:{category}:{window_name}"
        window_seconds = config["window"]
        limit = config["limit"]

        pipe = redis.pipeline()
        # Remove entries outside the current window
        pipe.zremrangebyscore(key, 0, now - window_seconds)
        # Count remaining entries
        pipe.zcard(key)
        # Add current request
        pipe.zadd(key, {str(uuid4()): now})
        # Set key expiry to window size (cleanup)
        pipe.expire(key, window_seconds + 1)

        results = await pipe.execute()
        current_count = results[1]

        if current_count >= limit:
            raise RateLimitExceeded(
                category=category,
                window=window_name,
                retry_after=window_seconds - (now % window_seconds),
            )

    return True


async def get_rate_limit_status(
    user_id: str,
    category: str = "standard",
) -> dict:
    """
    Get current rate limit usage for a user.

    Returns:
        Dict with usage counts per window.
    """
    redis = get_redis()
    now = time.time()
    limits = RATE_LIMITS.get(category, RATE_LIMITS["standard"])
    status = {}

    for window_name, config in limits.items():
        key = f"rate:{user_id}:{category}:{window_name}"
        # Clean expired entries
        await redis.zremrangebyscore(key, 0, now - config["window"])
        count = await redis.zcard(key)
        status[window_name] = {
            "used": count,
            "limit": config["limit"],
            "remaining": max(0, config["limit"] - count),
        }

    return status
