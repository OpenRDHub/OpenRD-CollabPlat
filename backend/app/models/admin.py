import uuid

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class SystemLog(Base, TimestampMixin):
    __tablename__ = "system_logs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    actor_id: Mapped[str] = mapped_column(String(36), index=True)
    actor_role: Mapped[str | None] = mapped_column(String(20))
    actor_nickname: Mapped[str | None] = mapped_column(String(50))
    action: Mapped[str] = mapped_column(String(100), index=True)
    module: Mapped[str] = mapped_column(String(30), index=True)
    target_type: Mapped[str | None] = mapped_column(String(30))
    target_id: Mapped[str | None] = mapped_column(String(36))
    target_name: Mapped[str | None] = mapped_column(String(200))
    risk_level: Mapped[str] = mapped_column(String(10), default="low")
    detail: Mapped[str | None] = mapped_column(Text)
    ip: Mapped[str | None] = mapped_column(String(45))
    user_agent: Mapped[str | None] = mapped_column(String(500))
    result: Mapped[str] = mapped_column(String(20), default="success")


class UserPermission(Base, TimestampMixin):
    """用户手动追加权限（角色模板之外）。最终权限 = 角色模板权限 ∪ 手动权限。"""

    __tablename__ = "user_permissions"
    __table_args__ = (
        UniqueConstraint("user_id", "permission_id", name="uq_user_permissions_user_id_permission_id"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    permission_id: Mapped[str] = mapped_column(String(50))
    granted_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"))
    reason: Mapped[str | None] = mapped_column(String(500))
