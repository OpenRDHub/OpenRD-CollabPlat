from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.dependencies.redis import get_redis
from app.services.admin import get_effective_permissions
from app.utils.security import decode_token

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    redis: Redis = Depends(get_redis),
) -> dict:
    payload = decode_token(credentials.credentials)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的 Token")

    jti = payload.get("jti")
    if jti and await redis.exists(f"blacklist:{jti}"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token 已吊销")

    return {"user_id": payload["sub"], "role": payload.get("role", "requester"), "jti": jti}


def require_roles(*roles: str) -> Callable:
    async def checker(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user["role"] not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
        return current_user
    return checker


def require_permissions(*permissions: str) -> Callable:
    async def checker(
        current_user: dict = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> dict:
        # 最终权限 = 角色模板权限 ∪ 数据库手动权限，手动授权后立即生效
        effective = await get_effective_permissions(db, current_user["user_id"], current_user["role"])
        for perm in permissions:
            if perm not in effective:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"缺少权限: {perm}")
        return current_user
    return checker
