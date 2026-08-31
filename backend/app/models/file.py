import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, SoftDeleteMixin, TimestampMixin


class File(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "files"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    filename: Mapped[str] = mapped_column(String(255))
    original_name: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str | None] = mapped_column(String(100))
    size: Mapped[int] = mapped_column(Integer, default=0)
    storage_path: Mapped[str] = mapped_column(String(500))
    biz_type: Mapped[str | None] = mapped_column(String(30), index=True)
    biz_id: Mapped[str | None] = mapped_column(String(36), index=True)
    uploader_id: Mapped[str] = mapped_column(String(36), index=True)
    sha256: Mapped[str | None] = mapped_column(String(64), index=True)
    detected_content_type: Mapped[str | None] = mapped_column(String(100))
    lifecycle_status: Mapped[str] = mapped_column(
        String(20), default="temporary", server_default="temporary", index=True
    )
    scan_status: Mapped[str] = mapped_column(
        String(20), default="not_configured", server_default="not_configured"
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
