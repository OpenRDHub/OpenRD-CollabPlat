from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import ALL_PERMISSIONS, ROLE_PERMISSIONS
from app.dependencies.auth import get_current_user, require_permissions
from app.dependencies.database import get_db
from app.schemas.admin import (
    CreateRoleRequest,
    PermissionOut,
    RoleOut,
    SetUserPermissionsRequest,
    SystemLogOut,
    UpdateRoleRequest,
)
from app.schemas.common import ApiResponse, PaginatedData
from app.services.admin import get_system_log_by_id, list_system_logs

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
