from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user, require_permissions
from app.dependencies.database import get_db
from app.schemas.common import ApiResponse, PaginatedData
from app.schemas.message import MessageOut, UnreadCountOut
from app.services.message import (
    delete_message,
    get_message_detail,
    get_unread_count,
    list_messages,
    mark_all_read,
    mark_read,
)

router = APIRouter(tags=["消息中心"])


@router.get("/messages", response_model=ApiResponse[PaginatedData[MessageOut]])
async def get_messages(
    category: str | None = Query(default=None),
    unread_only: int = Query(default=0),
    keyword: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: dict = Depends(require_permissions("message:view")),
    db: AsyncSession = Depends(get_db),
):
    items, total = await list_messages(
        db,
        user_id=current_user["user_id"],
        category=category,
        unread_only=bool(unread_only),
        keyword=keyword,
        page=page,
        page_size=page_size,
    )
    return ApiResponse(
        data=PaginatedData(
            items=[MessageOut(**item) for item in items],
            page=page,
            page_size=page_size,
            total=total,
        )
    )


@router.get("/messages/unread-count", response_model=ApiResponse[UnreadCountOut])
async def get_messages_unread_count(
    current_user: dict = Depends(require_permissions("message:view")),
    db: AsyncSession = Depends(get_db),
):
    result = await get_unread_count(db, current_user["user_id"])
    return ApiResponse(data=UnreadCountOut(**result))


@router.get("/messages/{message_id}", response_model=ApiResponse[MessageOut])
async def get_message(
    message_id: str,
    current_user: dict = Depends(require_permissions("message:view")),
    db: AsyncSession = Depends(get_db),
):
    detail = await get_message_detail(db, message_id, current_user["user_id"])
    if not detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="消息不存在")
    return ApiResponse(data=MessageOut(**detail))


@router.post("/messages/{message_id}/read", response_model=ApiResponse)
async def post_mark_read(
    message_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    success = await mark_read(db, message_id, current_user["user_id"])
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="消息不存在")
    return ApiResponse(message="已标记为已读")


@router.post("/messages/read-all", response_model=ApiResponse)
async def post_mark_all_read(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    count = await mark_all_read(db, current_user["user_id"])
    return ApiResponse(data={"marked_count": count})


@router.delete("/messages/{message_id}", response_model=ApiResponse)
async def delete_msg(
    message_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    success = await delete_message(db, message_id, current_user["user_id"])
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="消息不存在")
    return ApiResponse(message="消息已删除")
