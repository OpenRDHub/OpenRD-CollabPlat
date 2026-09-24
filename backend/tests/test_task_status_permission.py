"""
任务「提交更新」与「推进阶段」权限测试（权限收紧后）

需求：只允许 operator / super_admin / owner_id / leader_id（队长） 操作。
普通成员（如 active builder）、退出/已删除成员、需求方(requester)、无关用户 均拒绝。

端点：
  POST /api/v1/tasks/{task_id}/progress   提交更新
  POST /api/v1/tasks/{task_id}/status     推进阶段

运行：
    .venv/Scripts/python -m pytest tests/test_task_status_permission.py -v -s
"""

import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.config import get_settings
from app.dependencies.auth import get_current_user
from app.main import app
from app.models.task import Task, TaskProgress
from app.models.team import TaskMember
from app.services.task import create_task

_settings = get_settings()
_engine = create_async_engine(_settings.database_url, poolclass=NullPool)
_SessionFactory = async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=True)


@pytest.fixture
async def db_session() -> AsyncSession:
    async with _SessionFactory() as s:
        yield s
        await s.rollback()


def _uid(p: str = "id") -> str:
    return f"{p}-{uuid.uuid4().hex[:8]}"


def _override(user_id: str, role: str):
    async def _ov() -> dict:
        return {"user_id": user_id, "role": role, "jti": f"jti-{user_id}"}
    app.dependency_overrides[get_current_user] = _ov


def _clear_override():
    app.dependency_overrides.pop(get_current_user, None)


API = "/api/v1"
PROGRESS_PATH = f"{API}/tasks/{{task_id}}/progress"
STATUS_PATH = f"{API}/tasks/{{task_id}}/status"


def progress_url(task_id: str) -> str:
    return PROGRESS_PATH.replace("{task_id}", task_id)


def status_url(task_id: str) -> str:
    return STATUS_PATH.replace("{task_id}", task_id)


@pytest.fixture
async def task_scene(db_session: AsyncSession) -> dict:
    """一个 in_progress 任务，附各类成员；返回 task_id 与成员 user_id"""
    task = await create_task(
        db_session,
        title="状态权限测试任务",
        description="测试",
        task_type="工具开发项目",
        priority="medium",
        owner_id="owner-001",
        leader_id="leader-001",   # 队长
    )
    await db_session.refresh(task)
    task_id = task.id
    task.status = "in_progress"   # 进度提交要求 in_progress / pending_acceptance；状态流转 in_progress→pending_acceptance 合法
    await db_session.flush()

    # active 普通共建者（非队长、非负责人）→ 按需求应拒绝
    db_session.add(TaskMember(id=_uid("tm"), task_id=task_id, user_id="member-001",
                              role="队员", duty="开发", source="invite",
                              status="active", is_deleted=0))
    # 退出成员（非 active）
    db_session.add(TaskMember(id=_uid("tm"), task_id=task_id, user_id="left-001",
                              role="队员", duty="开发", source="invite",
                              status="left", is_deleted=0))
    # 已删除成员
    db_session.add(TaskMember(id=_uid("tm"), task_id=task_id, user_id="deleted-001",
                              role="队员", duty="开发", source="invite",
                              status="active", is_deleted=1))
    await db_session.commit()

    await db_session.refresh(task)
    return {"task_id": task_id, "updated_at": task.updated_at}


def _progress_payload(updated_at=None):
    return {
        "stage": "develop",
        "content": "进度更新",
        "file_ids": None,
        "base_stage": "team",
        "expected_updated_at": updated_at.isoformat() if updated_at else None,
    }


def _status_payload():
    # 从 in_progress 合法流转到 pending_acceptance（仅用于授权用例；拒绝用例任意合法值即可）
    return {"status": "pending_acceptance", "reason": None}


