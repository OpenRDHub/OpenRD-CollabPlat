import os
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.file import File

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")

ALLOWED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".md", ".txt", ".csv", ".json",
    ".zip", ".rar", ".7z",
}

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB


def get_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()


async def save_file(
    db: AsyncSession,
    *,
    file_content: bytes,
    filename: str,
    content_type: str | None,
    biz_type: str | None,
    uploader_id: str,
) -> File:
    ext = get_file_extension(filename)
    file_id = uuid.uuid4().hex
    stored_name = f"{file_id}{ext}"

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, stored_name)
    with open(file_path, "wb") as f:
        f.write(file_content)

    file_record = File(
        id=file_id,
        filename=stored_name,
        original_name=filename,
        content_type=content_type,
        size=len(file_content),
        storage_path=stored_name,
        biz_type=biz_type,
        uploader_id=uploader_id,
    )
    db.add(file_record)
    await db.commit()
    await db.refresh(file_record)
    return file_record


async def get_file_by_id(db: AsyncSession, file_id: str) -> File | None:
    stmt = select(File).where(File.id == file_id, File.is_deleted == 0)
    return (await db.execute(stmt)).scalar_one_or_none()


async def delete_file(db: AsyncSession, file_record: File, deleted_by: str) -> None:
    from datetime import datetime, timezone
    file_record.is_deleted = 1
    file_record.deleted_at = datetime.now(timezone.utc)
    file_record.deleted_by = deleted_by
    await db.commit()
