from fastapi import APIRouter, Depends
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.demand import Demand
from app.models.task import Task
from app.models.team import JoinApplication, TaskMember
from app.models.user import User
from app.schemas.common import ApiResponse

router = APIRouter(tags=["统计"])

# 需求「已处置」状态集合：用于本月转化率分母
_DISPOSED_DEMAND_STATUSES = ("converted", "linked", "archived", "closed", "rejected")


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
    # 平台总注册用户数（全部未删除角色）
    users_total = (await db.execute(
        select(func.count()).select_from(User).where(User.is_deleted == 0)
    )).scalar_one()

    # 公开需求总数
    demands_total = (await db.execute(
        select(func.count()).select_from(Demand).where(Demand.is_deleted == 0)
    )).scalar_one()

    # 招募中的任务数
    tasks_recruiting = (await db.execute(
        select(func.count()).select_from(Task).where(Task.status == "recruiting", Task.is_deleted == 0)
    )).scalar_one()

    # 待审核需求数
    pending_demands = (await db.execute(
        select(func.count()).select_from(Demand).where(
            Demand.status == "pending_review", Demand.is_deleted == 0
        )
    )).scalar_one()

    # 本月转化率：本月已转化 / 本月已处置
    month_expr = func.date_trunc("month", func.now())
    converted_month = (await db.execute(
        select(func.count()).select_from(Demand).where(
            Demand.status == "converted",
            Demand.is_deleted == 0,
            func.date_trunc("month", Demand.created_at) == month_expr,
        )
    )).scalar_one()
    disposed_month = (await db.execute(
        select(func.count()).select_from(Demand).where(
            Demand.status.in_(_DISPOSED_DEMAND_STATUSES),
            Demand.is_deleted == 0,
            func.date_trunc("month", Demand.created_at) == month_expr,
        )
    )).scalar_one()
    conversion_rate = round(converted_month / disposed_month * 100) if disposed_month else None

    # 今日活跃用户数（DAU）：last_active_at 落在今天
    dau_today = (await db.execute(
        select(func.count()).select_from(User).where(
            User.is_deleted == 0,
            User.last_active_at >= func.date_trunc("day", func.now()),
        )
    )).scalar_one()

    # 近 7 天新增需求数 / 工单数
    since_7d = func.now() - text("interval '7 days'")
    demands_7d = (await db.execute(
        select(func.count()).select_from(Demand).where(
            Demand.is_deleted == 0, Demand.created_at >= since_7d
        )
    )).scalar_one()
    tasks_7d = (await db.execute(
        select(func.count()).select_from(Task).where(
            Task.is_deleted == 0, Task.created_at >= since_7d
        )
    )).scalar_one()

    return ApiResponse(data={
        "tasks_total": tasks_total,
        "tasks_in_progress": tasks_in_progress,
        "tasks_completed": tasks_completed,
        "tasks_closed": tasks_closed,
        "users_requester": users_requester,
        "users_builder": users_builder,
        "users_total": users_total,
        "demands_total": demands_total,
        "tasks_recruiting": tasks_recruiting,
        "pending_demands": pending_demands,
        "conversion_rate": conversion_rate,
        "dau_today": dau_today,
        "demands_7d": demands_7d,
        "tasks_7d": tasks_7d,
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

    # 已转化的需求数（当前用户提交）
    converted_demands = (await db.execute(
        select(func.count()).select_from(Demand).where(
            Demand.creator_id == user_id,
            Demand.status == "converted",
            Demand.is_deleted == 0,
        )
    )).scalar_one()

    # 我是队长的工单数
    led_tasks = (await db.execute(
        select(func.count()).select_from(Task).where(
            Task.leader_id == user_id, Task.is_deleted == 0
        )
    )).scalar_one()

    # 待我处理的申请数：我担任队长的任务下的 pending 加入申请
    led_task_ids = select(Task.id).where(
        Task.leader_id == user_id, Task.is_deleted == 0
    ).scalar_subquery()
    pending_applications = (await db.execute(
        select(func.count()).select_from(JoinApplication).where(
            JoinApplication.status == "pending",
            JoinApplication.is_deleted == 0,
            JoinApplication.task_id.in_(led_task_ids),
        )
    )).scalar_one()

    return ApiResponse(data={
        "demand_count": demand_count,
        "task_count": task_count,
        "converted_demands": converted_demands,
        "led_tasks": led_tasks,
        "pending_applications": pending_applications,
    })
