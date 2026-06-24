import random
import string

from redis.asyncio import Redis

from app.config import get_settings


def _generate_code(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))


async def send_sms_code(redis: Redis, phone: str, scene: str) -> str:
    settings = get_settings()

    cooldown_key = f"sms_cooldown:{phone}"
    if await redis.exists(cooldown_key):
        raise ValueError("发送过于频繁，请稍后再试")

    code = _generate_code()
    code_key = f"sms_code:{scene}:{phone}"
    await redis.set(code_key, code, ex=settings.sms_code_expire_minutes * 60)
    await redis.set(cooldown_key, "1", ex=settings.sms_code_cooldown_seconds)

    # stub: 打印到控制台，后续对接阿里云 Dysms
    print(f"[SMS STUB] phone={phone}, scene={scene}, code={code}")
    return code


async def verify_sms_code(redis: Redis, phone: str, scene: str, code: str) -> bool:
    code_key = f"sms_code:{scene}:{phone}"
    stored = await redis.get(code_key)
    if stored and stored == code:
        await redis.delete(code_key)
        return True
    return False
