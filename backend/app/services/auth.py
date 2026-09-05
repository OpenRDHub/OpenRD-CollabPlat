import re

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.services import sms as sms_service
from app.services import user as user_service
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)

_PHONE_RE = re.compile(r"^1[3-9]\d{9}$")


async def register(
    db: AsyncSession, redis: Redis, *, username: str, phone: str, password: str, sms_code: str, nickname: str | None = None
) -> dict:
    if not await sms_service.verify_sms_code(redis, phone, "register", sms_code):
        raise ValueError("验证码无效或已过期")
    if await user_service.get_user_by_username(db, username):
        raise ValueError("用户名已存在")
    if await user_service.get_user_by_phone(db, phone):
        raise ValueError("手机号已注册")

    user = await user_service.create_user(db, username=username, phone=phone, password=password, nickname=nickname)
    access_token = create_access_token(user.id, user.role)
    refresh_token, jti = create_refresh_token(user.id)

    settings = get_settings()
    await redis.set(
        f"refresh:{user.id}:{jti}", "1", ex=settings.refresh_token_expire_days * 86400
    )
    return {"user": user, "access_token": access_token, "refresh_token": refresh_token}


async def _revoke_refresh_sessions(redis: Redis, user_id: str) -> None:
    async for key in redis.scan_iter(f"refresh:{user_id}:*"):
        await redis.delete(key)


async def _replace_session_after_onboarding(
    redis: Redis,
    *,
    user_id: str,
    refresh_jti: str,
    access_jti: str | None,
) -> None:
    settings = get_settings()
    refresh_keys = [
        key async for key in redis.scan_iter(f"refresh:{user_id}:*")
    ]
    pipeline = redis.pipeline(transaction=True)
    if refresh_keys:
        pipeline.delete(*refresh_keys)
    pipeline.set(
        f"refresh:{user_id}:{refresh_jti}",
        "1",
        ex=settings.refresh_token_expire_days * 86400,
    )
    if access_jti:
        pipeline.set(
            f"blacklist:{access_jti}",
            "1",
            ex=settings.access_token_expire_minutes * 60,
        )
    await pipeline.execute()


async def refresh(
    db: AsyncSession, redis: Redis, *, refresh_token_str: str
) -> dict:
    payload = decode_token(refresh_token_str)
    if not payload or payload.get("type") != "refresh":
        raise ValueError("无效的 refresh token")

    user_id = payload.get("sub")
    jti = payload.get("jti")
    if not user_id or not jti:
        raise ValueError("无效的 refresh token")

    key = f"refresh:{user_id}:{jti}"

    # Atomically consume the old session so concurrent refresh attempts cannot
    # both mint a new token pair.
    if not await redis.getdel(key):
        await _revoke_refresh_sessions(redis, user_id)
        raise ValueError("Token 已被吊销（疑似重放攻击）")

    user = await user_service.get_user_by_id(db, user_id)
    if not user:
        await _revoke_refresh_sessions(redis, user_id)
        raise ValueError("用户不存在")
    if user.is_locked:
        await _revoke_refresh_sessions(redis, user_id)
        raise ValueError("账号已被锁定")

    settings = get_settings()
    access_token = create_access_token(user.id, user.role)
    new_refresh, new_jti = create_refresh_token(user_id)
    await redis.set(
        f"refresh:{user_id}:{new_jti}", "1", ex=settings.refresh_token_expire_days * 86400
    )
    return {"access_token": access_token, "refresh_token": new_refresh}


async def logout(redis: Redis, *, refresh_token_str: str, access_jti: str | None = None) -> None:
    payload = decode_token(refresh_token_str)
    if payload and payload.get("type") == "refresh":
        user_id = payload["sub"]
        jti = payload["jti"]
        await redis.delete(f"refresh:{user_id}:{jti}")

    if access_jti:
        settings = get_settings()
        await redis.set(
            f"blacklist:{access_jti}", "1", ex=settings.access_token_expire_minutes * 60
        )


async def reset_password(
    db: AsyncSession, redis: Redis, *, phone: str, sms_code: str, new_password: str
) -> None:
    if not await sms_service.verify_sms_code(redis, phone, "reset_password", sms_code):
        raise ValueError("验证码无效或已过期")

    user = await user_service.get_user_by_phone(db, phone)
    if not user:
        raise ValueError("该手机号未注册")

    user.password_hash = hash_password(new_password)
    await db.commit()


async def onboarding(
    db: AsyncSession,
    redis: Redis,
    *,
    user_id: str,
    access_jti: str | None,
    role: str,
    nickname: str | None = None,
    province: str | None = None,
    occupation: str | None = None,
    bio: str | None = None,
    tags: list[str] | None = None,
) -> dict:
    user = await user_service.get_user_by_id(db, user_id)
    if not user:
        raise ValueError("用户不存在")
    if user.is_locked:
        raise ValueError("账号已被锁定")
    if user.is_onboarded:
        raise ValueError("已完成初始化，不可重复操作")

    if nickname:
        user.nickname = nickname
    user.role = role
    user.province = province
    user.occupation = occupation
    user.bio = bio
    user.tags = ",".join(tags) if tags else None
    user.is_onboarded = 1
    await db.commit()

    access_token = create_access_token(user.id, user.role)
    refresh_token, refresh_jti = create_refresh_token(user.id)
    await _replace_session_after_onboarding(
        redis,
        user_id=user.id,
        refresh_jti=refresh_jti,
        access_jti=access_jti,
    )
    return {"access_token": access_token, "refresh_token": refresh_token}


async def login(db: AsyncSession, redis: Redis, *, username: str, password: str) -> dict:
    if _PHONE_RE.match(username):
        user = await user_service.get_user_by_phone(db, username)
    else:
        user = await user_service.get_user_by_username(db, username)
    if not user or not verify_password(password, user.password_hash):
        raise ValueError("账号或密码错误")
    if user.is_locked:
        raise ValueError("账号已被锁定")

    access_token = create_access_token(user.id, user.role)
    refresh_token, jti = create_refresh_token(user.id)

    settings = get_settings()
    await redis.set(
        f"refresh:{user.id}:{jti}", "1", ex=settings.refresh_token_expire_days * 86400
    )
    return {"user": user, "access_token": access_token, "refresh_token": refresh_token}
