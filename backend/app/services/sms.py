import json
import logging
import secrets
from dataclasses import dataclass

from alibabacloud_dypnsapi20170525.client import Client
from alibabacloud_dypnsapi20170525.models import SendSmsVerifyCodeRequest
from alibabacloud_tea_openapi.exceptions._client import ClientException
from alibabacloud_tea_openapi.models import Config
from redis.asyncio import Redis

from app.config import get_settings

_sms_client: Client | None = None
logger = logging.getLogger(__name__)


class SmsConfigurationError(RuntimeError):
    """Raised when the selected SMS backend is not safely configured."""


class SmsRateLimitError(ValueError):
    """Raised when a phone number is still inside the SMS cooldown window."""


@dataclass(frozen=True)
class SmsDispatchResult:
    code: str
    is_development: bool = False


def _validate_aliyun_settings(scene: str) -> None:
    settings = get_settings()
    required = {
        "SMS_ACCESS_KEY_ID": settings.sms_access_key_id,
        "SMS_ACCESS_KEY_SECRET": settings.sms_access_key_secret,
        "SMS_SIGN_NAME": settings.sms_sign_name,
        "SMS_TEMPLATE_CODE": _get_template_code(scene),
    }
    if any(not value for value in required.values()):
        raise SmsConfigurationError("短信服务尚未配置，请联系管理员完善短信服务配置")


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


async def send_sms_code(redis: Redis, phone: str, scene: str) -> SmsDispatchResult:
    settings = get_settings()

    cooldown_key = f"sms_cooldown:{phone}"
    if await redis.exists(cooldown_key):
        raise SmsRateLimitError("发送过于频繁，请稍后再试")

    code_key = f"sms_code:{scene}:{phone}"

    if settings.sms_backend == "console":
        if settings.app_env != "development":
            raise SmsConfigurationError("本地验证码模式仅允许在开发环境使用")

        code = f"{secrets.randbelow(1_000_000):06d}"
        await redis.set(code_key, code, ex=settings.sms_code_expire_minutes * 60)
        await redis.set(cooldown_key, "1", ex=settings.sms_code_cooldown_seconds)
        logger.warning("Development SMS code generated for %s (%s): %s", phone, scene, code)
        return SmsDispatchResult(code=code, is_development=True)

    _validate_aliyun_settings(scene)
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
    await redis.set(code_key, code, ex=settings.sms_code_expire_minutes * 60)
    await redis.set(cooldown_key, "1", ex=settings.sms_code_cooldown_seconds)

    return SmsDispatchResult(code=code)


async def verify_sms_code(redis: Redis, phone: str, scene: str, code: str) -> bool:
    code_key = f"sms_code:{scene}:{phone}"
    stored = await redis.get(code_key)
    if stored and stored == code:
        await redis.delete(code_key)
        return True
    return False
