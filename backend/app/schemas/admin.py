import json
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class CreateRoleRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    code: str = Field(min_length=1, max_length=30, pattern=r"^[a-z_]+$")
    permission_ids: list[str] = Field(min_length=1)


class UpdateRoleRequest(BaseModel):
    name: str | None = Field(default=None, max_length=50)
    permission_ids: list[str] | None = None


class SetUserPermissionsRequest(BaseModel):
    manual_permission_ids: list[str]
    reason: str = Field(min_length=1)


class RoleOut(BaseModel):
    name: str
    code: str
    permissions: list[str] = []


class PermissionOut(BaseModel):
    id: str
    name: str
    module: str


class SystemLogOut(BaseModel):
    id: str
    actor_id: str
    actor_role: str | None = None
    actor_nickname: str | None = None
    action: str
    module: str
    target_type: str | None = None
    target_id: str | None = None
    target_name: str | None = None
    risk_level: str = "low"
    detail: dict | None = None
    ip: str | None = None
    user_agent: str | None = None
    result: str = "success"
    created_at: datetime | None = None

    @field_validator("detail", mode="before")
    @classmethod
    def parse_detail(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return None
        return v

    model_config = {"from_attributes": True}
