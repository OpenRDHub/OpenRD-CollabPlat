from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import router as v1_router
from app.config import get_settings
from app.utils.redis import close_redis, init_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis()
    yield
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
