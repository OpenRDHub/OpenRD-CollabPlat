import uuid

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, SoftDeleteMixin, TimestampMixin


class Task(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    demand_id: Mapped[str | None] = mapped_column(String(20), index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    task_type: Mapped[str | None] = mapped_column(String(50))
    priority: Mapped[str] = mapped_column(String(10), default="medium")
    scope: Mapped[str | None] = mapped_column(Text)
    acceptance_criteria: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="recruiting", index=True)
    team_status: Mapped[str] = mapped_column(String(20), default="forming")
    progress: Mapped[int] = mapped_column(Integer, default=0)
    planned_end_time: Mapped[str | None] = mapped_column(String(30))
    owner_id: Mapped[str | None] = mapped_column(String(36))
    leader_id: Mapped[str | None] = mapped_column(String(36))
    resource_links: Mapped[str | None] = mapped_column(Text)
    file_ids: Mapped[str | None] = mapped_column(Text)


class TaskProgress(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "task_progress"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    task_id: Mapped[str] = mapped_column(String(20), index=True)
    user_id: Mapped[str] = mapped_column(String(36))
    progress: Mapped[int] = mapped_column(Integer, default=0)
    content: Mapped[str | None] = mapped_column(Text)
    file_ids: Mapped[str | None] = mapped_column(Text)
