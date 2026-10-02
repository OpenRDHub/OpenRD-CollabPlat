from sqlalchemy import select

from app.models.message import MessageRecipient
from app.services.message import create_message, get_unread_count


async def test_unread_count_is_user_scoped_and_sums_categories(db_session):
    current_user = "b19-current-user"
    other_user = "b19-other-user"

    task_message = await create_message(
        db_session,
        category="task",
        title="任务更新",
        recipient_ids=[current_user],
    )
    await create_message(
        db_session,
        category="demand",
        title="需求更新",
        recipient_ids=[current_user],
    )
    await create_message(
        db_session,
        category="team",
        title="团队更新",
        recipient_ids=[other_user],
    )

    recipient = (await db_session.execute(
        select(MessageRecipient).where(
            MessageRecipient.message_id == task_message.id,
            MessageRecipient.user_id == current_user,
        )
    )).scalar_one()
    recipient.is_read = 1
    await db_session.commit()

    result = await get_unread_count(db_session, current_user)

    assert result == {"total": 1, "by_category": {"demand": 1}}
    assert result["total"] == sum(result["by_category"].values())
