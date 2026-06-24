from fastapi import APIRouter

from app.schemas.common import ApiResponse

router = APIRouter(prefix="/api/v1")


@router.get("/health", response_model=ApiResponse)
async def health():
    return ApiResponse(data={"status": "ok"})
