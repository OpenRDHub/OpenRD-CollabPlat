"""Verify an old PostgreSQL test database can upgrade without losing demand data.

Requires a dedicated *_test database already at l2f3a4b5c6d7. Inserts fixtures
and upgrades it to head; never downgrades or deletes existing data.
"""
import asyncio
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import MetaData, Table, inspect, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.v1.demand import router
from app.config import get_settings
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.demand import Demand
from app.models.user import User

PREVIOUS_REVISION = "l2f3a4b5c6d7"
USER_ID = "migration-submitter"
DEMAND_ID = "MIGRATION-NAME"


def test_database_url():
    url = get_settings().database_url
    parsed = make_url(url)
    if parsed.get_backend_name() != "postgresql" or not (parsed.database or "").endswith("_test"):
        raise RuntimeError("Migration verification requires a dedicated PostgreSQL *_test database")
    return url


async def prepare_old_data():
    engine = create_async_engine(test_database_url())
    try:
        async with engine.begin() as conn:
            revision = await conn.scalar(text("SELECT version_num FROM alembic_version"))
            if revision != PREVIOUS_REVISION:
                raise RuntimeError(f"Expected old revision {PREVIOUS_REVISION}, got {revision}")
            columns = await conn.run_sync(lambda c: inspect(c).get_columns("demands"))
            assert "submitter_display_name" not in {column["name"] for column in columns}
            # Reflect the actual old table: the new Demand ORM already expects the missing column.
            old_table = await conn.run_sync(
                lambda c: Table("demands", MetaData(), autoload_with=c)
            )
            now = datetime.now(UTC)
            await conn.execute(User.__table__.insert().values(
                id=USER_ID, platform_id="MIG-NAME", username="migration-submitter",
                phone="13900000099", password_hash="unused", nickname="历史账号昵称",
            ))
            await conn.execute(old_table.insert().values(
                id=DEMAND_ID, title="Historical demand", description="Preserve this description",
                creator_id=USER_ID, urgency="medium", status="pending_review", progress=35,
                is_deleted=0, created_at=now, updated_at=now,
            ))
    finally:
        await engine.dispose()


async def verify_upgraded_data():
    engine = create_async_engine(test_database_url())
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with engine.connect() as conn:
            columns = await conn.run_sync(lambda c: inspect(c).get_columns("demands"))
            column = next(c for c in columns if c["name"] == "submitter_display_name")
            assert column["nullable"] and column["type"].length == 15
        async with factory() as db:
            demand = await db.get(Demand, DEMAND_ID)
            assert demand.submitter_display_name is None
            assert (demand.title, demand.description, demand.progress, demand.creator_id) == (
                "Historical demand", "Preserve this description", 35, USER_ID,
            )
            assert (await db.get(User, USER_ID)).nickname == "历史账号昵称"

        api = FastAPI()
        api.include_router(router, prefix="/api/v1")

        async def database():
            async with factory() as db:
                yield db

        api.dependency_overrides[get_db] = database
        api.dependency_overrides[get_current_user] = lambda: {
            "user_id": USER_ID, "role": "super_admin", "jti": "migration-test",
        }
        async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as client:
            listing = await client.get("/api/v1/demands?hall_only=true")
            assert listing.status_code == 200, listing.text
            assert DEMAND_ID in {item["id"] for item in listing.json()["data"]["items"]}
            path = f"/api/v1/demands/{DEMAND_ID}"
            detail = await client.get(path)
            assert detail.status_code == 200, detail.text
            assert detail.json()["data"]["submitter_display_name"] == "历史账号昵称"
            updated = await client.patch(path + "/submitter-name", json={
                "submitter_display_name": "新提交昵称",
            })
            assert updated.status_code == 200, updated.text
        async with factory() as db:
            assert await db.scalar(select(Demand.submitter_display_name).where(
                Demand.id == DEMAND_ID,
            )) == "新提交昵称"
    finally:
        await engine.dispose()


def main():
    asyncio.run(prepare_old_data())
    subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"],
                   cwd=Path(__file__).resolve().parents[1], check=True)
    asyncio.run(verify_upgraded_data())
    print("Old PostgreSQL database upgrade verified: preserved data, nickname fallback, API reads/writes")


if __name__ == "__main__":
    main()
