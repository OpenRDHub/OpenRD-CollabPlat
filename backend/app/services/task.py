import json
import uuid

from sqlalchemy import func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskProgress


VALID_STATUS_TRANSITIONS = {
    "recruiting": ["team_ready", "closed"],
    "team_ready": ["in_progress", "closed"],
    "in_progress": ["pending_acceptance", "closed"],
    "pending_acceptance": ["completed", "in_progress", "closed"],
    "completed": [],
    "closed": [],
}


async def generate_task_id(db: AsyncSession) -> str:
    result = await db.execute(text("SELECT nextval('task_id_seq')"))
    seq_val = result.scalar_one()
    return f"TASK-{seq_val:04d}"


async def create_task(
    db: AsyncSession,
    *,
    demand_id: str | None = None,
    title: str,
    description: str | None = None,
    task_type: str | None = None,
    priority: str = "medium",
    scope: str | None = None,
    acceptance_criteria: str | None = None,
    planned_end_time: str | None = None,
    owner_id: str | None = None,
    leader_id: str | None = None,
) -> Task:
    task_id = await generate_task_id(db)
    task = Task(
        id=task_id,
        demand_id=demand_id,
        title=title,
        description=description,
        task_type=task_type,
        priority=priority,
        scope=scope,
        acceptance_criteria=acceptance_criteria,
        planned_end_time=planned_end_time,
        owner_id=owner_id,
        leader_id=leader_id,
        status="recruiting",
        team_status="forming",
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def list_tasks(
    db: AsyncSession,
    *,
    status: str | None = None,
    team_status: str | None = None,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Task], int]:
    base = select(Task).where(Task.is_deleted == 0)
    if status:
        base = base.where(Task.status == status)
    if team_status:
        base = base.where(Task.team_status == team_status)
    if keyword:
        like = f"%{keyword}%"
        base = base.where(
            or_(Task.title.ilike(like), Task.id.ilike(like), Task.demand_id.ilike(like))
        )

    count_stmt = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    items_stmt = base.order_by(Task.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(items_stmt)).scalars().all()
    return list(items), total


async def get_task_by_id(db: AsyncSession, task_id: str) -> Task | None:
    stmt = select(Task).where(Task.id == task_id, Task.is_deleted == 0)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_task(
    db: AsyncSession,
    task: Task,
    *,
    title: str | None = None,
    description: str | None = None,
    task_type: str | None = None,
    priority: str | None = None,
    scope: str | None = None,
    acceptance_criteria: str | None = None,
    planned_end_time: str | None = None,
) -> Task:
    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    if task_type is not None:
        task.task_type = task_type
    if priority is not None:
        task.priority = priority
    if scope is not None:
        task.scope = scope
    if acceptance_criteria is not None:
        task.acceptance_criteria = acceptance_criteria
    if planned_end_time is not None:
        task.planned_end_time = planned_end_time
    await db.commit()
    await db.refresh(task)
    return task


async def change_status(
    db: AsyncSession,
    task: Task,
    *,
    new_status: str,
    reason: str | None = None,
) -> Task:
    allowed = VALID_STATUS_TRANSITIONS.get(task.status, [])
    if new_status not in allowed:
        return None
    task.status = new_status
    if new_status == "closed" and reason:
        pass
    await db.commit()
    await db.refresh(task)
    return task


async def submit_progress(
    db: AsyncSession,
    *,
    task_id: str,
    user_id: str,
    progress: int,
    content: str | None = None,
    file_ids: list[str] | None = None,
) -> TaskProgress:
    entry = TaskProgress(
        id=uuid.uuid4().hex,
        task_id=task_id,
        user_id=user_id,
        progress=progress,
        content=content,
        file_ids=json.dumps(file_ids) if file_ids else None,
    )
    db.add(entry)

    task_stmt = select(Task).where(Task.id == task_id)
    task = (await db.execute(task_stmt)).scalar_one_or_none()
    if task:
        task.progress = progress

    await db.commit()
    await db.refresh(entry)
    return entry


async def update_resources(
    db: AsyncSession,
    task: Task,
    *,
    resource_links: list[dict] | None = None,
    file_ids: list[str] | None = None,
) -> Task:
    if resource_links is not None:
        task.resource_links = json.dumps(resource_links, ensure_ascii=False)
    if file_ids is not None:
        task.file_ids = json.dumps(file_ids)
    await db.commit()
    await db.refresh(task)
    return task


async def list_my_tasks(
    db: AsyncSession,
    *,
    user_id: str,
    status: str | None = None,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Task], int]:
    base = select(Task).where(
        Task.is_deleted == 0,
        or_(Task.owner_id == user_id, Task.leader_id == user_id),
    )
    if status:
        base = base.where(Task.status == status)
    if keyword:
        like = f"%{keyword}%"
        base = base.where(or_(Task.title.ilike(like), Task.id.ilike(like)))

    count_stmt = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    items_stmt = base.order_by(Task.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(items_stmt)).scalars().all()
    return list(items), total
