"""
任务大厅公开接口 /tasks/explore 测试。

覆盖：
  - 无需登录即可访问（公开接口）；
  - 仅返回活跃状态任务（排除 已完成 / 已关闭 / 软删除）；
  - limit 参数生效。
"""
import pytest

from app.models.demand import Demand
from app.models.task import Task
from app.models.user import User

EXPECTED_ACTIVE = {"recruiting", "team_ready", "in_progress", "pending_acceptance"}


async def seed(db_session, prefix: str):
    """写入 3 个活跃任务 + 1 个已完成 + 1 个已关闭 + 1 个软删除，返回 (活跃id集合, 排除id集合)。"""
    creator = User(
        id=f"{prefix}-U",
        platform_id=f"EXP{prefix}",
        username=f"exp_creator_{prefix}",
        phone=f"139{prefix}001",
        password_hash="hashed",
        role="requester",
        nickname="seed",
    )
    db_session.add(creator)
    demand = Demand(
        id=f"{prefix}-D", title="seed demand", description="seed demand desc", creator_id=creator.id,
    )
    db_session.add(demand)
    db_session.add_all([
        Task(id=f"{prefix}-REC-1", demand_id=demand.id, title="recruiting one", status="recruiting"),
        Task(id=f"{prefix}-REC-2", demand_id=demand.id, title="recruiting two", status="recruiting"),
        Task(id=f"{prefix}-PROG-1", demand_id=demand.id, title="in progress", status="in_progress"),
        Task(id=f"{prefix}-DONE-1", demand_id=demand.id, title="done", status="completed"),
        Task(id=f"{prefix}-CLOSED-1", demand_id=demand.id, title="closed", status="closed"),
        Task(id=f"{prefix}-DEL-1", demand_id=demand.id, title="deleted", status="recruiting", is_deleted=1),
    ])
    await db_session.commit()
    active = {f"{prefix}-REC-1", f"{prefix}-REC-2", f"{prefix}-PROG-1"}
    excluded = {f"{prefix}-DONE-1", f"{prefix}-CLOSED-1", f"{prefix}-DEL-1"}
    return active, excluded


@pytest.mark.asyncio
async def test_explore_is_public(client):
    response = await client.get("/api/v1/tasks/explore")
    assert response.status_code == 200, response.text


@pytest.mark.asyncio
async def test_explore_returns_only_active_tasks(client, db_session):
    await seed(db_session, "A")

    response = await client.get("/api/v1/tasks/explore?limit=20")
    assert response.status_code == 200, response.text
    items = response.json()["data"]["items"]

    # 仅返回活跃状态，且包含必要的字段
    assert len(items) >= 1
    assert len(items) <= 20
    for it in items:
        assert it["status"] in EXPECTED_ACTIVE
        assert "title" in it and "id" in it


@pytest.mark.asyncio
async def test_explore_respects_limit(client, db_session):
    await seed(db_session, "B")

    response = await client.get("/api/v1/tasks/explore?limit=1")
    assert response.status_code == 200, response.text
    items = response.json()["data"]["items"]
    assert len(items) == 1


@pytest.mark.asyncio
async def test_explore_excludes_completed_and_closed(client, db_session):
    _, excluded = await seed(db_session, "C")

    response = await client.get("/api/v1/tasks/explore?limit=20")
    items = response.json()["data"]["items"]
    ids = {it["id"] for it in items}

    assert "completed" not in {it["status"] for it in items}
    assert "closed" not in {it["status"] for it in items}
    assert excluded.isdisjoint(ids)
    for it in items:
        assert it["status"] in EXPECTED_ACTIVE
