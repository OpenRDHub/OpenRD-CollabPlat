"""B13 补充：communicate / close 状态流转接口的权限与状态机测试"""
import pytest

from app.dependencies.auth import get_current_user
from app.main import app
from app.services.demand import create_demand


@pytest.fixture
async def pending_demand(client, db_session):
    return await create_demand(
        db_session,
        creator_id="creator-001",
        actor_role="requester",
        title="状态流转测试需求",
        description="临时",
        urgency="normal",
    )


def _override(user_id: str, role: str):
    async def _ov() -> dict:
        return {"user_id": user_id, "role": role, "jti": f"jti-{user_id}"}
    app.dependency_overrides[get_current_user] = _ov


@pytest.mark.asyncio
async def test_communicate_requires_update_permission(client, pending_demand):
    _override("stranger-001", "builder")
    try:
        resp = await client.post(f"/api/v1/demands/{pending_demand.id}/communicate")
    finally:
        app.dependency_overrides.pop(get_current_user, None)
    assert resp.status_code == 403, resp.text


@pytest.mark.asyncio
async def test_communicate_transitions_pending_review_to_communicating(client, pending_demand):
    _override("op-001", "operator")
    try:
        resp = await client.post(f"/api/v1/demands/{pending_demand.id}/communicate")
    finally:
        app.dependency_overrides.pop(get_current_user, None)
    assert resp.status_code == 200, resp.text
    assert resp.json()["data"]["status"] == "communicating"


@pytest.mark.asyncio
async def test_repeated_communicate_returns_400(client, pending_demand):
    _override("op-001", "operator")
    try:
        first = await client.post(f"/api/v1/demands/{pending_demand.id}/communicate")
        second = await client.post(f"/api/v1/demands/{pending_demand.id}/communicate")
    finally:
        app.dependency_overrides.pop(get_current_user, None)
    assert first.status_code == 200
    assert second.status_code == 400, second.text


@pytest.mark.asyncio
async def test_close_requires_archive_permission(client, pending_demand):
    _override("stranger-001", "builder")
    try:
        resp = await client.post(f"/api/v1/demands/{pending_demand.id}/close")
    finally:
        app.dependency_overrides.pop(get_current_user, None)
    assert resp.status_code == 403, resp.text


@pytest.mark.asyncio
async def test_close_then_reclose_returns_400(client, pending_demand):
    _override("op-001", "operator")
    try:
        closed = await client.post(f"/api/v1/demands/{pending_demand.id}/close")
        reclosed = await client.post(f"/api/v1/demands/{pending_demand.id}/close")
    finally:
        app.dependency_overrides.pop(get_current_user, None)
    assert closed.status_code == 200, closed.text
    assert closed.json()["data"]["status"] == "closed"
    assert reclosed.status_code == 400, reclosed.text
