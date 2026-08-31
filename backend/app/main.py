import asyncio
import logging
from contextlib import asynccontextmanager, suppress
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import router as v1_router
from app.config import get_settings
from app.database import async_session_factory
from app.services.file import cleanup_expired_files
from app.utils.redis import close_redis, init_redis

logger = logging.getLogger(__name__)


async def file_cleanup_loop() -> None:
    interval = max(get_settings().file_cleanup_interval_minutes, 1) * 60
    while True:
        try:
            async with async_session_factory() as db:
                result = await cleanup_expired_files(db)
                if any(result.values()):
                    logger.info("file cleanup completed: %s", result)
        except Exception:
            logger.exception("file cleanup failed")
        await asyncio.sleep(interval)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis()
    cleanup_task = asyncio.create_task(file_cleanup_loop())
    try:
        yield
    finally:
        cleanup_task.cancel()
        with suppress(asyncio.CancelledError):
            await cleanup_task
        await close_redis()


settings = get_settings()

app = FastAPI(
    title="OpenRD API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router)

testdemo_dir = Path(__file__).resolve().parent.parent / "testdemo"
if testdemo_dir.exists():
    app.mount("/testdemo", StaticFiles(directory=str(testdemo_dir), html=True), name="testdemo")
