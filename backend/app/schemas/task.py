from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.models.task import TaskStage


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
    stage: TaskStage
    content: str | None = None
    file_ids: list[str] | None = None
    next_plan: str | None = None
    base_stage: TaskStage | None = None


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
    stage: TaskStage
    priority: str = "medium"
    task_type: str | None = None
    demand_id: str | None = None
    planned_end_time: str | None = None
    owner_id: str | None = None
    leader_id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class MyTaskOut(TaskOut):
    my_role: str
    my_stage: str


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
    stage: TaskStage
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
    content: str | None = None
    file_ids: list[str] | None = None
    stage: str | None = None
    next_plan: str | None = None
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
