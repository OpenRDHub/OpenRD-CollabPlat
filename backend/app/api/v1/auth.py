from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.dependencies.redis import get_redis
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    OnboardingRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    SmsCodeRequest,
    TokenResponse,
    UserOut,
)
from app.schemas.common import ApiResponse
from app.services import auth as auth_service
from app.services import sms as sms_service

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=ApiResponse)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)):
    try:
        result = await auth_service.register(
            db, redis, username=body.username, phone=body.phone,
            password=body.password, sms_code=body.sms_code,
            nickname=body.nickname,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return ApiResponse(data={
        "user": UserOut.model_validate(result["user"]).model_dump(),
        "access_token": result["access_token"],
        "refresh_token": result["refresh_token"],
        "token_type": "bearer",
    })


@router.post("/login", response_model=ApiResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)):
    try:
        result = await auth_service.login(db, redis, username=body.username, password=body.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return ApiResponse(data={
        "user": UserOut.model_validate(result["user"]).model_dump(),
        "access_token": result["access_token"],
        "refresh_token": result["refresh_token"],
        "token_type": "bearer",
    })


@router.post("/refresh", response_model=ApiResponse)
async def refresh(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    try:
        result = await auth_service.refresh(
            db, redis, refresh_token_str=body.refresh_token
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    return ApiResponse(data=TokenResponse(**result).model_dump())


@router.post("/logout", response_model=ApiResponse)
async def logout(
    body: LogoutRequest,
    redis: Redis = Depends(get_redis),
    current_user: dict = Depends(get_current_user),
):
    await auth_service.logout(redis, refresh_token_str=body.refresh_token, access_jti=current_user.get("jti"))
    return ApiResponse(message="已登出")


@router.post("/sms-code", response_model=ApiResponse)
async def send_sms_code(body: SmsCodeRequest, redis: Redis = Depends(get_redis)):
    try:
        await sms_service.send_sms_code(redis, body.phone, body.scene)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return ApiResponse(message="验证码已发送")


@router.post("/password/reset", response_model=ApiResponse)
async def reset_password(
    body: ResetPasswordRequest, db: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)
):
    try:
        await auth_service.reset_password(
            db, redis, phone=body.phone, sms_code=body.sms_code, new_password=body.new_password
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return ApiResponse(message="密码已重置")


@router.post("/onboarding", response_model=ApiResponse)
async def onboarding(
    body: OnboardingRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    try:
        await auth_service.onboarding(
            db,
            user_id=current_user["user_id"],
            role=body.role,
            nickname=body.nickname,
            province=body.province,
            occupation=body.occupation,
            bio=body.bio,
            tags=body.tags,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return ApiResponse(message="初始化完成")
