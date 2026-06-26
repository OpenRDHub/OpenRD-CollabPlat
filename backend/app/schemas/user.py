from datetime import datetime

from pydantic import BaseModel, Field


class ProfileUpdateRequest(BaseModel):
    nickname: str | None = Field(default=None, max_length=50)
    avatar_url: str | None = Field(default=None, max_length=500)
    province: str | None = Field(default=None, max_length=50)
    occupation: str | None = Field(default=None, max_length=100)
    bio: str | None = Field(default=None, max_length=500)
    tags: list[str] | None = Field(default=None, max_length=6)


class PasswordChangeRequest(BaseModel):
    old_password: str = Field(min_length=6, max_length=50)
    new_password: str = Field(min_length=6, max_length=50)


class AdminUserUpdate(BaseModel):
    nickname: str | None = Field(default=None, max_length=50)
    role: str | None = Field(default=None, pattern=r"^(requester|builder|operator|super_admin)$")
    province: str | None = Field(default=None, max_length=50)
    occupation: str | None = Field(default=None, max_length=100)
    bio: str | None = Field(default=None, max_length=500)
    tags: list[str] | None = Field(default=None, max_length=6)


class UserDetail(BaseModel):
    id: str
    platform_id: str
    username: str
    phone: str
    role: str
    nickname: str | None = None
    avatar_url: str | None = None
    province: str | None = None
    occupation: str | None = None
    bio: str | None = None
    tags: list[str] | None = None
    is_onboarded: int = 0
    is_locked: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
