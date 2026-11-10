"""Exercise hall filtering and live linked project summaries with isolated SQLite."""

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.v1.demand import router as demand_router
from app.api.v1.task import router as task_router
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.base import Base
from app.models.demand import Demand
from app.models.task import Task


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
    app.dependency_overrides[get_current_user] = lambda: {
        "user_id": "viewer", "role": "super_admin", "jti": "test",
    }
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            yield client, factory, engine
    finally:
        await engine.dispose()


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