# 角色矩阵：
#   owner-001  -> 负责人(owner_id)，角色无关
#   leader-001 -> 队长(leader_id)，角色无关
#   operator-001 / super_admin -> 系统授权
#   member-001 -> active 普通成员（非队长/非负责人）→ 应拒绝
#   builder-001 / left-001 / deleted-001 / requester-001 / stranger-001 -> 应拒绝
@pytest.mark.asyncio
@pytest.mark.parametrize("user_id,role,expected,note", [
    ("owner-001",    "builder",     200, "任务负责人(owner_id)"),
    ("leader-001",   "builder",     200, "任务队长(leader_id)"),
    ("operator-001", "operator",    200, "被授权运营"),
    ("admin-001",    "super_admin", 200, "超级管理员"),
    ("member-001",   "builder",     403, "active 普通成员（非队长）"),
    ("builder-001",  "builder",     403, "无关共建者"),
    ("left-001",     "builder",     403, "退出成员(status!=active)"),
    ("deleted-001",  "builder",     403, "已删除成员(is_deleted=1)"),
    ("requester-001", "requester",   403, "requester 需求方"),
    ("stranger-001", "builder",     403, "无关用户"),
])
async def test_submit_progress_permission(client, task_scene, user_id, role, expected, note):
    """提交更新：仅 owner/leader/operator/super_admin 放行，其余 403"""
    _override(user_id, role)
    try:
        resp = await client.post(
            progress_url(task_scene["task_id"]),
            json=_progress_payload(task_scene["updated_at"]),
        )
    finally:
        _clear_override()
    assert resp.status_code == expected, (
        f"{note} POST progress 期望 {expected}，实际 {resp.status_code}：{resp.text}"
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("user_id,role,expected,note", [
    ("owner-001",    "builder",     200, "任务负责人(owner_id)"),
    ("leader-001",   "builder",     200, "任务队长(leader_id)"),
    ("operator-001", "operator",    200, "被授权运营"),
    ("admin-001",    "super_admin", 200, "超级管理员"),
    ("member-001",   "builder",     403, "active 普通成员（非队长）"),
    ("builder-001",  "builder",     403, "无关共建者"),
    ("left-001",     "builder",     403, "退出成员(status!=active)"),
    ("deleted-001",  "builder",     403, "已删除成员(is_deleted=1)"),
    ("requester-001", "requester",   403, "requester 需求方"),
    ("stranger-001", "builder",     403, "无关用户"),
])
async def test_change_status_permission(client, task_scene, user_id, role, expected, note):
    """推进阶段：仅 owner/leader/operator/super_admin 放行，其余 403"""
    _override(user_id, role)
    try:
        resp = await client.post(status_url(task_scene["task_id"]), json=_status_payload())
    finally:
        _clear_override()
    assert resp.status_code == expected, (
        f"{note} POST status 期望 {expected}，实际 {resp.status_code}：{resp.text}"
    )


@pytest.mark.asyncio
async def test_submit_progress_creates_entry_for_owner(client, task_scene, db_session):
    """负责人提交后，TaskProgress 记录确实被创建"""
    _override("owner-001", "builder")
    try:
        resp = await client.post(
            progress_url(task_scene["task_id"]),
            json=_progress_payload(task_scene["updated_at"]),
        )
    finally:
        _clear_override()
    assert resp.status_code == 200

    rows = (await db_session.execute(
        select(TaskProgress).where(TaskProgress.task_id == task_scene["task_id"])
    )).scalars().all()
    assert any(r.user_id == "owner-001" for r in rows), "负责人提交后应有 TaskProgress 记录"


@pytest.mark.asyncio
async def test_change_status_applies_for_leader(client, task_scene, db_session):
    """队长推进阶段后，任务状态确实变为 pending_acceptance"""
    _override("leader-001", "builder")
    try:
        resp = await client.post(status_url(task_scene["task_id"]), json=_status_payload())
    finally:
        _clear_override()
    assert resp.status_code == 200

    await db_session.refresh(await db_session.get(Task, task_scene["task_id"]))
    refreshed = (await db_session.execute(
        select(Task).where(Task.id == task_scene["task_id"])
    )).scalars().first()
    assert refreshed.status == "pending_acceptance", "队长推进后状态应更新"


@pytest.mark.asyncio
async def test_submit_progress_no_side_effect_for_unauthorized(client, task_scene, db_session):
    """未授权用户提交被拒后，库里不应多出进度记录（防越权写入副作用）"""
    before = (await db_session.execute(
        select(TaskProgress).where(TaskProgress.task_id == task_scene["task_id"])
    )).scalars().all()

    _override("member-001", "builder")
    try:
        resp = await client.post(
            progress_url(task_scene["task_id"]),
            json=_progress_payload(task_scene["updated_at"]),
        )
    finally:
        _clear_override()
    assert resp.status_code == 403

    after = (await db_session.execute(
        select(TaskProgress).where(TaskProgress.task_id == task_scene["task_id"])
        .execution_options(populate_existing=True)
    )).scalars().all()
    assert len(after) == len(before), "越权请求不应产生进度记录"


@pytest.mark.asyncio
async def test_change_status_no_side_effect_for_unauthorized(client, task_scene, db_session):
    """未授权用户推进被拒后，任务状态不应改变"""
    _override("member-001", "builder")
    try:
        resp = await client.post(status_url(task_scene["task_id"]), json=_status_payload())
    finally:
        _clear_override()
    assert resp.status_code == 403

    refreshed = (await db_session.execute(
        select(Task).where(Task.id == task_scene["task_id"]).execution_options(populate_existing=True)
    )).scalars().first()
    assert refreshed.status == "in_progress", "越权推进不应改变任务状态"
