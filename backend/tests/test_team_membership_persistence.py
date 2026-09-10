import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.main import app
from app.models.task import Task
from app.models.team import JoinApplication, TaskMember


def _id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


@pytest.mark.asyncio
async def test_approved_member_survives_reload_and_appears_in_my_tasks(
    client: AsyncClient,
    db_session: AsyncSession,
):
    leader_id = _id("leader")
    member_id = _id("member")
    task_id = _id("TASK")
    application_id = _id("application")
    task = Task(
        id=task_id,
        title="B09 成员关系持久化验收",
        description="审批后刷新、重登仍可读取成员关系",
        status="recruiting",
        team_status="forming",
        progress=0,
        leader_id=leader_id,
    )
    application = JoinApplication(
        id=application_id,
        task_id=task_id,
        user_id=member_id,
        role="后端开发",
        status="pending",
    )
    db_session.add_all([task, application])
    await db_session.commit()

    identity = {"user_id": leader_id, "role": "operator", "jti": "test-b09"}

    async def current_user() -> dict:
        return dict(identity)

    app.dependency_overrides[get_current_user] = current_user
    try:
        approved = await client.post(
            f"/api/v1/tasks/{task_id}/join-applications/{application_id}/approve",
            json={"duty": "负责成员持久化"},
        )
        assert approved.status_code == 200, approved.text

        persisted = await db_session.execute(
            select(TaskMember).where(
                TaskMember.task_id == task_id,
                TaskMember.user_id == member_id,
                TaskMember.status == "active",
                TaskMember.is_deleted == 0,
            )
        )
        member = persisted.scalar_one()
        assert member.role == "后端开发"
        assert member.duty == "负责成员持久化"

        # 模拟退出后以获批成员身份重新登录，并连续读取两次（页面刷新）。
        identity.update(user_id=member_id, role="builder")
        for _ in range(2):
            team_response = await client.get(f"/api/v1/tasks/{task_id}/team")
            assert team_response.status_code == 200, team_response.text
            members = team_response.json()["data"]["members"]
            assert any(item["user_id"] == member_id for item in members)

            my_tasks_response = await client.get("/api/v1/me/tasks?page=1&page_size=100")
            assert my_tasks_response.status_code == 200, my_tasks_response.text
            my_tasks = my_tasks_response.json()["data"]["items"]
            joined_task = next(item for item in my_tasks if item["id"] == task_id)
            assert joined_task["my_role"] == "后端开发"
            assert joined_task["my_stage"] == "pending"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_approval_reuses_existing_member_instead_of_creating_duplicate(
    client: AsyncClient,
    db_session: AsyncSession,
):
    leader_id = _id("leader")
    member_id = _id("member")
    task_id = _id("TASK")
    application_id = _id("application")
    db_session.add_all(
        [
            Task(
                id=task_id,
                title="B09 重复成员保护",
                status="recruiting",
                team_status="forming",
                progress=25,
                leader_id=leader_id,
            ),
            TaskMember(
                id=_id("task-member"),
                task_id=task_id,
                user_id=member_id,
                role="测试",
                status="inactive",
            ),
            JoinApplication(
                id=application_id,
                task_id=task_id,
                user_id=member_id,
                role="测试工程师",
                status="pending",
            ),
        ]
    )
    await db_session.commit()

    async def current_user() -> dict:
        return {"user_id": leader_id, "role": "operator", "jti": "test-b09-duplicate"}

    app.dependency_overrides[get_current_user] = current_user
    try:
        response = await client.post(
            f"/api/v1/tasks/{task_id}/join-applications/{application_id}/approve",
            json={"duty": "重新激活"},
        )
        assert response.status_code == 200, response.text
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    count = await db_session.scalar(
        select(func.count()).select_from(TaskMember).where(
            TaskMember.task_id == task_id,
            TaskMember.user_id == member_id,
            TaskMember.is_deleted == 0,
        )
    )
    assert count == 1
    member = await db_session.scalar(
        select(TaskMember).where(TaskMember.task_id == task_id, TaskMember.user_id == member_id)
    )
    assert member is not None
    assert member.status == "active"
    assert member.role == "测试工程师"
    assert member.duty == "重新激活"
