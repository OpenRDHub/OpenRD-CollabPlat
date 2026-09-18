from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import ALL_PERMISSIONS, ROLE_PERMISSIONS
from app.dependencies.auth import require_permissions
from app.dependencies.database import get_db
from app.schemas.admin import (
    PermissionOut,
    RoleOut,
    SetUserPermissionsRequest,
    SystemLogOut,
    UserPermissionDetail,
)
from app.schemas.common import ApiResponse, PaginatedData
from app.services.admin import (
    get_system_log_by_id,
    get_user_permission_detail,
    list_system_logs,
    set_user_manual_permissions,
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
    "/admin/users/{user_id}/permissions",
    response_model=ApiResponse[UserPermissionDetail],
)
async def put_user_permissions(
    user_id: str,
    body: SetUserPermissionsRequest,
    current_user: dict = Depends(require_permissions("admin:role")),
    db: AsyncSession = Depends(get_db),
):
    """替换目标用户的手动权限集合（只保存手动权限，角色模板权限不可通过本接口修改）。"""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    if user.role == "super_admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="超级管理员已拥有全部权限，不能通过手动权限接口调整",
        )

    invalid = sorted(set(body.manual_permission_ids) - ALL_PERMISSIONS)
    if invalid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"非法权限 ID: {', '.join(invalid)}",
        )

    detail = await set_user_manual_permissions(
        db,
        user=user,
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
