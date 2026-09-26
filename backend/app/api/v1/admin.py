from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import ALL_PERMISSIONS, ROLE_PERMISSIONS
from app.dependencies.auth import require_permissions
from app.dependencies.database import get_db
from app.schemas.admin import (
    PermissionOut,
    RoleOut,
    SetUserAuthorizationRequest,
    SystemLogOut,
    UserPermissionDetail,
)
from app.schemas.common import ApiResponse, PaginatedData
from app.services.admin import (
    count_super_admins,
    get_effective_permissions,
    get_system_log_by_id,
    get_user_permission_detail,
    list_system_logs,
    serialize_super_admin_changes,
    set_user_authorization,
)
from app.services.user import get_user_by_id

router = APIRouter(tags=["管理治理"])


@router.get("/admin/roles", response_model=ApiResponse[list[RoleOut]])
async def get_roles(
    current_user: dict = Depends(require_permissions("admin:role")),
):
    roles = []
    for code, perms in ROLE_PERMISSIONS.items():
        roles.append(RoleOut(name=code, code=code, permissions=sorted(perms)))
    return ApiResponse(data=roles)


@router.get("/admin/permissions", response_model=ApiResponse[list[PermissionOut]])
async def get_permissions(
    current_user: dict = Depends(require_permissions("admin:role")),
):
    permissions = []
    for p in sorted(ALL_PERMISSIONS):
        module = p.split(":")[0] if ":" in p else "system"
        permissions.append(PermissionOut(id=p, name=p, module=module))
    return ApiResponse(data=permissions)


@router.get(
    "/admin/users/{user_id}/permissions",
    response_model=ApiResponse[UserPermissionDetail],
)
async def get_user_permissions(
    user_id: str,
    current_user: dict = Depends(require_permissions("admin:role")),
    db: AsyncSession = Depends(get_db),
):
    """查询目标用户的角色模板权限、手动权限与最终权限。"""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    detail = await get_user_permission_detail(db, user)
    return ApiResponse(data=UserPermissionDetail(**detail))


@router.put(
    "/admin/users/{user_id}/authorization",
    response_model=ApiResponse[UserPermissionDetail],
)
async def put_user_authorization(
    user_id: str,
    body: SetUserAuthorizationRequest,
    current_user: dict = Depends(require_permissions("admin:role")),
    db: AsyncSession = Depends(get_db),
):
    """单事务原子完成「角色变更 + 手动权限替换 + 审计日志」。

    防提权守卫：
    1. 任何人都不能修改自己的授权
    2. 只有超级管理员可以变更角色
    3. 只有超级管理员可以调整超级管理员（目标或新角色为 super_admin）
    4. 非超级管理员不能授予超出自身最终权限的权限
    5. 不能降级最后一个超级管理员
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    actor_is_super = current_user["role"] == "super_admin"

    # 守卫 1：不能修改自己的授权（防自我提权/自我降级）
    if user.id == current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="不能修改自己的授权",
        )

    # 守卫 2：只有超级管理员可以变更角色
    if body.role != user.role and not actor_is_super:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有超级管理员可以变更角色",
        )

    # 守卫 3：只有超级管理员可以调整超级管理员
    if (user.role == "super_admin" or body.role == "super_admin") and not actor_is_super:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有超级管理员可以调整超级管理员的授权",
        )

    invalid = sorted(set(body.manual_permission_ids) - ALL_PERMISSIONS)
    if invalid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"非法权限 ID: {', '.join(invalid)}",
        )

    # 守卫 4：非超级管理员不能授予超出自身最终权限的权限
    if not actor_is_super:
        actor_effective = await get_effective_permissions(
            db, current_user["user_id"], current_user["role"]
        )
        beyond = sorted(set(body.manual_permission_ids) - actor_effective)
        if beyond:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"不能授予超出自身权限范围的权限: {', '.join(beyond)}",
            )

    # 守卫 5：不能降级最后一个超级管理员
    if user.role == "super_admin" and body.role != "super_admin":
        # 用 advisory lock 串行化「判断+变更」流程，避免两个超管并发互降
        await serialize_super_admin_changes(db)
        if await count_super_admins(db) <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能降级最后一个超级管理员",
            )

    detail = await set_user_authorization(
        db,
        user=user,
        role=body.role,
        manual_permission_ids=body.manual_permission_ids,
        reason=body.reason,
        actor=current_user,
    )
    return ApiResponse(data=UserPermissionDetail(**detail))


@router.get("/admin/system-logs", response_model=ApiResponse[PaginatedData[SystemLogOut]])
async def get_system_logs(
    actor_id: str | None = Query(default=None),
    action: str | None = Query(default=None),
    module: str | None = Query(default=None),
    target_type: str | None = Query(default=None),
    target_id: str | None = Query(default=None),
    risk_level: str | None = Query(default=None),
    result: str | None = Query(default=None),
    keyword: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: dict = Depends(require_permissions("admin:log")),
    db: AsyncSession = Depends(get_db),
):
    items, total = await list_system_logs(
        db,
        actor_id=actor_id,
        action=action,
        module=module,
        target_type=target_type,
        target_id=target_id,
        risk_level=risk_level,
        result=result,
        keyword=keyword,
        page=page,
        page_size=page_size,
    )
    return ApiResponse(
        data=PaginatedData(
            items=[SystemLogOut.model_validate(log) for log in items],
            page=page,
            page_size=page_size,
            total=total,
        )
    )


@router.get("/admin/system-logs/{log_id}", response_model=ApiResponse[SystemLogOut])
async def get_system_log(
    log_id: str,
    current_user: dict = Depends(require_permissions("admin:log")),
    db: AsyncSession = Depends(get_db),
):
    log = await get_system_log_by_id(db, log_id)
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="日志不存在")
    return ApiResponse(data=SystemLogOut.model_validate(log))
