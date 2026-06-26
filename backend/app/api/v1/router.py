from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/api/v1")
router.include_router(auth_router)


@router.get("/health", response_model=ApiResponse)
async def health():
    return ApiResponse(data={"status": "ok"})
