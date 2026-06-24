import pytest
import sqlalchemy
from fakeredis import aioredis as fakeredis_aio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.config import get_settings
from app.dependencies.database import get_db
from app.dependencies.redis import get_redis
from app.main import app

settings = get_settings()
test_engine = create_async_engine(settings.database_url, poolclass=NullPool)
test_session_factory = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture
async def fake_redis():
    r = fakeredis_aio.FakeRedis(decode_responses=True)
    yield r
    await r.flushall()
    await r.aclose()


@pytest.fixture(autouse=True)
async def clean_db():
    yield
    async with test_engine.begin() as conn:
        await conn.execute(sqlalchemy.text("DELETE FROM users"))


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
