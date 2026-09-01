import json
import uuid

from sqlalchemy import func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.demand import Demand, DemandReply
from app.services.file import bind_files


async def generate_demand_id(db: AsyncSession) -> str:
    result = await db.execute(text("SELECT nextval('demand_id_seq')"))
    seq_val = result.scalar_one()
    return f"REQ-{seq_val:04d}"


async def create_demand(
    db: AsyncSession,
    *,
    creator_id: str,
    actor_role: str,
    title: str,
    description: str,
    urgency: str,
    contact_phone: str | None = None,
    attachment_ids: list[str] | None = None,
) -> Demand:
    demand_id = await generate_demand_id(db)
    demand = Demand(
        id=demand_id,
        title=title,
        description=description,
        urgency=urgency,
        status="pending_review",
        creator_id=creator_id,
        contact_phone=contact_phone,
        attachment_ids=json.dumps(attachment_ids) if attachment_ids else None,
    )
    db.add(demand)
    await bind_files(
        db,
        attachment_ids,
        biz_type="demand",
        biz_id=demand_id,
        actor_id=creator_id,
        actor_role=actor_role,
    )
    await db.commit()
    await db.refresh(demand)
    return demand


async def list_my_demands(
    db: AsyncSession,
    *,
    creator_id: str,
    status: str | None = None,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Demand], int]:
    base = select(Demand).where(Demand.creator_id == creator_id, Demand.is_deleted == 0)
    if status:
        base = base.where(Demand.status == status)
    if keyword:
        like = f"%{keyword}%"
        base = base.where(
            or_(Demand.title.ilike(like), Demand.feedback.ilike(like), Demand.linked_task_id.ilike(like))
        )

    count_stmt = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    items_stmt = base.order_by(Demand.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(items_stmt)).scalars().all()
    return list(items), total


async def list_demands(
    db: AsyncSession,
    *,
    status: str | None = None,
    convert_status: str | None = None,
    owner_id: str | None = None,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Demand], int]:
    base = select(Demand).where(Demand.is_deleted == 0)
    if status:
        base = base.where(Demand.status == status)
    if convert_status:
        base = base.where(Demand.convert_status == convert_status)
    if owner_id:
        base = base.where(Demand.owner_id == owner_id)
    if keyword:
        like = f"%{keyword}%"
        base = base.where(
            or_(
                Demand.title.ilike(like),
                Demand.id.ilike(like),
                Demand.linked_task_id.ilike(like),
            )
        )

    count_stmt = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    items_stmt = base.order_by(Demand.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(items_stmt)).scalars().all()
    return list(items), total


async def get_demand_by_id(db: AsyncSession, demand_id: str) -> Demand | None:
    stmt = select(Demand).where(Demand.id == demand_id, Demand.is_deleted == 0)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_demand(
    db: AsyncSession,
    demand: Demand,
    *,
    progress: int | None = None,
    feedback: str | None = None,
    owner_id: str | None = None,
) -> Demand:
    if progress is not None:
        demand.progress = progress
    if feedback is not None:
        demand.feedback = feedback
    if owner_id is not None:
        demand.owner_id = owner_id
    await db.commit()
    await db.refresh(demand)
    return demand


async def convert_demand(
    db: AsyncSession,
    demand: Demand,
    *,
    task_id: str,
) -> Demand:
    demand.status = "converted"
    demand.convert_status = "converted"
    demand.linked_task_id = task_id
    await db.commit()
    await db.refresh(demand)
    return demand


async def reject_demand(
    db: AsyncSession,
    demand: Demand,
    *,
    reason: str,
) -> Demand:
    demand.status = "rejected"
    demand.feedback = reason
    await db.commit()
    await db.refresh(demand)
    return demand


async def link_similar(
    db: AsyncSession,
    demand: Demand,
    *,
    target_demand_id: str | None = None,
    target_task_id: str | None = None,
    reason: str,
) -> Demand:
    demand.status = "linked"
    if target_demand_id:
        demand.linked_demand_id = target_demand_id
    if target_task_id:
        demand.linked_task_id = target_task_id
    demand.feedback = reason
    await db.commit()
    await db.refresh(demand)
    return demand


async def archive_demand(db: AsyncSession, demand: Demand) -> Demand:
    demand.status = "archived"
    await db.commit()
    await db.refresh(demand)
    return demand


# --- DemandReply ---

async def create_reply(
    db: AsyncSession,
    *,
    demand_id: str,
    thread_id: str,
    sender_id: str,
    sender_role: str,
    actor_role: str,
    content: str,
    attachment_ids: list[str] | None = None,
) -> DemandReply:
    reply_id = uuid.uuid4().hex
    reply = DemandReply(
        id=reply_id,
        demand_id=demand_id,
        thread_id=thread_id,
        sender_id=sender_id,
        sender_role=sender_role,
        content=content,
        attachment_ids=json.dumps(attachment_ids) if attachment_ids else None,
    )
    db.add(reply)
    await bind_files(
        db,
        attachment_ids,
        biz_type="demand_reply",
        biz_id=reply_id,
        actor_id=sender_id,
        actor_role=actor_role,
    )
    await db.commit()
    await db.refresh(reply)
    return reply


async def get_reply_by_id(db: AsyncSession, reply_id: str) -> DemandReply | None:
    stmt = select(DemandReply).where(DemandReply.id == reply_id, DemandReply.is_deleted == 0)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def revoke_reply(db: AsyncSession, reply: DemandReply) -> DemandReply:
    reply.is_revoked = 1
    reply.content = ""
    await db.commit()
    await db.refresh(reply)
    return reply


async def list_replies(
    db: AsyncSession,
    *,
    demand_id: str,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[DemandReply], int]:
    base = select(DemandReply).where(
        DemandReply.demand_id == demand_id, DemandReply.is_deleted == 0
    )
    count_stmt = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    items_stmt = base.order_by(DemandReply.created_at.asc()).offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(items_stmt)).scalars().all()
    return list(items), total
