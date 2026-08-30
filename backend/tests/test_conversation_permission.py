r"""
沟通区权限控制测试（PR2）

覆盖链路：
  DemandDetailView.vue（前端蒙版 canViewConversation）
    → GET/POST /api/v1/demands/{demand_id}/replies
    → demand.py::can_access_demand（系统层 demand:view + 数据层守卫）
        └─ team.py::is_task_member_or_leader（队长 / 正式队员 active+未删除）
            └─ task.py（create_task，demand.linked_task_id 桥梁）
    → POST /replies/{reply_id}/revoke（独立撤回权限，仅需登录）

运行：
    .venv/Scripts/python -m pytest tests/test_conversation_permission.py -v -s
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
from app.models.demand import Demand
from app.models.team import TaskMember          # demand.py 确认路径
from app.services.demand import create_reply
from app.services.task import create_task

try:                                             # Reply 模型（查 reply_id 用）
    from app.models.demand import DemandReply
except ImportError:
    from app.models.reply import DemandReply


# ---------------- 1. DB session ----------------
_settings = get_settings()
_engine = create_async_engine(_settings.database_url, poolclass=NullPool)
_SessionFactory = async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=True)


@pytest.fixture
async def db_session() -> AsyncSession:
    async with _SessionFactory() as s:
        yield s
        await s.rollback()


# ---------------- 2. 角色发现（适配你们 ROLE_PERMISSIONS） ----------------
try:
    from app.core.permissions import ROLE_PERMISSIONS
except ImportError:
    try:
        from app.permissions import ROLE_PERMISSIONS
    except ImportError:
        ROLE_PERMISSIONS = {}


def _role_with(perm: str, exclude=()):
    for role, perms in (ROLE_PERMISSIONS or {}).items():
        if perm in perms and role not in exclude:
            return role
    return None


NORMAL_ROLE = _role_with("demand:view", exclude=("operator", "super_admin")) or "requester"
NOPERM_ROLE = next((r for r in ("guest", "viewer", "anonymous")
                    if r not in (ROLE_PERMISSIONS or {})), "guest")
print(f"[info] NORMAL_ROLE={NORMAL_ROLE}（有 demand:view 的普通角色，用于隔离 creator/owner/member 分支）")
print(f"[info] NOPERM_ROLE={NOPERM_ROLE}（无 demand:view，用于测系统层拦截）")


# ---------------- 3. 路由 ----------------
API = "/api/v1"
REPLIES_PATH = f"{API}/demands/{{demand_id}}/replies"
REVOKE_PATH = f"{API}/demands/{{demand_id}}/replies/{{reply_id}}/revoke"
DETAIL_PATH = f"{API}/demands/{{demand_id}}"
THREAD_ID = "thread-001"          # 统一用字符串，避免 None 触发 422 / NOT NULL


def replies_url(did):  return REPLIES_PATH.replace("{demand_id}", did)
def detail_url(did):   return DETAIL_PATH.replace("{demand_id}", did)
def revoke_url(did, rid):
    return REVOKE_PATH.replace("{demand_id}", did).replace("{reply_id}", rid)
def _uid(p="id"):      return f"{p}-{uuid.uuid4().hex[:8]}"


def _override(user_id: str, role: str):
    async def _ov() -> dict:
        return {"user_id": user_id, "role": role, "jti": f"jti-{user_id}"}
    app.dependency_overrides[get_current_user] = _ov


def _clear_override():
    app.dependency_overrides.pop(get_current_user, None)


# ---------------- 4. 场景：需求 + 关联任务 + 各类成员 + 两条消息 ----------------
@pytest.fixture
async def scenario(db_session: AsyncSession) -> dict:
    demand_id = _uid("demand")
    demand = Demand(
        id=demand_id,
        title="沟通区权限测试需求",
        description="用于验证沟通区权限矩阵",   # NOT NULL，必须传
        urgency="medium",
        status="communicating",
        creator_id="creator-001",
        owner_id="owner-pm-001",
    )
    db_session.add(demand)
    await db_session.flush()

    # 建任务（demand → task 桥梁）
    task = await create_task(
        db_session,
        demand_id=demand_id,
        title="关联任务",
        description=demand.description,
        task_type="工具开发项目",
        priority="medium",
        scope=None,
        acceptance_criteria=None,
        planned_end_time=None,
        owner_id="owner-pm-001",
        leader_id="leader-001",
    )
    await db_session.refresh(task)      # 防 expire_on_commit 下同步取 .id 报 MissingGreenlet
    task_id = task.id

    # 正式队员：active + 未删除
    db_session.add(TaskMember(id=_uid("tm"), task_id=task_id, user_id="member-001",
                              role="队员", duty="开发", source="invite",
                              status="active", is_deleted=0))
    # 非 active 队员
    db_session.add(TaskMember(id=_uid("tm"), task_id=task_id, user_id="inactive-001",
                              role="队员", duty="开发", source="invite",
                              status="left", is_deleted=0))
    # 已删除队员
    db_session.add(TaskMember(id=_uid("tm"), task_id=task_id, user_id="deleted-001",
                              role="队员", duty="开发", source="invite",
                              status="active", is_deleted=1))

    demand.linked_task_id = task_id     # 桥梁：需求 → 任务
    await db_session.commit()

    # 造消息（thread_id 传字符串，匹配前端真实行为）
    await create_reply(db_session, demand_id=demand_id, thread_id=THREAD_ID,
                       sender_id="member-001", sender_role=NORMAL_ROLE,
                       content="成员发的消息", attachment_ids=None)
    await create_reply(db_session, demand_id=demand_id, thread_id=THREAD_ID,
                       sender_id="creator-001", sender_role=NORMAL_ROLE,
                       content="创建者发的消息", attachment_ids=None)
    await db_session.commit()

    rows = (await db_session.execute(
        select(DemandReply).where(DemandReply.demand_id == demand_id)
    )).scalars().all()
    member_reply_id = next(r.id for r in rows if r.sender_id == "member-001")
    creator_reply_id = next(r.id for r in rows if r.sender_id == "creator-001")

    return {"demand_id": demand_id, "task_id": task_id,
            "member_reply_id": member_reply_id, "creator_reply_id": creator_reply_id}


# ---------------- 5. GET replies 权限矩阵 ----------------
@pytest.mark.asyncio
@pytest.mark.parametrize("user_id,role,expected,note", [
    ("creator-001",  NORMAL_ROLE,   200, "需求创建者(creator_id)"),
    ("owner-pm-001", NORMAL_ROLE,   200, "被分配PM(owner_id)"),
    ("operator-001", "operator",    200, "运营"),
    ("admin-001",    "super_admin", 200, "超管"),
    ("leader-001",   NORMAL_ROLE,   200, "任务队长(Task.leader_id)"),
    ("member-001",   NORMAL_ROLE,   200, "任务正式队员(active+未删除)"),
    ("inactive-001", NORMAL_ROLE,   403, "非active队员(status!=active)"),
    ("deleted-001",  NORMAL_ROLE,   403, "已删除队员(is_deleted=1)"),
    ("stranger-001", NORMAL_ROLE,   403, "无关用户"),
    ("creator-001",  NOPERM_ROLE,   403, "创建者但无demand:view(系统层拦截)"),
])
async def test_get_replies_permission(client, scenario, user_id, role, expected, note):
    _override(user_id, role)
    try:
        resp = await client.get(replies_url(scenario["demand_id"]))
    finally:
        _clear_override()
    assert resp.status_code == expected, (
        f"{note} GET replies 期望 {expected}，实际 {resp.status_code}：{resp.text}")


# ---------------- 6. POST reply 权限矩阵（与 GET 一致） ----------------
@pytest.mark.asyncio
@pytest.mark.parametrize("user_id,role,expected,note", [
    ("creator-001",  NORMAL_ROLE,   200, "需求创建者"),
    ("owner-pm-001", NORMAL_ROLE,   200, "被分配PM"),
    ("operator-001", "operator",    200, "运营"),
    ("member-001",   NORMAL_ROLE,   200, "任务正式队员"),
    ("leader-001",   NORMAL_ROLE,   200, "任务队长"),
    ("inactive-001", NORMAL_ROLE,   403, "非active队员"),
    ("stranger-001", NORMAL_ROLE,   403, "无关用户"),
])
async def test_post_reply_permission(client, scenario, user_id, role, expected, note):
    _override(user_id, role)
    try:
        resp = await client.post(
            replies_url(scenario["demand_id"]),
            json={"thread_id": THREAD_ID, "content": "权限测试消息", "attachment_ids": None},
        )
    finally:
        _clear_override()
    assert resp.status_code == expected, (
        f"{note} POST reply 期望 {expected}，实际 {resp.status_code}：{resp.text}")


# ---------------- 7. sender_role 身份标记 ----------------
@pytest.mark.asyncio
async def test_post_reply_sender_role(client, scenario):
    """创建者发 → sender_role='requester'；非创建者 → 沿用自身角色"""
    _override("creator-001", NORMAL_ROLE)
    try:
        r1 = await client.post(replies_url(scenario["demand_id"]),
                               json={"thread_id": THREAD_ID, "content": "创建者回复"})
    finally:
        _clear_override()
    assert r1.status_code == 200
    assert r1.json()["data"]["sender_role"] == "requester", \
        f"创建者 sender_role 应为 requester，实际 {r1.json()['data']['sender_role']}"

    _override("member-001", NORMAL_ROLE)
    try:
        r2 = await client.post(replies_url(scenario["demand_id"]),
                               json={"thread_id": THREAD_ID, "content": "队员回复"})
    finally:
        _clear_override()
    assert r2.status_code == 200
    assert r2.json()["data"]["sender_role"] == NORMAL_ROLE, \
        "非创建者 sender_role 应沿用自身角色"


# ---------------- 8. 资源不存在优先于无权限 ----------------
@pytest.mark.asyncio
async def test_replies_404_before_403(client):
    """需求不存在 → 404 优先于 403"""
    _override("stranger-001", NORMAL_ROLE)
    try:
        resp = await client.get(replies_url("definitely-not-exist-999"))
    finally:
        _clear_override()
    assert resp.status_code == 404, f"期望 404，实际 {resp.status_code}：{resp.text}"


# ---------------- 9. 沟通区之外：需求详情仍可看（锁住需求边界） ----------------
@pytest.mark.asyncio
async def test_detail_open_to_users_with_view_perm(client, scenario):
    """有 demand:view 的无关用户也能看需求详情（沟通区外的部分不被误伤）"""
    _override("stranger-001", NORMAL_ROLE)
    try:
        resp = await client.get(detail_url(scenario["demand_id"]))
    finally:
        _clear_override()
    assert resp.status_code == 200, f"有 demand:view 应能看详情，实际 {resp.status_code}"


@pytest.mark.asyncio
async def test_detail_requires_view_perm(client, scenario):
    """无 demand:view → 详情也 403（系统层拦截）"""
    _override("stranger-001", NOPERM_ROLE)
    try:
        resp = await client.get(detail_url(scenario["demand_id"]))
    finally:
        _clear_override()
    assert resp.status_code == 403
