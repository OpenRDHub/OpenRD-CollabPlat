"""Exercise hall filtering and live linked project summaries with isolated SQLite."""

import json

import pytest
from fastapi import FastAPI, Request
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.v1.demand import router as demand_router
from app.api.v1.task import router as task_router
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.admin import SystemLog
from app.models.base import Base
from app.models.demand import Demand
from app.models.task import Task
from app.models.user import User


@pytest.fixture
async def hall_scene():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as db:
        db.add(Task(id="PROJECT-1", title="Project", status="in_progress",
                    team_status="collaborating", stage="develop", leader_id="viewer"))
        for id_, status, conversion, linked in [
            ("REQ-1", "pending_review", None, None),
            ("REQ-2", "communicating", "", None),
            ("REQ-3", "converted", None, "PROJECT-1"),
            ("REQ-4", "archived", "converted", "PROJECT-1"),
            ("REQ-5", "linked", None, "PROJECT-1"),
            ("REQ-6", "converted", "converted", "MISSING"),
            ("REQ-7", "converted", "converted", None),
        ]:
            db.add(Demand(id=id_, title="Demand " + id_, description="Hall test",
                          creator_id="viewer", status=status, convert_status=conversion,
                          linked_task_id=linked, progress=10))
        await db.commit()

    app = FastAPI()
    app.include_router(demand_router, prefix="/api/v1")
    app.include_router(task_router, prefix="/api/v1")

    async def get_test_db():
        async with factory() as db:
            yield db

    app.dependency_overrides[get_db] = get_test_db
    def get_test_user(request: Request):
        return {"user_id": "viewer", "role": request.headers.get("x-test-role", "super_admin"), "jti": "test"}

    app.dependency_overrides[get_current_user] = get_test_user
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            yield client, factory, engine
    finally:
        await engine.dispose()


async def test_submitter_name_is_required_and_survives_conversion(hall_scene, monkeypatch):
    client, factory, _ = hall_scene

    async def demand_id(_db):
        return "REQ-NAMED"

    async def task_id(_db):
        return "PROJECT-NAMED"

    monkeypatch.setattr("app.services.demand.generate_demand_id", demand_id)
    monkeypatch.setattr("app.services.task.generate_task_id", task_id)
    payload = {"title": "New demand", "description": "Description", "urgency": "medium"}
    invalid_payloads = [payload, *(
        {**payload, "submitter_display_name": name} for name in ("", "   ", "长" * 16)
    )]
    for invalid in invalid_payloads:
        assert (await client.post("/api/v1/demands", json=invalid)).status_code == 422

    response = await client.post("/api/v1/demands", json={
        **payload, "submitter_display_name": "  小河  ",
    })
    assert response.status_code == 200, response.text
    demand_path = "/api/v1/demands/REQ-NAMED"
    assert (await client.get(demand_path)).json()["data"]["submitter_display_name"] == "小河"

    response = await client.post(f"{demand_path}/convert", json={
        "title": "New project", "task_type": "工具开发", "priority": "medium",
    })
    assert response.status_code == 200, response.text
    async with factory() as db:
        task = await db.get(Task, "PROJECT-NAMED")
        task.owner_id = "new-owner"
        task.leader_id = "new-leader"
        await db.commit()
    response = await client.get("/api/v1/tasks/PROJECT-NAMED")
    assert response.json()["data"]["initiator_display_name"] == "小河"
    assert (await client.get(demand_path)).json()["data"]["submitter_display_name"] == "小河"


async def test_only_super_admin_can_correct_submitter_name_and_audit_change(hall_scene):
    client, factory, _ = hall_scene
    async with factory() as db:
        demand = await db.get(Demand, "REQ-3")
        demand.submitter_display_name = "旧昵称"
        task = await db.get(Task, "PROJECT-1")
        task.demand_id = demand.id
        await db.commit()

    path = "/api/v1/demands/REQ-3/submitter-name"
    for role in ("requester", "operator"):
        response = await client.patch(path, json={"submitter_display_name": "越权"},
                                      headers={"x-test-role": role})
        assert response.status_code == 403
    for payload in ({"submitter_display_name": " "}, {"submitter_display_name": "长" * 16},
                    {"submitter_display_name": "昵称", "creator_id": "another-user"}):
        assert (await client.patch(path, json=payload)).status_code == 422

    payload = {"submitter_display_name": "  新昵称  "}
    for _ in range(2):
        response = await client.patch(path, json=payload)
        assert response.status_code == 200, response.text
        assert response.json()["data"]["submitter_display_name"] == "新昵称"

    assert (await client.get("/api/v1/demands/REQ-3")).json()["data"]["submitter_display_name"] == "新昵称"
    assert (await client.get("/api/v1/tasks/PROJECT-1")).json()["data"]["initiator_display_name"] == "新昵称"
    async with factory() as db:
        demand = await db.get(Demand, "REQ-3")
        assert demand.creator_id == "viewer"
        logs = (await db.scalars(select(SystemLog).where(
            SystemLog.action == "demand.update_submitter_name",
        ))).all()
        assert len(logs) == 1
        assert (logs[0].actor_id, logs[0].actor_role, logs[0].target_id) == ("viewer", "super_admin", "REQ-3")
        assert json.loads(logs[0].detail) == {"before": "旧昵称", "after": "新昵称"}


