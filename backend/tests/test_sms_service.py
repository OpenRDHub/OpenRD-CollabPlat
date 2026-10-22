from types import SimpleNamespace

import pytest

from app.services import sms as sms_service


def _settings(*, app_env: str = "development", sms_backend: str = "console"):
    return SimpleNamespace(
        app_env=app_env,
        sms_backend=sms_backend,
        sms_code_expire_minutes=5,
        sms_code_cooldown_seconds=60,
        sms_access_key_id="",
        sms_access_key_secret="",
        sms_sign_name="",
        sms_template_register="",
        sms_template_reset_password="",
    )


@pytest.mark.asyncio
async def test_console_backend_generates_and_stores_one_time_code(fake_redis, monkeypatch):
    monkeypatch.setattr(sms_service, "get_settings", lambda: _settings())

    result = await sms_service.send_sms_code(
        fake_redis, "13800138001", "reset_password"
    )

    assert result.is_development is True
    assert len(result.code) == 6
    assert result.code.isdigit()
    assert await fake_redis.get("sms_code:reset_password:13800138001") == result.code
    assert await fake_redis.exists("sms_cooldown:13800138001")


@pytest.mark.asyncio
async def test_console_backend_keeps_cooldown_protection(fake_redis, monkeypatch):
    monkeypatch.setattr(sms_service, "get_settings", lambda: _settings())
    await sms_service.send_sms_code(fake_redis, "13800138001", "register")

    with pytest.raises(sms_service.SmsRateLimitError, match="发送过于频繁"):
        await sms_service.send_sms_code(fake_redis, "13800138001", "register")


@pytest.mark.asyncio
async def test_console_backend_is_rejected_outside_development(fake_redis, monkeypatch):
    monkeypatch.setattr(
        sms_service,
        "get_settings",
        lambda: _settings(app_env="production"),
    )

    with pytest.raises(sms_service.SmsConfigurationError, match="仅允许在开发环境"):
        await sms_service.send_sms_code(fake_redis, "13800138001", "register")


@pytest.mark.asyncio
async def test_aliyun_backend_requires_configuration(fake_redis, monkeypatch):
    monkeypatch.setattr(
        sms_service,
        "get_settings",
        lambda: _settings(sms_backend="aliyun"),
    )

    with pytest.raises(sms_service.SmsConfigurationError, match="尚未配置"):
        await sms_service.send_sms_code(fake_redis, "13800138001", "register")
