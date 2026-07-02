from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.demand import Demand
from app.models.task import Task
from app.models.team import TaskMember
from app.models.user import User
from app.schemas.common import ApiResponse

router = APIRouter(tags=["统计"])


@router.get("/stats", response_model=ApiResponse)
async def get_platform_stats(db: AsyncSession = Depends(get_db)):
    tasks_total = (await db.execute(select(func.count()).select_from(Task))).scalar_one()
    tasks_in_progress = (await db.execute(
        select(func.count()).select_from(Task).where(Task.status == "in_progress")
    )).scalar_one()
    tasks_completed = (await db.execute(
        select(func.count()).select_from(Task).where(Task.status == "completed")
    )).scalar_one()
    tasks_closed = (await db.execute(
        select(func.count()).select_from(Task).where(Task.status == "closed")
    )).scalar_one()

    users_requester = (await db.execute(
        select(func.count()).select_from(User).where(User.role == "requester", User.is_deleted == 0)
    )).scalar_one()
    users_builder = (await db.execute(
        select(func.count()).select_from(User).where(User.role == "builder", User.is_deleted == 0)
    )).scalar_one()

    return ApiResponse(data={
        "tasks_total": tasks_total,
        "tasks_in_progress": tasks_in_progress,
        "tasks_completed": tasks_completed,
        "tasks_closed": tasks_closed,
        "users_requester": users_requester,
        "users_builder": users_builder,
    })


@router.get("/me/stats", response_model=ApiResponse)
async def get_my_stats(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = current_user["user_id"]

    demand_count = (await db.execute(
        select(func.count()).select_from(Demand).where(Demand.creator_id == user_id, Demand.is_deleted == 0)
    )).scalar_one()

    task_count = (await db.execute(
        select(func.count()).select_from(TaskMember).where(TaskMember.user_id == user_id)
    )).scalar_one()

    return ApiResponse(data={
        "demand_count": demand_count,
        "task_count": task_count,
    })
