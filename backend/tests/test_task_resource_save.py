"""
任务资源链接（resource_links）/ 负责人（leader_id）持久化测试

覆盖 PR（2026-09-23 修复）：
  TaskDetailView.vue 的编辑弹窗通过 PATCH /api/v1/tasks/{id} 发送 `resource_links` 与
  `leader_id`，此前后端 `TaskUpdateRequest` 与 `update_task` 均未处理这两个字段，
  导致保存时被静默丢弃，刷新后“项目资源”列表消失。

本测试验证修复后：
  - PATCH 携带 `resource_links` → 落库（JSON 字符串）并随详情返回（list[dict]，顺序/字段保留）
  - PATCH 携带 `leader_id` → 落库并随详情返回
  - 发送空 `resource_links: []` → 清空并持久化
  - 请求体不含 `resource_links` → 已有资源不被覆盖（仅更新传入字段）
  - 无 `task:manage` 权限（如 builder）→ 403
  - 已关闭/已完成任务 → 400（状态守卫仍生效）

运行：
    .venv/Scripts/python -m pytest tests/test_task_resource_save.py -v -s
"""

import json

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.main import app
from app.models.task import Task
from app.services.task import create_task

API = "/api/v1"
TASKS_PATH = f"{API}/tasks/{{task_id}}"


def task_url(task_id: str) -> str:
    return TASKS_PATH.replace("{task_id}", task_id)


def _uid(p: str = "id") -> str:
    import uuid
    return f"{p}-{uuid.uuid4().hex[:8]}"


def _override(user_id: str, role: str):
    async def _ov() -> dict:
        return {"user_id": user_id, "role": role, "jti": f"jti-{user_id}"}
    app.dependency_overrides[get_current_user] = _ov


def _clear_override():
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
async def task_scene(db_session: AsyncSession) -> dict:
    """一个 recruiting 任务，owner/leader 初始为占位账号；返回 task_id 与原始 leader_id"""
    task = await create_task(
        db_session,
        title="资源持久化测试任务",
        description="用于验证 resource_links / leader_id 落库",
        task_type="工具开发项目",
        priority="medium",
        owner_id="owner-001",
        leader_id="leader-origin",
    )
    await db_session.refresh(task)
    return {"task_id": task.id, "origin_leader": task.leader_id}


@pytest.mark.asyncio
async def test_patch_persists_resource_links(client: AsyncClient, task_scene: dict, db_session: AsyncSession):
    """PATCH 携带 resource_links → 详情返回列表，且库里以 JSON 字符串落库"""
    links = [
        {"label": "官网", "url": "https://example.com"},
        {"label": "文档", "url": "www.example.com/docs"},   # 缺协议，后端原样存储
    ]
    _override("operator-001", "operator")
    try:
        resp = await client.patch(
            task_url(task_scene["task_id"]),
            json={"resource_links": links},
        )
    finally:
        _clear_override()
    assert resp.status_code == 200, resp.text
    assert resp.json()["data"]["resource_links"] == links

    # 直接读库，确认确实持久化（而非仅回显）
    raw = (await db_session.execute(
        select(Task.resource_links).where(Task.id == task_scene["task_id"])
    )).scalar_one()
    assert raw is not None
    stored = json.loads(raw)
    assert stored == links


@pytest.mark.asyncio
async def test_patch_persists_leader_id(client: AsyncClient, task_scene: dict, db_session: AsyncSession):
    """PATCH 携带 leader_id → 详情与库里均更新为新的负责人"""
    new_leader = "leader-new-001"
    _override("operator-001", "operator")
    try:
        resp = await client.patch(
            task_url(task_scene["task_id"]),
            json={"leader_id": new_leader},
        )
    finally:
        _clear_override()
    assert resp.status_code == 200, resp.text
    assert resp.json()["data"]["leader_id"] == new_leader

    stored = (await db_session.execute(
        select(Task.leader_id).where(Task.id == task_scene["task_id"])
    )).scalar_one()
    assert stored == new_leader


