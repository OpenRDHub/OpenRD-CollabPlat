import json

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import get_permissions_for_role
from app.dependencies.auth import get_current_user, require_permissions
from app.dependencies.database import get_db
from app.schemas.common import ApiResponse, PaginatedData
from app.schemas.user import (
    AdminUserUpdate,
    PasswordChangeRequest,
    ProfileUpdateRequest,
    UserDetail,
)
from app.services.user import (
    admin_update_user,
    change_password,
    get_user_by_id,
    list_users,
    lock_user,
    unlock_user,
    update_profile,
)

router = APIRouter(tags=["用户"])


def _user_to_detail(user) -> UserDetail:
    tags = None
    if user.tags:
        try:
            tags = json.loads(user.tags)
        except (json.JSONDecodeError, TypeError):
            tags = []
    return UserDetail(
        id=user.id,
        platform_id=user.platform_id,
        username=user.username,
        phone=user.phone,
        role=user.role,
        nickname=user.nickname,
        avatar_url=user.avatar_url,
        province=user.province,
        occupation=user.occupation,
        bio=user.bio,
        tags=tags,
        is_onboarded=user.is_onboarded,
        is_locked=user.is_locked,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )

@router.get("/me", response_model=ApiResponse[UserDetail])
async def get_me(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_id(db, current_user["user_id"])
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    return ApiResponse(data=_user_to_detail(user))


@router.patch("/me/profile", response_model=ApiResponse[UserDetail])
async def patch_profile(
    body: ProfileUpdateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_id(db, current_user["user_id"])
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    updates = body.model_dump(exclude_unset=True)
    user = await update_profile(db, user, **updates)
    return ApiResponse(data=_user_to_detail(user))


@router.patch("/me/password", response_model=ApiResponse)
async def patch_password(
    body: PasswordChangeRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_id(db, current_user["user_id"])
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    ok = await change_password(db, user, old_password=body.old_password, new_password=body.new_password)
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="原密码错误")
    return ApiResponse(message="密码修改成功")


@router.get("/me/permissions", response_model=ApiResponse[list[str]])
async def get_my_permissions(
    current_user: dict = Depends(get_current_user),
):
    perms = sorted(get_permissions_for_role(current_user["role"]))
    return ApiResponse(data=perms)


# --- Admin routes ---

@router.get("/admin/users", response_model=ApiResponse[PaginatedData[UserDetail]])
async def admin_list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    keyword: str | None = Query(default=None),
    role: str | None = Query(default=None),
    current_user: dict = Depends(require_permissions("admin:user")),
    db: AsyncSession = Depends(get_db),
):
    items, total = await list_users(db, page=page, page_size=page_size, keyword=keyword, role=role)
    return ApiResponse(
        data=PaginatedData(
            items=[_user_to_detail(u) for u in items],
            page=page,
            page_size=page_size,
            total=total,
        )
    )


@router.get("/admin/users/{user_id}", response_model=ApiResponse[UserDetail])
async def admin_get_user(
    user_id: str,
    current_user: dict = Depends(require_permissions("admin:user")),
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    return ApiResponse(data=_user_to_detail(user))


@router.patch("/admin/users/{user_id}", response_model=ApiResponse[UserDetail])
async def admin_patch_user(
    user_id: str,
    body: AdminUserUpdate,
    current_user: dict = Depends(require_permissions("admin:user")),
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    updates = body.model_dump(exclude_unset=True)
    user = await admin_update_user(db, user, **updates)
    return ApiResponse(data=_user_to_detail(user))


@router.post("/admin/users/{user_id}/lock", response_model=ApiResponse)
async def admin_lock_user(
    user_id: str,
    current_user: dict = Depends(require_permissions("admin:user")),
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    if user.is_locked:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户已处于锁定状态")
    await lock_user(db, user)
    return ApiResponse(message="用户已锁定")


@router.post("/admin/users/{user_id}/unlock", response_model=ApiResponse)
async def admin_unlock_user(
    user_id: str,
    current_user: dict = Depends(require_permissions("admin:user")),
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    if not user.is_locked:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户未处于锁定状态")
    await unlock_user(db, user)
    return ApiResponse(message="用户已解锁")