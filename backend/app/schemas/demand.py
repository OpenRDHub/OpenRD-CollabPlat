from datetime import datetime

from pydantic import BaseModel, Field


class CreateDemandRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    urgency: str = Field(pattern=r"^(low|medium|high)$")
    contact_phone: str | None = Field(default=None, pattern=r"^1[3-9]\d{9}$")
    attachment_ids: list[str] | None = Field(default=None, max_length=3)


class DemandUpdateRequest(BaseModel):
    progress: int | None = Field(default=None, ge=0, le=100)
    feedback: str | None = None
    owner_id: str | None = None


class ReplyRequest(BaseModel):
    thread_id: str = Field(min_length=1, max_length=36)
    content: str = Field(min_length=1)
    attachment_ids: list[str] | None = Field(default=None, max_length=5)


class ConvertRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    task_type: str = Field(min_length=1, max_length=50)
    priority: str = Field(pattern=r"^(low|medium|high)$")
    scope: str | None = None
    acceptance_criteria: str | None = None
    planned_end_time: str | None = None


class RejectRequest(BaseModel):
    reason: str = Field(min_length=1)


class LinkSimilarRequest(BaseModel):
    target_demand_id: str | None = None
    target_task_id: str | None = None
    reason: str = Field(min_length=1)


class DemandOut(BaseModel):
    id: str
    title: str
    urgency: str
    status: str
    convert_status: str | None = None
    creator_id: str
    progress: int = 0
    feedback: str | None = None
    linked_task_id: str | None = None
    linked_demand_id: str | None = None
    owner_id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class DemandDetail(BaseModel):
    id: str
    title: str
    description: str
    urgency: str
    status: str
    convert_status: str | None = None
    creator_id: str
    contact_phone: str | None = None
    attachment_ids: list[str] | None = None
    linked_task_id: str | None = None
    linked_demand_id: str | None = None
    progress: int = 0
    feedback: str | None = None
    owner_id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class DemandReplyOut(BaseModel):
    id: str
    demand_id: str
    thread_id: str
    sender_id: str
    sender_role: str
    content: str
    attachment_ids: list[str] | None = None
    is_revoked: int = 0
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
