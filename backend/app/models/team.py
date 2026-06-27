import uuid

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, SoftDeleteMixin, TimestampMixin


class TaskMember(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "task_members"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    task_id: Mapped[str] = mapped_column(String(20), index=True)
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    role: Mapped[str] = mapped_column(String(50))
    duty: Mapped[str | None] = mapped_column(String(200))
    source: Mapped[str] = mapped_column(String(20), default="application")
    status: Mapped[str] = mapped_column(String(20), default="active")


class JoinApplication(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "join_applications"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    task_id: Mapped[str] = mapped_column(String(20), index=True)
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    role: Mapped[str] = mapped_column(String(50))
    skills: Mapped[str | None] = mapped_column(Text)
    reason: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    reviewer_id: Mapped[str | None] = mapped_column(String(36))
    reject_reason: Mapped[str | None] = mapped_column(Text)


class Assignment(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "assignments"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    task_id: Mapped[str] = mapped_column(String(20), index=True)
    title: Mapped[str] = mapped_column(String(200))
    owner_id: Mapped[str | None] = mapped_column(String(36))
    deliverable: Mapped[str | None] = mapped_column(Text)
    due_time: Mapped[str | None] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(20), default="todo")
