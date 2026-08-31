import asyncio
import hashlib
import io
import json
import os
import re
import struct
import uuid
import zipfile
from datetime import UTC, datetime, timedelta
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.demand import Demand, DemandReply
from app.models.file import File
from app.models.task import Task, TaskProgress
from app.models.team import TaskMember

BACKEND_ROOT = Path(__file__).resolve().parents[2]

ALLOWED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".md", ".txt", ".csv", ".json",
    ".zip", ".rar", ".7z",
}

BIZ_TYPE_ALIASES = {
    "demand": "demand",
    "demand_attachment": "demand",
    "demand_reply": "demand_reply",
    "reply_attachment": "demand_reply",
    "task": "task",
    "task_file": "task",
    "task_progress": "task_progress",
    "progress_attachment": "task_progress",
    "avatar": "avatar",
}

TEXT_EXTENSIONS = {".md", ".txt", ".csv"}
OLE_EXTENSIONS = {".doc", ".xls", ".ppt"}
OFFICE_ZIP_MARKERS = {
    ".docx": "word/",
    ".xlsx": "xl/",
    ".pptx": "ppt/",
}
CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f]")


def normalize_biz_type(biz_type: str | None) -> str | None:
    if biz_type is None:
        return None
    normalized = BIZ_TYPE_ALIASES.get(biz_type)
    if normalized is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的附件业务类型",
        )
    return normalized


def get_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()


def get_storage_root() -> Path:
    configured = Path(get_settings().upload_dir)
    root = configured if configured.is_absolute() else BACKEND_ROOT / configured
    return root.resolve()


def get_max_file_size() -> int:
    return get_settings().max_file_size_mb * 1024 * 1024


def sanitize_filename(filename: str) -> str:
    safe_name = Path(filename.replace("\\", "/")).name.strip()
    safe_name = CONTROL_CHARS.sub("", safe_name)
    if not safe_name or safe_name in {".", ".."}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件名无效")
    if len(safe_name) > 255:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件名过长")
    return safe_name


async def read_upload_limited(upload: UploadFile) -> bytes:
    max_size = get_max_file_size()
    chunks: list[bytes] = []
    total = 0
    while chunk := await upload.read(1024 * 1024):
        total += len(chunk)
        if total > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文件大小超过 {get_settings().max_file_size_mb}MB 限制",
            )
        chunks.append(chunk)
    if total == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不允许上传空文件")
    return b"".join(chunks)


def _validate_zip(content: bytes, extension: str) -> str:
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            names = archive.namelist()
            if len(names) > 10_000:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="压缩包文件数量超过安全限制",
                )
            expanded_size = sum(info.file_size for info in archive.infolist())
            if expanded_size > max(len(content) * 200, 200 * 1024 * 1024):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="压缩包解压倍率超过安全限制",
                )
            marker = OFFICE_ZIP_MARKERS.get(extension)
            if marker and (
                "[Content_Types].xml" not in names
                or not any(name.startswith(marker) for name in names)
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="文件内容与扩展名不匹配",
                )
    except zipfile.BadZipFile as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="压缩文件结构无效",
        ) from exc
    return {
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ".zip": "application/zip",
    }[extension]


def detect_content_type(content: bytes, extension: str) -> str:
    if extension == ".pdf" and content.startswith(b"%PDF-"):
        return "application/pdf"
    if extension in {".jpg", ".jpeg"} and content.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if extension == ".png" and content.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if extension == ".gif" and content[:6] in {b"GIF87a", b"GIF89a"}:
        return "image/gif"
    if extension == ".webp" and content.startswith(b"RIFF") and content[8:12] == b"WEBP":
        return "image/webp"
    if extension in {*OFFICE_ZIP_MARKERS, ".zip"} and content.startswith(b"PK"):
        return _validate_zip(content, extension)
    if extension in OLE_EXTENSIONS and content.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"):
        return "application/x-ole-storage"
    if extension == ".rar" and content.startswith((b"Rar!\x1a\x07\x00", b"Rar!\x1a\x07\x01\x00")):
        return "application/vnd.rar"
    if extension == ".7z" and content.startswith(b"7z\xbc\xaf\x27\x1c"):
        return "application/x-7z-compressed"
    if extension in TEXT_EXTENSIONS or extension == ".json":
        if b"\x00" in content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文本文件包含二进制内容",
            )
        try:
            decoded = content.decode("utf-8-sig")
            if extension == ".json":
                json.loads(decoded)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文本或 JSON 文件内容无效",
            ) from exc
        return "application/json" if extension == ".json" else "text/plain"
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="文件内容与扩展名不匹配",
    )


