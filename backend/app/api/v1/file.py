import os

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user, require_permissions
from app.dependencies.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.file import FileOut
from app.services.file import (
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE,
    UPLOAD_DIR,
    delete_file,
    get_file_by_id,
    get_file_extension,
    save_file,
)

router = APIRouter(tags=["文件存储"])


@router.post("/files", response_model=ApiResponse[FileOut])
async def upload_file(
    file: UploadFile = File(...),
    biz_type: str | None = Query(default=None),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件名不能为空")

    ext = get_file_extension(file.filename)
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"不支持的文件类型: {ext}")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件大小超过 20MB 限制")

    file_record = await save_file(
        db,
        file_content=content,
        filename=file.filename,
        content_type=file.content_type,
        biz_type=biz_type,
        uploader_id=current_user["user_id"],
    )
    return ApiResponse(data=FileOut(
        file_id=file_record.id,
        filename=file_record.original_name,
        size=file_record.size,
        url=f"/api/v1/files/{file_record.id}",
    ))


@router.get("/files/{file_id}")
async def download_file(
    file_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    file_record = await get_file_by_id(db, file_id)
    if not file_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")

    file_path = os.path.join(UPLOAD_DIR, file_record.storage_path)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件已丢失")

    return FileResponse(
        path=file_path,
        filename=file_record.original_name,
        media_type=file_record.content_type or "application/octet-stream",
    )


@router.delete("/files/{file_id}", response_model=ApiResponse)
async def remove_file(
    file_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    file_record = await get_file_by_id(db, file_id)
    if not file_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")

    is_owner = file_record.uploader_id == current_user["user_id"]
    is_admin = current_user["role"] in ("operator", "super_admin")
    if not is_owner and not is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无删除权限")

    await delete_file(db, file_record, deleted_by=current_user["user_id"])
    return ApiResponse(message="文件已删除")
