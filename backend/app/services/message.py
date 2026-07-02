import uuid
from datetime import datetime, timezone

from sqlalchemy import and_, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message import Message, MessageRecipient


async def create_message(
    db: AsyncSession,
    *,
    category: str,
    title: str,
    content: str | None = None,
    target_type: str | None = None,
    target_id: str | None = None,
    sender_id: str | None = None,
    recipient_ids: list[str],
) -> Message:
    msg = Message(
        id=uuid.uuid4().hex,
        category=category,
        title=title,
        content=content,
        target_type=target_type,
        target_id=target_id,
        sender_id=sender_id,
    )
    db.add(msg)

    for uid in recipient_ids:
        recipient = MessageRecipient(
            id=uuid.uuid4().hex,
            message_id=msg.id,
            user_id=uid,
        )
        db.add(recipient)

    await db.commit()
    await db.refresh(msg)
    return msg


async def list_messages(
    db: AsyncSession,
    *,
    user_id: str,
    category: str | None = None,
    unread_only: bool = False,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[dict], int]:
    base = (
        select(Message, MessageRecipient.is_read)
        .join(MessageRecipient, MessageRecipient.message_id == Message.id)
        .where(
            MessageRecipient.user_id == user_id,
            MessageRecipient.is_deleted == 0,
        )
    )
    if category and category != "all":
        base = base.where(Message.category == category)
    if unread_only:
        base = base.where(MessageRecipient.is_read == 0)
    if keyword:
        like = f"%{keyword}%"
        base = base.where(Message.title.ilike(like))

    count_stmt = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    items_stmt = base.order_by(Message.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    rows = (await db.execute(items_stmt)).all()

    result = []
    for msg, is_read in rows:
        result.append({
            "id": msg.id,
            "category": msg.category,
            "title": msg.title,
            "content": msg.content,
            "target_type": msg.target_type,
            "target_id": msg.target_id,
            "sender_id": msg.sender_id,
            "is_read": is_read,
            "created_at": msg.created_at,
        })
    return result, total


async def get_unread_count(db: AsyncSession, user_id: str) -> dict:
    base = (
        select(Message.category, func.count())
        .join(MessageRecipient, MessageRecipient.message_id == Message.id)
        .where(
            MessageRecipient.user_id == user_id,
            MessageRecipient.is_deleted == 0,
            MessageRecipient.is_read == 0,
        )
        .group_by(Message.category)
    )
    rows = (await db.execute(base)).all()
    by_category = {cat: count for cat, count in rows}
    total = sum(by_category.values())
    return {"total": total, "by_category": by_category}


async def get_message_detail(db: AsyncSession, message_id: str, user_id: str) -> dict | None:
    stmt = (
        select(Message, MessageRecipient)
        .join(MessageRecipient, MessageRecipient.message_id == Message.id)
        .where(
            Message.id == message_id,
            MessageRecipient.user_id == user_id,
            MessageRecipient.is_deleted == 0,
        )
    )
    row = (await db.execute(stmt)).first()
    if not row:
        return None

    msg, recipient = row
    if not recipient.is_read:
        recipient.is_read = 1
        recipient.read_at = datetime.now(timezone.utc).isoformat()
        await db.commit()

    return {
        "id": msg.id,
        "category": msg.category,
        "title": msg.title,
        "content": msg.content,
        "target_type": msg.target_type,
        "target_id": msg.target_id,
        "sender_id": msg.sender_id,
        "is_read": 1,
        "created_at": msg.created_at,
    }


async def mark_read(db: AsyncSession, message_id: str, user_id: str) -> bool:
    stmt = (
        update(MessageRecipient)
        .where(
            MessageRecipient.message_id == message_id,
            MessageRecipient.user_id == user_id,
            MessageRecipient.is_deleted == 0,
        )
        .values(is_read=1, read_at=datetime.now(timezone.utc).isoformat())
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


async def mark_all_read(db: AsyncSession, user_id: str) -> int:
    stmt = (
        update(MessageRecipient)
        .where(
            MessageRecipient.user_id == user_id,
            MessageRecipient.is_read == 0,
            MessageRecipient.is_deleted == 0,
        )
        .values(is_read=1, read_at=datetime.now(timezone.utc).isoformat())
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount


async def delete_message(db: AsyncSession, message_id: str, user_id: str) -> bool:
    stmt = (
        update(MessageRecipient)
        .where(
            MessageRecipient.message_id == message_id,
            MessageRecipient.user_id == user_id,
            MessageRecipient.is_deleted == 0,
        )
        .values(
            is_deleted=1,
            deleted_at=datetime.now(timezone.utc),
            deleted_by=user_id,
        )
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0
