"""Run with pytest --confcutdir=tests/isolated tests/isolated/test_recruitment_approval.py."""

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.v1.task import router as task_router
from app.api.v1.team import router as team_router
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.base import Base
from app.models.task import Task
from app.models.team import TaskMember


@pytest.mark.parametrize("reactivate", [False, True])
async def test_approval_keeps_recruiting_until_leader_confirms(reactivate):
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as db:
        db.add(Task(id="RECRUIT-1", title="Recruitment", status="recruiting",
                    team_status="forming", stage="team", leader_id="leader"))
        if reactivate:
            db.add(TaskMember(id="old-member", task_id="RECRUIT-1", user_id="first",
                              role="成员", status="inactive"))
        await db.commit()

    app = FastAPI()
    app.include_router(task_router, prefix="/api/v1")
    app.include_router(team_router, prefix="/api/v1")
    identity = {"user_id": "first", "role": "builder", "jti": "test"}

    async def get_test_db():
        async with factory() as db:
            yield db

    app.dependency_overrides[get_db] = get_test_db
    app.dependency_overrides[get_current_user] = lambda: dict(identity)
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            for user_id in ("first", "second"):
                identity["user_id"] = user_id
                applied = await client.post("/api/v1/tasks/RECRUIT-1/join-applications",
                                            json={"role": "共建者"})
                assert applied.status_code == 200, applied.text
                application_id = applied.json()["data"]["id"]
                identity["user_id"] = "leader"
                approved = await client.post(
                    f"/api/v1/tasks/RECRUIT-1/join-applications/{application_id}/approve",
                    json={},
                )
                assert approved.status_code == 200, approved.text
                assert approved.json()["data"]["status"] == "active"
                async with factory() as db:
                    task = await db.get(Task, "RECRUIT-1")
                    assert task.status == "recruiting"
                    assert task.team_status == "forming"
                    assert task.stage == "team"

            # An ordinary member cannot end recruitment; the leader explicitly confirms.
            identity["user_id"] = "second"
            denied = await client.post("/api/v1/tasks/RECRUIT-1/status",
                                       json={"status": "team_ready"})
            assert denied.status_code == 403, denied.text
            identity["user_id"] = "leader"
            confirmed = await client.post("/api/v1/tasks/RECRUIT-1/status",
                                          json={"status": "team_ready"})
            assert confirmed.status_code == 200, confirmed.text
            async with factory() as db:
                task = await db.get(Task, "RECRUIT-1")
                assert task.status == "team_ready"
                assert task.team_status == "collaborating"
                assert task.stage == "team"

            identity["user_id"] = "third"
            stopped = await client.post("/api/v1/tasks/RECRUIT-1/join-applications",
                                        json={"role": "共建者"})
            assert stopped.status_code == 400, stopped.text
    finally:
        await engine.dispose()
