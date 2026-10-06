import uuid

from app.models.demand import Demand
from app.models.team import TaskMember
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
    }
