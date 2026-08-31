import pytest
import sqlalchemy
from fakeredis import aioredis as fakeredis_aio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.config import get_settings
from app.dependencies.database import get_db
from app.dependencies.redis import get_redis
from app.main import app

settings = get_settings()
database_name = make_url(settings.database_url).database or ""
if not database_name.endswith("_test"):
    raise RuntimeError(
        "Tests require a dedicated database whose name ends with '_test'; "
        f"got {database_name!r}"
    )

test_engine = create_async_engine(settings.database_url, poolclass=NullPool)
test_session_factory = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

TRUNCATE_TEST_DATA = sqlalchemy.text(
    """
    TRUNCATE TABLE
        message_recipients, messages, system_logs, assignments,
        join_applications, task_members, task_progress, tasks,
        demand_replies, demands, files, users
    RESTART IDENTITY CASCADE
    """
)


async def _clean_test_data() -> None:
    async with test_engine.begin() as conn:
        await conn.execute(TRUNCATE_TEST_DATA)
        await conn.execute(sqlalchemy.text("ALTER SEQUENCE platform_id_seq RESTART WITH 1"))
        await conn.execute(sqlalchemy.text("ALTER SEQUENCE demand_id_seq RESTART WITH 1"))
        await conn.execute(sqlalchemy.text("ALTER SEQUENCE task_id_seq RESTART WITH 1"))


@pytest.fixture
async def fake_redis():
    r = fakeredis_aio.FakeRedis(decode_responses=True)
    yield r
    await r.flushall()
    await r.aclose()


@pytest.fixture(autouse=True)
async def clean_db():
    await _clean_test_data()
    yield
    await _clean_test_data()


@pytest.fixture
async def db_session():
    async with test_session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(fake_redis):
    async def override_db():
        async with test_session_factory() as session:
            try:
                yield session
            finally:
                await session.rollback()

    app.dependency_overrides[get_redis] = lambda: fake_redis
    app.dependency_overrides[get_db] = override_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()
