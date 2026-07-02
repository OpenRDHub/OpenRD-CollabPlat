from datetime import datetime

from pydantic import BaseModel, Field


class MessageOut(BaseModel):
    id: str
    category: str
    title: str
    content: str | None = None
    target_type: str | None = None
    target_id: str | None = None
    sender_id: str | None = None
    is_read: int = 0
    created_at: datetime | None = None


class UnreadCountOut(BaseModel):
    total: int = 0
    by_category: dict[str, int] = {}
