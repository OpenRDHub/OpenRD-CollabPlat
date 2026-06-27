import uuid

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, SoftDeleteMixin, TimestampMixin


class Demand(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "demands"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    urgency: Mapped[str] = mapped_column(String(10), default="medium")
    status: Mapped[str] = mapped_column(String(20), default="pending_review")
    convert_status: Mapped[str | None] = mapped_column(String(20))
    creator_id: Mapped[str] = mapped_column(String(36), index=True)
    contact_phone: Mapped[str | None] = mapped_column(String(20))
    attachment_ids: Mapped[str | None] = mapped_column(Text)
    linked_task_id: Mapped[str | None] = mapped_column(String(20))
    linked_demand_id: Mapped[str | None] = mapped_column(String(20))
    progress: Mapped[int] = mapped_column(Integer, default=0)
    feedback: Mapped[str | None] = mapped_column(Text)
    owner_id: Mapped[str | None] = mapped_column(String(36))


class DemandReply(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "demand_replies"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    demand_id: Mapped[str] = mapped_column(String(20), index=True)
    thread_id: Mapped[str] = mapped_column(String(36), index=True)
    sender_id: Mapped[str] = mapped_column(String(36))
    sender_role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text)
    attachment_ids: Mapped[str | None] = mapped_column(Text)
    is_revoked: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