@pytest.mark.asyncio
async def test_patch_resource_links_roundtrip_order_and_fields(client: AsyncClient, task_scene: dict):
    """多个资源链接：顺序、字段（label/url）均原样保留返回"""
    links = [
        {"label": "A", "url": "https://a.com"},
        {"label": "B", "url": "https://b.com"},
        {"label": "C", "url": "https://c.com"},
    ]
    _override("operator-001", "operator")
    try:
        await client.patch(task_url(task_scene["task_id"]), json={"resource_links": links})
        detail = await client.get(task_url(task_scene["task_id"]))
    finally:
        _clear_override()
    assert detail.status_code == 200, detail.text
    got = detail.json()["data"]["resource_links"]
    assert got == links
    assert [g["label"] for g in got] == ["A", "B", "C"]


@pytest.mark.asyncio
async def test_patch_can_clear_resource_links(client: AsyncClient, task_scene: dict, db_session: AsyncSession):
    """发送 resource_links: [] 应清空并持久化（回归：修复前该字段被忽略，无法清空）"""
    _override("operator-001", "operator")
    try:
        seeded = await client.patch(
            task_url(task_scene["task_id"]),
            json={"resource_links": [{"label": "临时", "url": "https://x.com"}]},
        )
        assert seeded.status_code == 200
        cleared = await client.patch(
            task_url(task_scene["task_id"]),
            json={"resource_links": []},
        )
    finally:
        _clear_override()
    assert cleared.status_code == 200, cleared.text
    assert cleared.json()["data"]["resource_links"] == []

    raw = (await db_session.execute(
        select(Task.resource_links).where(Task.id == task_scene["task_id"])
    )).scalar_one()
    assert json.loads(raw) == []


@pytest.mark.asyncio
async def test_patch_omitting_resource_links_keeps_existing(client: AsyncClient, task_scene: dict):
    """请求体不含 resource_links 时，已有资源不应被覆盖（仅更新传入字段）"""
    links = [{"label": "保留", "url": "https://keep.com"}]
    _override("operator-001", "operator")
    try:
        seeded = await client.patch(
            task_url(task_scene["task_id"]),
            json={"resource_links": links},
        )
        assert seeded.status_code == 200
        # 仅更新标题，不传 resource_links
        title_only = await client.patch(
            task_url(task_scene["task_id"]),
            json={"title": "只改标题"},
        )
    finally:
        _clear_override()
    assert title_only.status_code == 200, title_only.text
    assert title_only.json()["data"]["title"] == "只改标题"
    assert title_only.json()["data"]["resource_links"] == links


@pytest.mark.asyncio
async def test_patch_resource_links_requires_manage_permission(client: AsyncClient, task_scene: dict):
    """无 task:manage 权限（builder 仅 task:update）→ 403"""
    _override("builder-001", "builder")
    try:
        resp = await client.patch(
            task_url(task_scene["task_id"]),
            json={"resource_links": [{"label": "x", "url": "https://x.com"}]},
        )
    finally:
        _clear_override()
    assert resp.status_code == 403, resp.text


@pytest.mark.asyncio
async def test_patch_resource_links_rejected_when_task_closed(client: AsyncClient, task_scene: dict, db_session: AsyncSession):
    """已关闭任务不可编辑：状态守卫仍生效（400），资源不会被写入"""
    task = (await db_session.execute(
        select(Task).where(Task.id == task_scene["task_id"])
    )).scalars().one()
    task.status = "closed"
    await db_session.commit()

    _override("operator-001", "operator")
    try:
        resp = await client.patch(
            task_url(task_scene["task_id"]),
            json={"resource_links": [{"label": "x", "url": "https://x.com"}]},
        )
    finally:
        _clear_override()
    assert resp.status_code == 400, resp.text

    raw = (await db_session.execute(
        select(Task.resource_links).where(Task.id == task_scene["task_id"])
    )).scalar_one()
    assert raw is None or json.loads(raw) == []
