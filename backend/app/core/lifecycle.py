"""
Helper to initialize internal clients (Redis, Upstox) for background tasks.
"""

from app.core.redis import init_redis, close_redis
from app.core.upstox_client import upstox_client
from app.core.logging import get_logger

logger = get_logger("lifecycle")

async def init_app_clients():
    """Initialize Redis and Upstox clients if they aren't already."""
    await init_redis()
    await upstox_client.init()
    logger.debug("init_app_clients :: Redis and Upstox initialized")

async def close_app_clients():
    """Close and reset Redis and Upstox clients."""
    await upstox_client.close()
    await close_redis()
    logger.debug("close_app_clients :: Redis and Upstox closed and reset")