async def scan_file_content(content: bytes) -> str:
    settings = get_settings()
    if not settings.file_scan_enabled:
        return "not_configured"
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(settings.clamav_host, settings.clamav_port),
            timeout=5,
        )
        writer.write(b"zINSTREAM\0")
        for offset in range(0, len(content), 1024 * 1024):
            chunk = content[offset : offset + 1024 * 1024]
            writer.write(struct.pack(">I", len(chunk)) + chunk)
        writer.write(struct.pack(">I", 0))
        await writer.drain()
        response = (await asyncio.wait_for(reader.read(4096), timeout=30)).decode(
            "utf-8", errors="replace"
        )
        writer.close()
        await writer.wait_closed()
        if "FOUND" in response:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件未通过恶意软件扫描",
            )
        if response.rstrip("\0\r\n").endswith("OK"):
            return "clean"
        raise RuntimeError(f"unexpected ClamAV response: {response!r}")
    except HTTPException:
        raise
    except (OSError, TimeoutError, RuntimeError) as exc:
        if settings.file_scan_required:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="文件扫描服务不可用",
            ) from exc
        return "unavailable"


def resolve_storage_path(storage_path: str) -> Path:
    root = get_storage_root()
    candidate = (root / storage_path).resolve()
    if candidate.parent != root:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="文件存储路径无效",
        )
    return candidate


def _write_file_atomic(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    try:
        with temporary.open("xb") as stream:
            stream.write(content)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


async def save_file(
    db: AsyncSession,
    *,
    file_content: bytes,
    filename: str,
    content_type: str | None,
    biz_type: str | None,
    biz_id: str | None,
    uploader_id: str,
) -> File:
    safe_name = sanitize_filename(filename)
    ext = get_file_extension(safe_name)
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型: {ext}",
        )
    detected_type = detect_content_type(file_content, ext)
    scan_status = await scan_file_content(file_content)
    file_id = uuid.uuid4().hex
    stored_name = f"{file_id}{ext}"
    file_path = resolve_storage_path(stored_name)
    await asyncio.to_thread(_write_file_atomic, file_path, file_content)

    bound = biz_id is not None
    expires_at = None
    if not bound:
        expires_at = datetime.now(UTC) + timedelta(hours=get_settings().file_temp_ttl_hours)

    file_record = File(
        id=file_id,
        filename=stored_name,
        original_name=safe_name,
        content_type=detected_type,
        size=len(file_content),
        storage_path=stored_name,
        biz_type=normalize_biz_type(biz_type),
        biz_id=biz_id,
        uploader_id=uploader_id,
        sha256=hashlib.sha256(file_content).hexdigest(),
        detected_content_type=detected_type,
        lifecycle_status="bound" if bound else "temporary",
        scan_status=scan_status,
        expires_at=expires_at,
    )
    try:
        db.add(file_record)
        await db.commit()
        await db.refresh(file_record)
    except Exception:
        await db.rollback()
        await asyncio.to_thread(file_path.unlink, missing_ok=True)
        raise
    return file_record


async def get_file_by_id(db: AsyncSession, file_id: str) -> File | None:
    stmt = select(File).where(File.id == file_id, File.is_deleted == 0)
    return (await db.execute(stmt)).scalar_one_or_none()


