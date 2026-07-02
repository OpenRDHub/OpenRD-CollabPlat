from fastapi import APIRouter

from app.api.v1.admin import router as admin_router
from app.api.v1.auth import router as auth_router
from app.api.v1.demand import router as demand_router
from app.api.v1.file import router as file_router
from app.api.v1.message import router as message_router
from app.api.v1.task import router as task_router
from app.api.v1.team import router as team_router
from app.api.v1.user import router as user_router
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/api/v1")
router.include_router(auth_router)
router.include_router(user_router)
router.include_router(demand_router)
router.include_router(task_router)
router.include_router(team_router)
router.include_router(message_router)
router.include_router(admin_router)
router.include_router(file_router)


@router.get("/health", response_model=ApiResponse)
async def health():
    return ApiResponse(data={"status": "ok"})
