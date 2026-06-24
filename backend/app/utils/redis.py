from redis.asyncio import Redis

from app.config import get_settings

_redis: Redis | None = None


async def init_redis() -> Redis:
    global _redis
    settings = get_settings()

    if settings.app_env == "development":
        try:
            r = Redis.from_url(settings.redis_url, decode_responses=True)
            await r.ping()
            _redis = r
        except Exception:
            from fakeredis import aioredis as fakeredis_aio
            _redis = fakeredis_aio.FakeRedis(decode_responses=True)
            print("[Redis] 无法连接真实 Redis，已降级为内存模式（fakeredis）")
    else:
        _redis = Redis.from_url(settings.redis_url, decode_responses=True)

    return _redis


async def close_redis() -> None:
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None


def get_redis_client() -> Redis:
    if _redis is None:
        raise RuntimeError("Redis not initialized. Call init_redis() first.")
    return _redis
