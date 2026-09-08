from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.team import is_task_member_or_leader
from app.dependencies.auth import get_current_user, require_permissions
from app.dependencies.database import get_db
from app.schemas.common import ApiResponse, PaginatedData
from app.schemas.task import (
    ProgressRequest,
    ResourcesRequest,
    StatusChangeRequest,
    TaskDetail,
    TaskOut,
    TaskProgressOut,
    TaskUpdateRequest,
)
from app.services.task import (
    change_status,
    get_task_by_id,
    list_my_tasks,
    list_tasks,
    submit_progress,
    update_resources,
    update_task,
)

router = APIRouter(tags=["任务"])


# --- 任务大厅 & 详情 ---

@router.get("/tasks", response_model=ApiResponse[PaginatedData[TaskOut]])
async def get_tasks_list(
    status_filter: str | None = Query(default=None, alias="status"),
    team_status: str | None = Query(default=None),
    keyword: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: dict = Depends(require_permissions("task:view")),
    db: AsyncSession = Depends(get_db),
):
    items, total = await list_tasks(
        db,
        status=status_filter,
        team_status=team_status,
        keyword=keyword,
        page=page,
        page_size=page_size,
    )
    return ApiResponse(
        data=PaginatedData(
            items=[TaskOut.model_validate(t) for t in items],
            page=page,
            page_size=page_size,
            total=total,
        )
    )


@router.get("/tasks/{task_id}", response_model=ApiResponse[TaskDetail])
async def get_task(
    task_id: str,
    current_user: dict = Depends(require_permissions("task:view")),
    db: AsyncSession = Depends(get_db),
):
    task = await get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")
    return ApiResponse(data=TaskDetail.model_validate(task))


# --- 任务管理 ---

@router.patch("/tasks/{task_id}", response_model=ApiResponse[TaskDetail])
async def patch_task(
    task_id: str,
    body: TaskUpdateRequest,
    current_user: dict = Depends(require_permissions("task:manage")),
    db: AsyncSession = Depends(get_db),
):
    task = await get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")
    if task.status in ("completed", "closed"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="已完成或已关闭的任务不可编辑")
    updates = body.model_dump(exclude_unset=True)
    task = await update_task(db, task, **updates)
    return ApiResponse(data=TaskDetail.model_validate(task))


@router.post("/tasks/{task_id}/status", response_model=ApiResponse[TaskDetail])
async def post_change_status(
    task_id: str,
    body: StatusChangeRequest,
    current_user: dict = Depends(require_permissions("task:manage")),
    db: AsyncSession = Depends(get_db),
):
    task = await get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")
    result = await change_status(db, task, new_status=body.status, reason=body.reason)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不允许从 {task.status} 变更到 {body.status}",
        )
    return ApiResponse(data=TaskDetail.model_validate(result))


@router.post("/tasks/{task_id}/progress", response_model=ApiResponse[TaskProgressOut])
async def post_progress(
    task_id: str,
    body: ProgressRequest,
    current_user: dict = Depends(require_permissions("task:update")),
    db: AsyncSession = Depends(get_db),
):
    task = await get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")
    if task.status not in ("in_progress", "pending_acceptance"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前状态不允许提交进度")
    
    # ===== 新增：数据归属校验 =====
    user_id = current_user["user_id"]
    user_role = current_user["role"]
    
    # 被授权运营 / 超级管理员 → 直接放行
    is_authorized = user_role in ("operator", "super_admin")
    
    # 队长 / active 正式成员
    is_member = await is_task_member_or_leader(db, task_id, user_id)
    
    if not is_authorized and not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="仅任务队长、正式成员、运营或超级管理员可提交进度",
        )    
    
    entry = await submit_progress(
        db,
        task_id=task_id,
        user_id=current_user["user_id"],
        progress=body.progress,
        content=body.content,
        file_ids=body.file_ids,
        actor_role=current_user["role"],
    )
    return ApiResponse(data=TaskProgressOut.model_validate(entry))


@router.post("/tasks/{task_id}/resources", response_model=ApiResponse[TaskDetail])
async def post_resources(
    task_id: str,
    body: ResourcesRequest,
    current_user: dict = Depends(require_permissions("task:manage")),
    db: AsyncSession = Depends(get_db),
):
    task = await get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")
    task = await update_resources(
        db, task,
        resource_links=body.resource_links,
        file_ids=body.file_ids,
        actor_id=current_user["user_id"],
        actor_role=current_user["role"],
    )
    return ApiResponse(data=TaskDetail.model_validate(task))


# --- 我的任务 ---

@router.get("/me/tasks", response_model=ApiResponse[PaginatedData[TaskOut]])
async def get_my_tasks(
    status_filter: str | None = Query(default=None, alias="status"),
    keyword: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items, total = await list_my_tasks(
        db,
        user_id=current_user["user_id"],
        status=status_filter,
        keyword=keyword,
        page=page,
        page_size=page_size,
    )
    return ApiResponse(
        data=PaginatedData(
            items=[TaskOut.model_validate(t) for t in items],
            page=page,
            page_size=page_size,
            total=total,
        )
    )
