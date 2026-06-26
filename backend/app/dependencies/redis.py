from redis.asyncio import Redis

from app.utils.redis import get_redis_client


async def get_redis() -> Redis:
    return get_redis_client()
