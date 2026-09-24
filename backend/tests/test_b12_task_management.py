import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.main import app
from app.models.task import Task, TaskStage
from app.models.team import TaskMember


def _task(task_id: str, title: str, status: str, **owners: str) -> Task:
    return Task(
        id=task_id,
        title=title,
        description=None,
        status=status,
        team_status="forming",
        stage=TaskStage.TEAM,
        **owners,
    )


@pytest.mark.asyncio
async def test_my_tasks_returns_only_active_relationships_with_role_and_stage(
    client: AsyncClient,
    db_session: AsyncSession,
):
    user_id = "b12-user"
    db_session.add_all(
        [
            _task("B12-OWNER", "我发布的任务", "recruiting", owner_id=user_id),
            _task("B12-LEADER", "我负责的任务", "team_ready", leader_id=user_id),
            _task("B12-MEMBER", "我参与的任务", "in_progress"),
            _task("B12-INACTIVE", "已退出的任务", "pending_acceptance"),
            _task("B12-DELETED", "已删除的成员关系", "completed"),
            _task("B12-OTHER", "无关任务", "closed", owner_id="other-user"),
            TaskMember(
                id="b12-member-active",
                task_id="B12-MEMBER",
                user_id=user_id,
                role="前端开发",
                status="active",
            ),
            TaskMember(
                id="b12-member-left",
                task_id="B12-INACTIVE",
                user_id=user_id,
                role="测试",
                status="inactive",
            ),
            TaskMember(
                id="b12-member-deleted",
                task_id="B12-DELETED",
                user_id=user_id,
                role="产品",
                status="active",
                is_deleted=1,
            ),
        ]
    )
    await db_session.commit()

    identity = {"user_id": user_id, "role": "builder", "jti": "test-b12-my-tasks"}

    async def current_user() -> dict:
        return dict(identity)

    app.dependency_overrides[get_current_user] = current_user
    try:
        response = await client.get("/api/v1/me/tasks?page=1&page_size=100")
        assert response.status_code == 200, response.text
        payload = response.json()["data"]
        assert payload["total"] == 3
        by_id = {item["id"]: item for item in payload["items"]}
        assert set(by_id) == {"B12-OWNER", "B12-LEADER", "B12-MEMBER"}
        assert (by_id["B12-OWNER"]["my_role"], by_id["B12-OWNER"]["my_stage"]) == ("需求方", "pending")
        assert (by_id["B12-LEADER"]["my_role"], by_id["B12-LEADER"]["my_stage"]) == ("任务队长", "pending")
        assert (by_id["B12-MEMBER"]["my_role"], by_id["B12-MEMBER"]["my_stage"]) == ("前端开发", "doing")

        filtered = await client.get("/api/v1/me/tasks?status=in_progress&keyword=参与")
        assert filtered.status_code == 200, filtered.text
        assert [item["id"] for item in filtered.json()["data"]["items"]] == ["B12-MEMBER"]

        identity["user_id"] = "b12-stranger"
        empty = await client.get("/api/v1/me/tasks")
        assert empty.status_code == 200, empty.text
        assert empty.json()["data"]["items"] == []
        assert empty.json()["data"]["total"] == 0
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_task_management_uses_real_title_status_and_progress_contracts(
    client: AsyncClient,
    db_session: AsyncSession,
):
    task = _task("B12-MANAGE", "修复前标题", "recruiting", owner_id="b12-owner")
    db_session.add(task)
    await db_session.commit()

    async def current_user() -> dict:
        return {"user_id": "b12-operator", "role": "operator", "jti": "test-b12-management"}

    app.dependency_overrides[get_current_user] = current_user
    try:
        too_large = await client.get("/api/v1/tasks?page=1&page_size=200")
        assert too_large.status_code == 422

        invalid = await client.post(
            "/api/v1/tasks/B12-MANAGE/status",
            json={"status": "in_progress"},
        )
        assert invalid.status_code == 400

        ready = await client.post(
            "/api/v1/tasks/B12-MANAGE/status",
            json={"status": "team_ready"},
        )
        assert ready.status_code == 200, ready.text

        renamed = await client.patch(
            "/api/v1/tasks/B12-MANAGE",
            json={"title": "修复后标题"},
        )
        assert renamed.status_code == 200, renamed.text
        assert renamed.json()["data"]["title"] == "修复后标题"

        started = await client.post(
            "/api/v1/tasks/B12-MANAGE/status",
            json={"status": "in_progress"},
        )
        assert started.status_code == 200, started.text

        progress = await client.post(
            "/api/v1/tasks/B12-MANAGE/progress",
            json={
                "stage": "develop",
                "content": "B12 管理端真实更新验收",
                "base_stage": "team",
                "expected_updated_at": started.json()["data"]["updated_at"],
            },
        )
        assert progress.status_code == 200, progress.text
        assert progress.json()["data"]["stage"] == "develop"
        assert progress.json()["data"]["content"] == "B12 管理端真实更新验收"

        detail = await client.get("/api/v1/tasks/B12-MANAGE")
        assert detail.status_code == 200, detail.text
        assert detail.json()["data"]["status"] == "in_progress"
        assert detail.json()["data"]["stage"] == "develop"
    finally:
        app.dependency_overrides.pop(get_current_user, None)
