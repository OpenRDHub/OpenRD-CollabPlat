from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.file import FileOut
from app.services.file import (
    ALLOWED_EXTENSIONS,
    can_access_business_object,
    delete_file,
    ensure_file_access,
    get_file_by_id,
    get_file_extension,
    normalize_biz_type,
    read_upload_limited,
    resolve_storage_path,
    sanitize_filename,
    save_file,
)

router = APIRouter(tags=["文件存储"])


def _check_storage_enabled():
    if not get_settings().storage_enabled:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="文件存储服务暂未开放")


@router.post("/files", response_model=ApiResponse[FileOut])
async def upload_file(
    file: UploadFile = File(...),
    biz_type: str | None = Query(default=None),
    biz_id: str | None = Query(default=None),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _check_storage_enabled()
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件名不能为空")

    safe_name = sanitize_filename(file.filename)
    ext = get_file_extension(safe_name)
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"不支持的文件类型: {ext}")

    content = await read_upload_limited(file)

    normalized_type = normalize_biz_type(biz_type)
    if biz_id is not None:
        if normalized_type is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="biz_id 必须与 biz_type 同时提供",
            )
        if not await can_access_business_object(
            db,
            biz_type=normalized_type,
            biz_id=biz_id,
            user_id=current_user["user_id"],
            role=current_user["role"],
        ):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权绑定到该业务对象")

    file_record = await save_file(
        db,
        file_content=content,
        filename=safe_name,
        content_type=file.content_type,
        biz_type=normalized_type,
        biz_id=biz_id,
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
    _check_storage_enabled()
    file_record = await get_file_by_id(db, file_id)
    if not file_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")

    await ensure_file_access(
        db,
        file_record,
        user_id=current_user["user_id"],
        role=current_user["role"],
    )

    file_path = resolve_storage_path(file_record.storage_path)
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件已丢失")

    return FileResponse(
        path=str(file_path),
        filename=file_record.original_name,
        media_type=file_record.content_type or "application/octet-stream",
    )


@router.delete("/files/{file_id}", response_model=ApiResponse)
async def remove_file(
    file_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _check_storage_enabled()
    file_record = await get_file_by_id(db, file_id)
    if not file_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")

    await ensure_file_access(
        db,
        file_record,
        user_id=current_user["user_id"],
        role=current_user["role"],
    )

    is_owner = file_record.uploader_id == current_user["user_id"]
    is_admin = current_user["role"] in ("operator", "super_admin")
    if not is_owner and not is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无删除权限")
    if file_record.biz_id is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="文件仍被业务记录引用，请先解除附件关联",
        )

    await delete_file(db, file_record, deleted_by=current_user["user_id"])
    return ApiResponse(message="文件已删除")
