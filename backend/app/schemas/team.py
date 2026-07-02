import json
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class JoinApplicationRequest(BaseModel):
    role: str = Field(min_length=1, max_length=50)
    skills: list[str] | None = None
    reason: str | None = None


class ApproveApplicationRequest(BaseModel):
    duty: str | None = Field(default=None, max_length=200)


class RejectApplicationRequest(BaseModel):
    reason: str = Field(min_length=1)


class InviteMemberRequest(BaseModel):
    platform_id: str = Field(min_length=1, max_length=20)
    suggested_role: str = Field(min_length=1, max_length=50)
    reason: str | None = None
    due_time: str | None = None


class UpdateMemberRequest(BaseModel):
    role: str | None = Field(default=None, max_length=50)
    duty: str | None = Field(default=None, max_length=200)


class TransferLeaderRequest(BaseModel):
    new_leader_id: str = Field(min_length=1)
    reason: str | None = None


class AssignmentItem(BaseModel):
    id: str | None = None
    title: str = Field(min_length=1, max_length=200)
    owner_id: str | None = None
    deliverable: str | None = None
    due_time: str | None = None
    status: str = Field(default="todo", pattern=r"^(todo|doing|done)$")


class SaveAssignmentsRequest(BaseModel):
    assignments: list[AssignmentItem]


class TaskMemberOut(BaseModel):
    id: str
    task_id: str
    user_id: str
    role: str
    duty: str | None = None
    source: str = "application"
    status: str = "active"
    name: str | None = None
    platform_id: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class JoinApplicationOut(BaseModel):
    id: str
    task_id: str
    user_id: str
    role: str
    skills: list[str] | None = None
    reason: str | None = None
    status: str = "pending"
    reviewer_id: str | None = None
    reject_reason: str | None = None
    created_at: datetime | None = None

    @field_validator("skills", mode="before")
    @classmethod
    def parse_skills(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return []
        return v

    model_config = {"from_attributes": True}


class AssignmentOut(BaseModel):
    id: str
    task_id: str
    title: str
    owner_id: str | None = None
    deliverable: str | None = None
    due_time: str | None = None
    status: str = "todo"
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class TeamDetailOut(BaseModel):
    task_id: str
    leader_id: str | None = None
    members: list[TaskMemberOut] = []
    applications: list[JoinApplicationOut] = []
    assignments: list[AssignmentOut] = []
