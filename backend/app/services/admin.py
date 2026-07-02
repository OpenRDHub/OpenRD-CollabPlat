import json
import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin import SystemLog


async def create_system_log(
    db: AsyncSession,
    *,
    actor_id: str,
    actor_role: str | None = None,
    actor_nickname: str | None = None,
    action: str,
    module: str,
    target_type: str | None = None,
    target_id: str | None = None,
    target_name: str | None = None,
    risk_level: str = "low",
    detail: dict | None = None,
    ip: str | None = None,
    user_agent: str | None = None,
    result: str = "success",
) -> SystemLog:
    log = SystemLog(
        id=uuid.uuid4().hex,
        actor_id=actor_id,
        actor_role=actor_role,
        actor_nickname=actor_nickname,
        action=action,
        module=module,
        target_type=target_type,
        target_id=target_id,
        target_name=target_name,
        risk_level=risk_level,
        detail=json.dumps(detail, ensure_ascii=False) if detail else None,
        ip=ip,
        user_agent=user_agent,
        result=result,
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log


async def list_system_logs(
    db: AsyncSession,
    *,
    actor_id: str | None = None,
    action: str | None = None,
    module: str | None = None,
    target_type: str | None = None,
    target_id: str | None = None,
    risk_level: str | None = None,
    result: str | None = None,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[SystemLog], int]:
    base = select(SystemLog)
    if actor_id:
        base = base.where(SystemLog.actor_id == actor_id)
    if action:
        base = base.where(SystemLog.action == action)
    if module:
        base = base.where(SystemLog.module == module)
    if target_type:
        base = base.where(SystemLog.target_type == target_type)
    if target_id:
        base = base.where(SystemLog.target_id == target_id)
    if risk_level:
        base = base.where(SystemLog.risk_level == risk_level)
    if result:
        base = base.where(SystemLog.result == result)
    if keyword:
        like = f"%{keyword}%"
        base = base.where(
            or_(
                SystemLog.actor_nickname.ilike(like),
                SystemLog.target_name.ilike(like),
                SystemLog.action.ilike(like),
            )
        )

    count_stmt = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    items_stmt = base.order_by(SystemLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(items_stmt)).scalars().all()
    return list(items), total


async def get_system_log_by_id(db: AsyncSession, log_id: str) -> SystemLog | None:
    stmt = select(SystemLog).where(SystemLog.id == log_id)
    return (await db.execute(stmt)).scalar_one_or_none()
