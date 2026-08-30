r"""
测试：需求转化为任务时，demand.owner_id 是否被正确写入。

运行：
    .venv/Scripts/python -m pytest tests/test_demand_convert.py -v -s
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


# ========== 1. DB session ==========
# expire_on_commit=True：commit 后对象过期，后续查询强制回数据库取真实值。
# 这是第一个测试能验证到"路由改了数据库"的关键。
_settings = get_settings()
_engine = create_async_engine(_settings.database_url, poolclass=NullPool)
_SessionFactory = async_sessionmaker(
    _engine, class_=AsyncSession, expire_on_commit=True
)


@pytest.fixture
async def db_session() -> AsyncSession:
    async with _SessionFactory() as session:
        yield session
        await session.rollback()


# ========== 2. 认证 override（绕过 JWT） ==========
ADMIN_USER = {
    "user_id": "test-admin-001",
    "role": "super_admin",
    "jti": "test-jti-001",
}


@pytest.fixture
async def admin_client(client: AsyncClient) -> AsyncClient:
    async def _override_current_user() -> dict:
        return dict(ADMIN_USER)

    app.dependency_overrides[get_current_user] = _override_current_user
    yield client
    app.dependency_overrides.pop(get_current_user, None)


# ========== 3. 路由（已验证可用） ==========
CONVERT_PATH = "/api/v1/demands/{demand_id}/convert"


def convert_url(demand_id: str) -> str:
    return CONVERT_PATH.replace("{demand_id}", demand_id)


# ========== 4. 工具 ==========
def _uid(prefix: str = "demand") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _make_demand(demand_id: str, status: str, owner_id):
    return Demand(
        id=demand_id,
        title="转化权限测试需求",
        description="用于验证转化时 owner_id 写入",
        urgency="medium",
        status=status,
        creator_id="creator-001",
        owner_id=owner_id,
    )


async def _reload_demand(session: AsyncSession, demand_id: str) -> Demand:
    """强制从数据库重新加载，populate_existing 绕过 identity map 缓存。"""
    result = await session.execute(
        select(Demand)
        .where(Demand.id == demand_id)
        .execution_options(populate_existing=True)
    )
    return result.scalar_one()


# ========== 5. Fixture ==========
@pytest.fixture
async def pending_demand(db_session: AsyncSession) -> Demand:
    demand = _make_demand(_uid(), "pending_review", None)
    db_session.add(demand)
    await db_session.commit()
    await db_session.refresh(demand)   # refresh 后属性可用，避免后续同步访问过期属性
    return demand


# ========== 6. 测试用例 ==========
@pytest.mark.asyncio
async def test_convert_sets_demand_owner_id(
    admin_client: AsyncClient,
    db_session: AsyncSession,
    pending_demand: Demand,
):
    """核心：转化时 demand.owner_id 应被写入为当前操作人。"""
    assert pending_demand.owner_id is None, "前置条件：owner_id 应为空"

    payload = {
        "title": "转化测试任务",
        "task_type": "工具开发项目",
        "priority": "medium",
        "scope": "测试范围",
        "acceptance_criteria": "测试验收标准",
    }

    resp = await admin_client.post(convert_url(pending_demand.id), json=payload)
    assert resp.status_code == 200, f"转化失败 [{resp.status_code}]: {resp.text}"

    updated = await _reload_demand(db_session, pending_demand.id)
    assert updated.owner_id is not None, "Bug 复现：demand.owner_id 未被写入！"
    assert updated.owner_id == ADMIN_USER["user_id"]


@pytest.mark.asyncio
async def test_convert_does_not_overwrite_existing_owner(
    admin_client: AsyncClient,
    db_session: AsyncSession,
):
    """边界：已有 owner_id 时，转化不应覆盖。"""
    # 关键：id 存局部变量，避免 commit 后对象过期、同步访问属性触发 MissingGreenlet
    demand_id = _uid()
    demand = _make_demand(demand_id, "communicating", "existing-pm-001")
    db_session.add(demand)
    await db_session.commit()

    payload = {
        "title": "不覆盖测试任务",
        "task_type": "工具开发项目",
        "priority": "low",
        "scope": "测试范围",
        "acceptance_criteria": "测试验收标准",
    }

    resp = await admin_client.post(convert_url(demand_id), json=payload)
    assert resp.status_code == 200, f"转化失败 [{resp.status_code}]: {resp.text}"

    updated = await _reload_demand(db_session, demand_id)
    assert updated.owner_id == "existing-pm-001", (
        f"owner_id 被错误覆盖为 {updated.owner_id}"
    )