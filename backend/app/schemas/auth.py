from pydantic import BaseModel, Field, field_validator


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    phone: str = Field(pattern=r"^1[3-9]\d{9}$")
    password: str = Field(min_length=6, max_length=50)
    sms_code: str = Field(min_length=4, max_length=6)
    nickname: str | None = Field(default=None, max_length=50)


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class SmsCodeRequest(BaseModel):
    phone: str = Field(pattern=r"^1[3-9]\d{9}$")
    scene: str = Field(pattern=r"^(register|reset_password)$")


class ResetPasswordRequest(BaseModel):
    phone: str = Field(pattern=r"^1[3-9]\d{9}$")
    sms_code: str = Field(min_length=4, max_length=6)
    new_password: str = Field(min_length=6, max_length=50)


class OnboardingRequest(BaseModel):
    role: str = Field(pattern=r"^(requester|builder)$")
    nickname: str | None = Field(default=None, max_length=50)
    province: str | None = None
    occupation: str | None = None
    bio: str | None = None
    tags: list[str] | None = Field(default=None, max_length=6)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
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

    @field_validator("tags", mode="before")
    @classmethod
    def parse_tags(cls, v):
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return []
        return v

    model_config = {"from_attributes": True}
