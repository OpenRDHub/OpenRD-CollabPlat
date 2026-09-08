"""
任务进度提交权限测试（PR3，TDD 红灯先行）

漏洞：post_progress 仅校验系统权限 task:update，未做数据归属校验，
     导致任意持有 task:update 的角色（含无关 builder）可篡改任意任务进度。

修复后判据：
  可提交：队长 / active 成员 / 被授权运营或超管
  不可提交：builder(非成员) / 退出成员 / requester(需求方) / 无关用户

运行：
    .venv/Scripts/python -m pytest tests/test_progress_permission.py -v -s
"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.config import get_settings
from app.dependencies.auth import get_current_user
from app.main import app
from app.models.task import Task, TaskProgress
from app.models.team import TaskMember
from app.services.task import create_task

try:
    from app.models.demand import Demand
except ImportError:
    Demand = None   # 测试不依赖 demand 表也可，progress 只依赖 task


_settings = get_settings()
_engine = create_async_engine(_settings.database_url, poolclass=NullPool)
_SessionFactory = async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=True)


@pytest.fixture
async def db_session() -> AsyncSession:
    async with _SessionFactory() as s:
        yield s
        await s.rollback()


# 角色发现
try:
    from app.core.permissions import ROLE_PERMISSIONS
except ImportError:
    try:
        from app.permissions import ROLE_PERMISSIONS
    except ImportError:
        ROLE_PERMISSIONS = {}


def _role_with(perm: str) -> str | None:
    for role, perms in (ROLE_PERMISSIONS or {}).items():
        if perm in perms:
            return role
    return None


# builder：需有 task:update（能越过系统层），但不是任务成员 —— 这是漏洞触发条件
BUILDER_ROLE = "builder"
UPDATE_HOLDER = _role_with("task:update")   # 兜底：若一个角色都找不到就用 builder
print(f"[info] BUILDER_ROLE={BUILDER_ROLE}, UPDATE_HOLDER(有task:update)={UPDATE_HOLDER}")


API = "/api/v1"
PROGRESS_PATH = f"{API}/tasks/{{task_id}}/progress"


def progress_url(task_id: str) -> str:
    return PROGRESS_PATH.replace("{task_id}", task_id)


def _uid(p: str = "id") -> str:
    return f"{p}-{uuid.uuid4().hex[:8]}"


def _override(user_id: str, role: str):
    async def _ov() -> dict:
        return {"user_id": user_id, "role": role, "jti": f"jti-{user_id}"}
    app.dependency_overrides[get_current_user] = _ov


def _clear_override():
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
async def task_scene(db_session: AsyncSession) -> dict:
    """一个 recruiting 任务，附各类成员；返回 task_id 与成员 user_id"""
    task = await create_task(
        db_session,
        title="进度权限测试任务",
        description="测试",
        task_type="工具开发项目",
        priority="medium",
        owner_id="owner-001",
        leader_id="leader-001",   # 队长
    )
    await db_session.refresh(task)
    task_id = task.id
    task.status = "in_progress"   # 进度提交要求 in_progress / pending_acceptance
    await db_session.flush()

    # active 正式成员
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

    return {"task_id": task_id}


def _payload():
    return {"progress": 50, "content": "进度更新", "file_ids": None}


@pytest.mark.asyncio
@pytest.mark.parametrize("user_id,role,expected,note", [
    ("leader-001",   "super_admin", 200, "任务队长"),           # 队长
    ("member-001",   BUILDER_ROLE,  200, "active 正式成员"),     # active 成员
    ("operator-001", "operator",    200, "被授权运营"),
    ("admin-001",    "super_admin", 200, "超级管理员"),
    ("builder-001",  BUILDER_ROLE,  403, "builder 非成员共建者"),   # ← 漏洞核心
    ("left-001",     BUILDER_ROLE,  403, "退出成员(status!=active)"),
    ("deleted-001",  BUILDER_ROLE,  403, "已删除成员(is_deleted=1)"),
    ("requester-001", "requester",  403, "requester 需求方非成员"),
    ("stranger-001", BUILDER_ROLE,  403, "无关用户"),
])
async def test_submit_progress_permission(client, task_scene, user_id, role, expected, note):
    """
    核心测试：
    - builder/退出/删除/requester/无关 → 403（漏洞复现 + 回归）
    - 队长/active成员/运营/超管 → 200
    """
    _override(user_id, role)
    try:
        resp = await client.post(progress_url(task_scene["task_id"]), json=_payload())
    finally:
        _clear_override()

    assert resp.status_code == expected, (
        f"{note} POST progress 期望 {expected}，实际 {resp.status_code}：{resp.text}"
    )


@pytest.mark.asyncio
async def test_progress_creates_entry_for_authorized(client, task_scene, db_session):
    """授权成员提交后，TaskProgress 记录确实被创建（验证 not None + 写入库）"""
    _override("member-001", BUILDER_ROLE)
    try:
        resp = await client.post(progress_url(task_scene["task_id"]), json=_payload())
    finally:
        _clear_override()
    assert resp.status_code == 200

    await db_session.execute(
        select(TaskProgress).where(
            TaskProgress.task_id == task_scene["task_id"],
            TaskProgress.user_id == "member-001",
        ).execution_options(populate_existing=True)
    )
    rows = (await db_session.execute(
        select(TaskProgress).where(TaskProgress.task_id == task_scene["task_id"])
    )).scalars().all()
    assert any(r.user_id == "member-001" for r in rows), "授权成员提交后应有 TaskProgress 记录"


@pytest.mark.asyncio
async def test_progress_not_created_for_unauthorized(client, task_scene, db_session):
    """未授权用户提交被拒后，库里不应多出记录（防越权写入副作用）"""
    before = (await db_session.execute(
        select(TaskProgress).where(TaskProgress.task_id == task_scene["task_id"])
    )).scalars().all()

    _override("builder-001", BUILDER_ROLE)
    try:
        resp = await client.post(progress_url(task_scene["task_id"]), json=_payload())
    finally:
        _clear_override()
    assert resp.status_code == 403

    after = (await db_session.execute(
        select(TaskProgress).where(TaskProgress.task_id == task_scene["task_id"])
        .execution_options(populate_existing=True)
    )).scalars().all()
    assert len(after) == len(before), "越权请求不应产生进度记录"