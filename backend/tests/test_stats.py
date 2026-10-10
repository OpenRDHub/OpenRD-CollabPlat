import uuid

from sqlalchemy import select

from app.models.demand import Demand
from app.models.task import Task
from app.models.team import JoinApplication, TaskMember
from app.models.user import User
from app.utils.security import create_access_token, hash_password


STATS_URL = "/api/v1/me/stats"


async def create_user(db_session, suffix: int) -> User:
    user = User(
        id=uuid.uuid4().hex,
        platform_id=f"STA{suffix:07d}",
        username=f"stats_user_{suffix}",
        phone=f"137{suffix:08d}",
        password_hash=hash_password("Test123!"),
        role="requester",
        nickname=f"Stats User {suffix}",
    )
    db_session.add(user)
    await db_session.commit()
    return user


def auth_headers(user: User) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(user.id, user.role)}"}


async def test_my_stats_requires_bearer_token(client):
    response = await client.get(STATS_URL)

    assert response.status_code == 401


async def test_my_stats_rejects_invalid_bearer_token(client):
    response = await client.get(
        STATS_URL,
        headers={"Authorization": "Bearer not-a-valid-token"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "无效的 Token"


async def test_my_stats_returns_zero_without_related_records(client, db_session):
    user = await create_user(db_session, 1)

    response = await client.get(STATS_URL, headers=auth_headers(user))

    assert response.status_code == 200, response.text
    assert response.json()["data"] == {
        "demand_count": 0,
        "task_count": 0,
        "converted_demands": 0,
        "led_tasks": 0,
        "pending_applications": 0,
    }


async def test_my_stats_counts_only_current_users_demands_and_memberships(
    client, db_session
):
    current_user = await create_user(db_session, 2)
    other_user = await create_user(db_session, 3)

    db_session.add_all([
        Demand(
            id="REQ-STATS-1",
            title="Current user demand",
            description="Included in the current user's statistics.",
            creator_id=current_user.id,
        ),
        Demand(
            id="REQ-STATS-DELETED",
            title="Deleted current user demand",
            description="Soft-deleted demands must not be counted.",
            creator_id=current_user.id,
            is_deleted=1,
        ),
        Demand(
            id="REQ-STATS-OTHER",
            title="Other user demand",
            description="Other users' demands must not be counted.",
            creator_id=other_user.id,
        ),
        TaskMember(
            task_id="TASK-STATS-1",
            user_id=current_user.id,
            role="member",
        ),
        TaskMember(
            task_id="TASK-STATS-2",
            user_id=current_user.id,
            role="leader",
        ),
        TaskMember(
            task_id="TASK-STATS-OTHER",
            user_id=other_user.id,
            role="member",
        ),
    ])
    await db_session.commit()

    response = await client.get(STATS_URL, headers=auth_headers(current_user))

    assert response.status_code == 200, response.text
    assert response.json()["data"] == {
        "demand_count": 1,
        "task_count": 2,
        "converted_demands": 0,
        "led_tasks": 0,
        "pending_applications": 0,
    }


PLATFORM_STATS_URL = "/api/v1/stats"


async def test_platform_stats_is_public(client):
    response = await client.get(PLATFORM_STATS_URL)

    assert response.status_code == 200, response.text
    data = response.json()["data"]
    for key in (
        "tasks_total", "tasks_in_progress", "tasks_completed", "tasks_closed",
        "users_requester", "users_builder", "users_total",
        "demands_total", "tasks_recruiting", "pending_demands",
        "conversion_rate", "dau_today", "demands_7d", "tasks_7d",
    ):
        assert key in data


async def test_platform_stats_counts_via_delta(client, db_session):
    before = (await client.get(PLATFORM_STATS_URL)).json()["data"]

    user = await create_user(db_session, 9001)
    demand = Demand(id="D-DELTA", title="delta demand", description="delta demand desc", creator_id=user.id, status="pending_review")
    db_session.add(demand)
    db_session.add_all([
        Task(id="TASK-DELTA-1", demand_id=demand.id, title="recruiting one", status="recruiting"),
        Task(id="TASK-DELTA-2", demand_id=demand.id, title="recruiting two", status="recruiting"),
        Task(id="TASK-DELTA-3", demand_id=demand.id, title="in progress", status="in_progress"),
    ])
    await db_session.commit()

    after = (await client.get(PLATFORM_STATS_URL)).json()["data"]

    assert after["tasks_recruiting"] == before["tasks_recruiting"] + 2
    assert after["pending_demands"] == before["pending_demands"] + 1
    assert after["demands_total"] == before["demands_total"] + 1
    assert after["users_total"] == before["users_total"] + 1
    assert after["conversion_rate"] is None or isinstance(after["conversion_rate"], int)


async def test_my_stats_new_fields_via_delta(client, db_session):
    user = await create_user(db_session, 9002)
    headers = auth_headers(user)

    before = (await client.get(STATS_URL, headers=headers)).json()["data"]

    demand = Demand(id="D-NEW", title="converted", description="converted demand desc", creator_id=user.id, status="converted")
    db_session.add(demand)
    db_session.add(Task(
        id="TASK-NEW-1", demand_id=demand.id, title="led task",
        status="recruiting", leader_id=user.id,
    ))
    applicant = await create_user(db_session, 9003)
    db_session.add(TaskMember(id="TM-NEW-1", task_id="TASK-NEW-1", user_id=user.id, role="leader"))
    db_session.add(JoinApplication(
        id="JA-NEW-1", task_id="TASK-NEW-1", user_id=applicant.id, role="member", status="pending",
    ))
    await db_session.commit()

    after = (await client.get(STATS_URL, headers=headers)).json()["data"]

    assert after["converted_demands"] == before["converted_demands"] + 1
    assert after["led_tasks"] == before["led_tasks"] + 1
    assert after["pending_applications"] == before["pending_applications"] + 1


async def test_my_stats_refreshes_last_active_at(client, db_session):
    user = await create_user(db_session, 9004)
    headers = auth_headers(user)

    # 触发一次需认证的请求，get_current_user 应刷新 last_active_at（DAU 统计）
    response = await client.get(STATS_URL, headers=headers)
    assert response.status_code == 200

    refreshed = (await db_session.execute(
        select(User).where(User.id == user.id).execution_options(populate_existing=True)
    )).scalar_one()
    assert refreshed.last_active_at is not None
