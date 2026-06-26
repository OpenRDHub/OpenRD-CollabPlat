import json

from alibabacloud_dypnsapi20170525.client import Client
from alibabacloud_dypnsapi20170525.models import SendSmsVerifyCodeRequest
from alibabacloud_tea_openapi.models import Config
from alibabacloud_tea_openapi.exceptions._client import ClientException
from redis.asyncio import Redis

from app.config import get_settings

_sms_client: Client | None = None


def _get_sms_client() -> Client:
    global _sms_client
    if _sms_client is None:
        settings = get_settings()
        config = Config(
            access_key_id=settings.sms_access_key_id,
            access_key_secret=settings.sms_access_key_secret,
            endpoint="dypnsapi.aliyuncs.com",
        )
        _sms_client = Client(config)
    return _sms_client


def _get_template_code(scene: str) -> str:
    settings = get_settings()
    if scene == "register":
        return settings.sms_template_register
    elif scene == "reset_password":
        return settings.sms_template_reset_password
    return settings.sms_template_register


async def send_sms_code(redis: Redis, phone: str, scene: str) -> str:
    settings = get_settings()

    cooldown_key = f"sms_cooldown:{phone}"
    if await redis.exists(cooldown_key):
        raise ValueError("发送过于频繁，请稍后再试")

    client = _get_sms_client()
    request = SendSmsVerifyCodeRequest(
        phone_number=phone,
        sign_name=settings.sms_sign_name,
        template_code=_get_template_code(scene),
        template_param=json.dumps({"code": "##code##", "min": str(settings.sms_code_expire_minutes)}),
        code_length=6,
        code_type=1,
        valid_time=settings.sms_code_expire_minutes * 60,
        interval=settings.sms_code_cooldown_seconds,
        return_verify_code=True,
        duplicate_policy=1,
    )

    try:
        response = client.send_sms_verify_code(request)
    except ClientException as e:
        raise ValueError(f"短信服务异常: {e}") from e
    except Exception as e:
        raise ValueError(f"短信发送失败: {e}") from e

    if response.body.code != "OK":
        raise ValueError(f"短信发送失败: {response.body.message}")

    code = response.body.model.verify_code

    # 存入 Redis 用于我们自己的校验
    code_key = f"sms_code:{scene}:{phone}"
    await redis.set(code_key, code, ex=settings.sms_code_expire_minutes * 60)
    await redis.set(cooldown_key, "1", ex=settings.sms_code_cooldown_seconds)

    return code


async def verify_sms_code(redis: Redis, phone: str, scene: str, code: str) -> bool:
    code_key = f"sms_code:{scene}:{phone}"
    stored = await redis.get(code_key)
    if stored and stored == code:
        await redis.delete(code_key)
        return True
    return False
