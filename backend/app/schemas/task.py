from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class TaskUpdateRequest(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    description: str | None = None
    task_type: str | None = Field(default=None, max_length=50)
    priority: str | None = Field(default=None, pattern=r"^(low|medium|high)$")
    scope: str | None = None
    acceptance_criteria: str | None = None
    planned_end_time: str | None = None


class StatusChangeRequest(BaseModel):
    status: str = Field(pattern=r"^(recruiting|team_ready|in_progress|pending_acceptance|completed|closed)$")
    reason: str | None = None


class ProgressRequest(BaseModel):
    progress: int = Field(ge=0, le=100)
    content: str | None = None
    file_ids: list[str] | None = None


class ResourcesRequest(BaseModel):
    resource_links: list[dict] | None = None
    file_ids: list[str] | None = None


class ResourceLink(BaseModel):
    name: str
    url: str


class TaskOut(BaseModel):
    id: str
    title: str
    description: str | None = None
    status: str
    team_status: str
    progress: int = 0
    priority: str = "medium"
    task_type: str | None = None
    demand_id: str | None = None
    planned_end_time: str | None = None
    owner_id: str | None = None
    leader_id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class TaskDetail(BaseModel):
    id: str
    title: str
    description: str | None = None
    task_type: str | None = None
    priority: str = "medium"
    scope: str | None = None
    acceptance_criteria: str | None = None
    status: str
    team_status: str
    progress: int = 0
    planned_end_time: str | None = None
    demand_id: str | None = None
    owner_id: str | None = None
    leader_id: str | None = None
    resource_links: list[dict] | None = None
    file_ids: list[str] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @field_validator("resource_links", mode="before")
    @classmethod
    def parse_resource_links(cls, v):
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return []
        return v

    @field_validator("file_ids", mode="before")
    @classmethod
    def parse_file_ids(cls, v):
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return []
        return v

    model_config = {"from_attributes": True}


class TaskProgressOut(BaseModel):
    id: str
    task_id: str
    user_id: str
    progress: int = 0
    content: str | None = None
    file_ids: list[str] | None = None
    created_at: datetime | None = None

    @field_validator("file_ids", mode="before")
    @classmethod
    def parse_file_ids(cls, v):
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return []
        return v

    model_config = {"from_attributes": True}