async def can_access_business_object(
    db: AsyncSession,
    *,
    biz_type: str,
    biz_id: str,
    user_id: str,
    role: str,
) -> bool:
    """Return whether a user may read attachments for a bound business object."""
    if biz_type == "demand":
        demand = (
            await db.execute(
                select(Demand).where(Demand.id == biz_id, Demand.is_deleted == 0)
            )
        ).scalar_one_or_none()
        if not demand:
            return False
        if role == "super_admin":
            return True
        return bool(
            demand.creator_id == user_id
            or demand.owner_id == user_id
            or role == "operator"
        )

    if biz_type == "demand_reply":
        reply = (
            await db.execute(
                select(DemandReply).where(
                    DemandReply.id == biz_id,
                    DemandReply.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        if not reply:
            return False
        if role == "super_admin":
            return True
        return await can_access_business_object(
            db,
            biz_type="demand",
            biz_id=reply.demand_id,
            user_id=user_id,
            role=role,
        )

    if biz_type == "task_progress":
        progress = (
            await db.execute(
                select(TaskProgress).where(
                    TaskProgress.id == biz_id,
                    TaskProgress.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        if not progress:
            return False
        if role == "super_admin":
            return True
        return await can_access_business_object(
            db,
            biz_type="task",
            biz_id=progress.task_id,
            user_id=user_id,
            role=role,
        )

    if biz_type == "task":
        task = (
            await db.execute(
                select(Task).where(Task.id == biz_id, Task.is_deleted == 0)
            )
        ).scalar_one_or_none()
        if not task:
            return False
        if role == "super_admin":
            return True
        if role == "operator" or task.owner_id == user_id or task.leader_id == user_id:
            return True
        member = (
            await db.execute(
                select(TaskMember).where(
                    TaskMember.task_id == biz_id,
                    TaskMember.user_id == user_id,
                    TaskMember.status == "active",
                    TaskMember.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        return member is not None

    return False


async def ensure_file_access(
    db: AsyncSession,
    file_record: File,
    *,
    user_id: str,
    role: str,
) -> None:
    """Enforce download access for bound files and private temporary uploads."""
    if (
        file_record.biz_id is None
        and file_record.expires_at is not None
        and file_record.expires_at <= datetime.now(UTC)
    ):
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="临时文件已过期")
    if file_record.biz_id is None:
        if file_record.uploader_id == user_id or role in ("operator", "super_admin"):
            return
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无文件访问权限")

    if not file_record.biz_type or not await can_access_business_object(
        db,
        biz_type=file_record.biz_type,
        biz_id=file_record.biz_id,
        user_id=user_id,
        role=role,
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无文件访问权限")


async def bind_files(
    db: AsyncSession,
    file_ids: list[str] | None,
    *,
    biz_type: str,
    biz_id: str,
    actor_id: str,
    actor_role: str,
) -> None:
    """Bind temporary uploads to one authoritative business object."""
    if not file_ids:
        return

    unique_ids = list(dict.fromkeys(file_ids))
    files = (
        await db.execute(
            select(File).where(File.id.in_(unique_ids), File.is_deleted == 0)
        )
    ).scalars().all()
    by_id = {record.id: record for record in files}
    missing = [file_id for file_id in unique_ids if file_id not in by_id]
    if missing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="附件不存在")

    normalized_type = normalize_biz_type(biz_type)
    for file_id in unique_ids:
        record = by_id[file_id]
        if (
            record.biz_id is None
            and record.expires_at is not None
            and record.expires_at <= datetime.now(UTC)
        ):
            raise HTTPException(status_code=status.HTTP_410_GONE, detail="附件已过期")
        is_admin = actor_role in ("operator", "super_admin")
        if record.uploader_id != actor_id and not is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="不能绑定他人上传的附件")
        if record.biz_id is not None and (
            record.biz_type != normalized_type or record.biz_id != biz_id
        ):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="附件已绑定其他业务对象")
        record.biz_type = normalized_type
        record.biz_id = biz_id
        record.lifecycle_status = "bound"
        record.expires_at = None


async def delete_file(db: AsyncSession, file_record: File, deleted_by: str) -> None:
    file_record.is_deleted = 1
    file_record.lifecycle_status = "deleted"
    file_record.deleted_at = datetime.now(UTC)
    file_record.deleted_by = deleted_by
    await db.commit()
    file_path = resolve_storage_path(file_record.storage_path)
    await asyncio.to_thread(file_path.unlink, missing_ok=True)


async def cleanup_expired_files(db: AsyncSession) -> dict[str, int]:
    """Expire orphan uploads and retry physical deletion for soft-deleted files."""
    now = datetime.now(UTC)
    stmt = select(File).where(
        or_(
            (
                (File.is_deleted == 0)
                & (File.biz_id.is_(None))
                & (File.expires_at.is_not(None))
                & (File.expires_at <= now)
            ),
            File.is_deleted == 1,
        )
    )
    records = (await db.execute(stmt)).scalars().all()
    expired = 0
    removed_content = 0
    purged_metadata = 0
    purge_before = now - timedelta(days=get_settings().file_deleted_retention_days)
    for record in records:
        if record.is_deleted == 0:
            record.is_deleted = 1
            record.lifecycle_status = "expired"
            record.deleted_at = now
            record.deleted_by = "system:file-cleanup"
            expired += 1
        file_path = resolve_storage_path(record.storage_path)
        existed = file_path.exists()
        await asyncio.to_thread(file_path.unlink, missing_ok=True)
        if existed:
            removed_content += 1
        if (
            record.biz_id is None
            and record.deleted_at is not None
            and record.deleted_at <= purge_before
        ):
            await db.delete(record)
            purged_metadata += 1
    await db.commit()
    return {
        "expired": expired,
        "removed_content": removed_content,
        "purged_metadata": purged_metadata,
    }
