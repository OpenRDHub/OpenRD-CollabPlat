"""SQLite locally; use the migrated PostgreSQL test database in APP_ENV=testing CI."""
import json
import os

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.v1.task import router as task_router
from app.api.v1.team import router as team_router
from app.config import get_settings
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.admin import SystemLog, UserPermission
from app.models.base import Base
from app.models.demand import Demand
from app.models.task import Task, TaskProgress
from app.models.team import Assignment, TaskMember
from app.models.user import User


@pytest.fixture
async def scene():
    postgres = os.environ.get("APP_ENV") == "testing"
    url = get_settings().database_url if postgres else "sqlite+aiosqlite:///:memory:"
    if postgres:
        assert (make_url(url).database or "").endswith("_test")
    engine = create_async_engine(url)
    if not postgres:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as db:
        db.add(User(id="granted", platform_id="P-GRANTED", username="granted",
                    phone="13000000000", password_hash="unused", role="builder"))
        await db.flush()
        db.add_all([
            UserPermission(user_id="granted", permission_id="task:status"),
            Task(id="REOPEN-1", title="Keep work", status="in_progress",
                 team_status="collaborating", stage="beta", owner_id="owner", leader_id="leader",
                 file_ids='["file-1"]', resource_links='[{"url":"https://example.com"}]'),
            TaskMember(id="MEM-1", task_id="REOPEN-1", user_id="member", role="dev", status="active"),
            TaskProgress(id="PROG-1", task_id="REOPEN-1", user_id="leader",
                         stage="beta", content="Keep history", next_plan="Keep plan"),
            Assignment(id="ASSIGN-1", task_id="REOPEN-1", title="Keep assignment", owner_id="member"),
            Demand(id="DEM-1", title="Keep demand", description="Source", creator_id="owner",
                   status="converted", linked_task_id="REOPEN-1", progress=75),
        ])
        await db.commit()
    identity = {"user_id": "leader", "role": "builder", "jti": "test"}
    api = FastAPI()
    api.include_router(task_router, prefix="/api/v1")
    api.include_router(team_router, prefix="/api/v1")

    async def database():
        async with factory() as db:
            yield db

    api.dependency_overrides[get_db] = database
    api.dependency_overrides[get_current_user] = lambda: dict(identity)
    try:
        async with AsyncClient(transport=ASGITransport(app=api, raise_app_exceptions=False),
                               base_url="http://test") as client:
            yield client, factory, identity
    finally:
        await engine.dispose()


PATH = "/api/v1/tasks/REOPEN-1/status"


@pytest.mark.parametrize("user_id,role,expected", [
    ("leader", "builder", 200), ("owner", "requester", 200),
    ("granted", "builder", 200), ("operator", "operator", 200),
    ("admin", "super_admin", 200), ("member", "builder", 403),
    ("stranger", "builder", 403), ("requester", "requester", 403),
])
async def test_reopen_permissions_and_history(scene, user_id, role, expected):
    client, factory, identity = scene
    identity.update(user_id=user_id, role=role)
    response = await client.post(PATH, json={"status": "recruiting", "reason": "  补充成员  "})
    assert response.status_code == expected, response.text
    async with factory() as db:
        task = await db.get(Task, "REOPEN-1")
        assert (task.status, task.team_status) == (
            ("recruiting", "forming") if expected == 200 else ("in_progress", "collaborating")
        )
        assert task.stage == "beta"
        assert task.file_ids == '["file-1"]'
        assert task.resource_links == '[{"url":"https://example.com"}]'
        assert (task.owner_id, task.leader_id) == ("owner", "leader")
        assert (await db.get(TaskMember, "MEM-1")).status == "active"
        progress = await db.get(TaskProgress, "PROG-1")
        assert (progress.stage, progress.content, progress.next_plan) == ("beta", "Keep history", "Keep plan")
        assert (await db.get(Assignment, "ASSIGN-1")).title == "Keep assignment"
        demand = await db.get(Demand, "DEM-1")
        assert (demand.status, demand.progress, demand.linked_task_id) == ("converted", 75, "REOPEN-1")
        logs = (await db.scalars(select(SystemLog).where(SystemLog.target_id == "REOPEN-1"))).all()
        assert len(logs) == (1 if expected == 200 else 0)
        if logs:
            assert (logs[0].actor_id, logs[0].actor_role, logs[0].action) == (
                user_id, role, "task.reopen_recruitment"
            )
            assert json.loads(logs[0].detail) == {
                "reason": "补充成员", "from_status": "in_progress", "to_status": "recruiting",
                "from_team_status": "collaborating", "to_team_status": "forming",
            }
    if expected == 200:
        identity.update(user_id="new-builder", role="builder")
        joined = await client.post("/api/v1/tasks/REOPEN-1/join-applications", json={"role": "dev"})
        assert joined.status_code == 200, joined.text


@pytest.mark.parametrize("payload", [
    {"status": "recruiting"}, {"status": "recruiting", "reason": None},
    {"status": "recruiting", "reason": ""}, {"status": "recruiting", "reason": " \t\n "},
    {"status": "recruiting", "reason": "字" * 501},
])
async def test_reopen_requires_reason_without_writes(scene, payload):
    client, factory, _ = scene
    response = await client.post(PATH, json=payload)
    assert response.status_code == 400, response.text
    async with factory() as db:
        assert (await db.get(Task, "REOPEN-1")).status == "in_progress"
        assert not (await db.scalars(select(SystemLog))).all()


async def test_reason_boundary_and_repeated_reopen(scene):
    client, factory, _ = scene
    payload = {"status": "recruiting", "reason": "字" * 500}
    assert (await client.post(PATH, json=payload)).status_code == 200
    assert (await client.post(PATH, json=payload)).status_code == 400
    async with factory() as db:
        assert len((await db.scalars(select(SystemLog))).all()) == 1


@pytest.mark.parametrize("initial", ["team_ready", "pending_acceptance", "completed", "closed"])
async def test_other_states_cannot_reopen(scene, initial):
    client, factory, _ = scene
    async with factory() as db:
        task = await db.get(Task, "REOPEN-1")
        task.status = initial
        await db.commit()
    assert (await client.post(PATH, json={"status": "recruiting", "reason": "test"})).status_code == 400
    async with factory() as db:
        assert (await db.get(Task, "REOPEN-1")).status == initial
        assert not (await db.scalars(select(SystemLog))).all()


async def test_audit_failure_rolls_back_status(scene, monkeypatch):
    client, factory, _ = scene

    async def fail_log(*args, **kwargs):
        raise RuntimeError("audit unavailable")

    monkeypatch.setattr("app.services.admin.create_system_log", fail_log)
    response = await client.post(PATH, json={"status": "recruiting", "reason": "test"})
    assert response.status_code == 500
    async with factory() as db:
        task = await db.get(Task, "REOPEN-1")
        assert (task.status, task.team_status) == ("in_progress", "collaborating")
        assert not (await db.scalars(select(SystemLog))).all()


async def test_existing_forward_transition_still_works_without_reason(scene):
    client, _, _ = scene
    response = await client.post(PATH, json={"status": "pending_acceptance"})
    assert response.status_code == 200, response.text
    assert response.json()["data"]["team_status"] == "collaborating"