async def test_historical_submitter_falls_back_to_account_nickname(hall_scene):
    client, factory, _ = hall_scene
    async with factory() as db:
        db.add(User(id="viewer", platform_id="TEST001", username="test-user",
                    phone="13800000001", password_hash="unused", nickname="历史昵称"))
        task = await db.get(Task, "PROJECT-1")
        task.demand_id = "REQ-3"
        db.add(Task(id="INDEPENDENT", title="Independent"))
        await db.commit()

    assert (await client.get("/api/v1/demands/REQ-3")).json()["data"]["submitter_display_name"] == "历史昵称"
    assert (await client.get("/api/v1/tasks/PROJECT-1")).json()["data"]["initiator_display_name"] == "历史昵称"
    assert (await client.get("/api/v1/tasks/INDEPENDENT")).json()["data"]["initiator_display_name"] is None


async def test_hall_filters_before_pagination_and_preserves_history(hall_scene):
    client, _, _ = hall_scene
    ids = []
    for page in (1, 2):
        response = await client.get("/api/v1/demands", params={
            "hall_only": "true", "page": page, "page_size": 2,
        })
        assert response.status_code == 200, response.text
        data = response.json()["data"]
        assert data["total"] == 3
        ids.extend(item["id"] for item in data["items"])
    assert len(ids) == len(set(ids)) == 3
    assert set(ids) == {"REQ-1", "REQ-2", "REQ-5"}
    for path in ("/api/v1/demands", "/api/v1/me/demands"):
        assert (await client.get(path)).json()["data"]["total"] == 7
    data = (await client.get("/api/v1/demands", params={
        "hall_only": "true", "keyword": "REQ-3",
    })).json()["data"]
    assert data["total"] == 0
    assert data["items"] == []
    data = (await client.get("/api/v1/demands", params={
        "hall_only": "true", "status": "linked",
    })).json()["data"]
    assert data["total"] == 1


async def test_project_progress_follows_task_updates_deletion_and_restore(hall_scene):
    client, _, _ = hall_scene
    for stage in ("develop", "beta", "opensource"):
        task = (await client.get("/api/v1/tasks/PROJECT-1")).json()["data"]
        if stage != task["stage"]:
            response = await client.post("/api/v1/tasks/PROJECT-1/progress", json={
                "stage": stage, "content": "Update stage", "base_stage": task["stage"],
                "expected_updated_at": task["updated_at"],
            })
            assert response.status_code == 200, response.text
        detail = (await client.get("/api/v1/demands/REQ-3")).json()["data"]
        assert detail["status"] == "converted"
        project = detail["linked_project"]
        assert project == {"task_id": "PROJECT-1", "availability": "available",
                           "status": "in_progress", "team_status": "collaborating", "stage": stage}
        for path in ("/api/v1/me/demands", "/api/v1/demands", "/api/v1/demands?hall_only=true"):
            items = (await client.get(path)).json()["data"]["items"]
            assert next(item for item in items if item["id"] == "REQ-5")["linked_project"] == project
        tasks = (await client.get("/api/v1/tasks")).json()["data"]["items"]
        assert tasks[0]["stage"] == stage

    changed = await client.post("/api/v1/tasks/PROJECT-1/status", json={"status": "pending_acceptance"})
    assert changed.status_code == 200, changed.text
    assert (await client.get("/api/v1/demands/REQ-3")).json()["data"]["linked_project"]["status"] == "pending_acceptance"
    deleted = await client.post("/api/v1/tasks/PROJECT-1/delete", json={"reason": "Test"})
    assert deleted.status_code == 200, deleted.text
    detail = (await client.get("/api/v1/demands/REQ-3")).json()["data"]
    assert detail["linked_task_deleted"] is True
    assert detail["linked_project"]["availability"] == "deleted"
    assert detail["linked_project"]["stage"] is None
    assert (await client.get("/api/v1/tasks")).json()["data"]["total"] == 0
    assert (await client.get("/api/v1/demands?hall_only=true")).json()["data"]["total"] == 3
    restored = await client.post("/api/v1/tasks/PROJECT-1/restore")
    assert restored.status_code == 200, restored.text
    detail = (await client.get("/api/v1/demands/REQ-3")).json()["data"]
    assert detail["linked_task_deleted"] is False
    assert detail["linked_project"]["availability"] == "available"
    assert detail["linked_project"]["stage"] == "opensource"


async def test_missing_and_unlinked_history_and_batched_task_query(hall_scene):
    client, _, engine = hall_scene
    for id_, availability in [("REQ-6", "missing"), ("REQ-7", "unlinked")]:
        detail = (await client.get(f"/api/v1/demands/{id_}")).json()["data"]
        assert detail["linked_project"]["availability"] == availability
        assert detail["linked_project"]["status"] is None
        assert detail["progress"] == 10

    statements = []

    def capture(conn, cursor, statement, parameters, context, executemany):
        statements.append(statement)

    event.listen(engine.sync_engine, "before_cursor_execute", capture)
    try:
        response = await client.get("/api/v1/demands")
        assert response.status_code == 200, response.text
    finally:
        event.remove(engine.sync_engine, "before_cursor_execute", capture)
    assert sum("FROM tasks" in statement for statement in statements) == 1
