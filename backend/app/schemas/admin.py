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


class SetUserAuthorizationRequest(BaseModel):
    """单事务完成「角色变更 + 手动权限替换」的请求体。"""

    role: str = Field(min_length=1, max_length=20, pattern=r"^(requester|builder|operator|super_admin)$")
    manual_permission_ids: list[str] = []
    reason: str = Field(min_length=1, max_length=500)

    @field_validator("reason")
    @classmethod
    def reason_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("调整原因不能为空")
        return v


class UserPermissionDetail(BaseModel):
    role: str
    template_permission_ids: list[str]
    manual_permission_ids: list[str]
    effective_permission_ids: list[str]


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
