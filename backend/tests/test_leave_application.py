import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.main import app
from app.models.task import Task
from app.models.team import LeaveApplication, TaskMember


def _id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


@pytest.mark.asyncio
async def test_member_must_apply_and_leader_approve_before_leaving(client: AsyncClient, db_session: AsyncSession):
    leader_id, member_id, task_id = _id("leader"), _id("member"), _id("TASK")
    member = TaskMember(id=_id("membership"), task_id=task_id, user_id=member_id, role="前端开发", status="active")
    db_session.add_all([
        Task(id=task_id, title="退出审批测试", status="team_ready", team_status="collaborating", leader_id=leader_id),
        member,
    ])
    await db_session.commit()
    identity = {"user_id": member_id, "role": "builder", "jti": "leave-test"}

    async def current_user() -> dict:
        return dict(identity)

    app.dependency_overrides[get_current_user] = current_user
    try:
        submitted = await client.post(f"/api/v1/tasks/{task_id}/leave-applications", json={"reason": "时间安排变化，需要交接当前工作"})
        assert submitted.status_code == 200, submitted.text
        application_id = submitted.json()["data"]["id"]
        await db_session.refresh(member)
        assert member.status == "active"

        duplicate = await client.post(f"/api/v1/tasks/{task_id}/leave-applications", json={"reason": "重复申请"})
        assert duplicate.status_code == 409

        identity.update(user_id=_id("admin"), role="super_admin")
        admin_attempt = await client.post(
            f"/api/v1/tasks/{task_id}/leave-applications/{application_id}/approve"
        )
        assert admin_attempt.status_code == 403

        identity.update(user_id=leader_id, role="builder")
        team_before = await client.get(f"/api/v1/tasks/{task_id}/team")
        assert any(item["id"] == application_id for item in team_before.json()["data"]["leave_applications"])
        approved = await client.post(f"/api/v1/tasks/{task_id}/leave-applications/{application_id}/approve")
        assert approved.status_code == 200, approved.text
        await db_session.refresh(member)
        assert member.status == "left"
        application = await db_session.scalar(select(LeaveApplication).where(LeaveApplication.id == application_id))
        assert application.status == "approved"
        team_after = await client.get(f"/api/v1/tasks/{task_id}/team")
        assert all(item["user_id"] != member_id for item in team_after.json()["data"]["members"])
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_leader_cannot_request_leave_before_transfer(client: AsyncClient, db_session: AsyncSession):
    leader_id, task_id = _id("leader"), _id("TASK")
    db_session.add_all([
        Task(id=task_id, title="队长退出限制", status="team_ready", leader_id=leader_id),
        TaskMember(id=_id("membership"), task_id=task_id, user_id=leader_id, role="队长", status="active"),
    ])
    await db_session.commit()

    async def current_user() -> dict:
        return {"user_id": leader_id, "role": "builder", "jti": "leader-leave-test"}

    app.dependency_overrides[get_current_user] = current_user
    try:
        response = await client.post(f"/api/v1/tasks/{task_id}/leave-applications", json={"reason": "准备退出"})
        assert response.status_code == 400
        assert response.json()["detail"] == "队长退出前必须先转移队长身份"
    finally:
        app.dependency_overrides.pop(get_current_user, None)
