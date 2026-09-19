from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user, require_permissions
from app.dependencies.database import get_db
from app.models.task import TaskProgress
from app.schemas.common import ApiResponse, PaginatedData
from app.schemas.task import (
    MyTaskOut,
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


# --- 进度时间线（项目进度面板主体渲染的数据源） ---
STAGE_LABELS = {"team": "组队", "develop": "开发", "beta": "内测", "opensource": "开源"}


@router.get("/tasks/{task_id}/timeline", response_model=ApiResponse[dict])
async def get_task_timeline(
    task_id: str,
    current_user: dict = Depends(require_permissions("task:view")),
    db: AsyncSession = Depends(get_db),
):
    """返回任务的进度更新时间线，基于 TaskProgress 记录（按时间升序）。"""
    task = await get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")
    result = await db.execute(
        select(TaskProgress)
        .where(TaskProgress.task_id == task_id, TaskProgress.is_deleted == 0)
        .order_by(TaskProgress.created_at.asc())
    )
    entries = result.scalars().all()
    timeline = [
        {
            "id": e.id,
            "task_id": e.task_id,
            "title": STAGE_LABELS.get(e.stage, e.stage or "进度更新"),
            "description": "\n".join(
                filter(
                    None,
                    [e.content or "", f"下一步：{e.next_plan}" if e.next_plan else ""],
                )
            ),
            "date": e.created_at.strftime("%Y-%m-%d %H:%M") if e.created_at else "",
            # 最新一条标记为“进行中”，其余为“已完成”
            "state": "doing" if idx == len(entries) - 1 else "done",
        }
        for idx, e in enumerate(entries)
    ]
    return ApiResponse(data={"timeline": timeline})


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
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = await get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")
    # 权限：仅运营/超级管理员、任务负责人(owner)、队长(leader) 可推进阶段；
    # 普通共建者（非队长）无权操作。
    user_role = current_user["role"]
    user_id = current_user["user_id"]
    is_authorized = user_role in ("operator", "super_admin")
    is_owner_or_leader = user_id in (task.leader_id, task.owner_id)
    if not is_authorized and not is_owner_or_leader:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="仅任务队长、负责人、运营或超级管理员可变更任务状态",
        )
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
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = await get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")
    if task.status not in ("in_progress", "pending_acceptance"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前状态不允许提交进度")
    
    # ===== 数据归属校验：仅运营/超级管理员、任务负责人(owner)、队长(leader) 可提交进度 =====
    user_id = current_user["user_id"]
    user_role = current_user["role"]
    is_authorized = user_role in ("operator", "super_admin")
    is_owner_or_leader = user_id in (task.leader_id, task.owner_id)
    if not is_authorized and not is_owner_or_leader:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="仅任务队长、负责人、运营或超级管理员可提交进度",
        )
    
    entry = await submit_progress(
        db,
        task_id=task_id,
        user_id=current_user["user_id"],
        stage=body.stage,
        content=body.content,
        file_ids=body.file_ids,
        next_plan=body.next_plan,
        base_stage=body.base_stage,
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

@router.get("/me/tasks", response_model=ApiResponse[PaginatedData[MyTaskOut]])
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
            items=[
                MyTaskOut(
                    **TaskOut.model_validate(task).model_dump(),
                    my_role=my_role,
                    my_stage=my_stage,
                )
                for task, my_role, my_stage in items
            ],
            page=page,
            page_size=page_size,
            total=total,
        )
    )
