from pydantic import BaseModel, Field, field_validator
import re


# 中国大陆手机号
PHONE_RE = re.compile(r'^1[3-9]\d{9}$')
    
def validate_phone(value: str) -> str:
    """
    校验手机号，返回清洗后的值（已 strip）。
    非法时抛出 ValueError，文案与前端 utils/validate.ts 的 validatePhone 保持一致。
    抽出为模块级函数，供多个 Request Schema 复用。
    """
    phone = value.strip()

    # 1. 空值校验
    if not phone:
        raise ValueError('请输入手机号')

    # 2. 纯数字校验
    if not phone.isdigit():
        raise ValueError('手机号只能为数字')

    # 3. 长度校验
    if len(phone) != 11:
        raise ValueError('手机号应为 11 位数字')

    # 4. 号段正则校验
    if not PHONE_RE.match(phone):
        raise ValueError('手机号格式不正确')

    return phone


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    phone: str 
    password: str = Field(min_length=6, max_length=50)
    sms_code: str = Field(min_length=4, max_length=6)
    nickname: str | None = Field(default=None, max_length=50)
    
    @field_validator('phone')
    def validate_phone_field(cls, v: str) -> str:
        return validate_phone(v)


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class SmsCodeRequest(BaseModel):
    phone: str
    scene: str
    
    @field_validator('phone')
    def validate_phone_field(cls, v: str) -> str:
        return validate_phone(v)
    
    @field_validator('scene')
    def validate_scene(cls, v: str) -> str:
        if v not in ('register', 'reset_password'):
            raise ValueError('场景参数不合法')
        return v


class ResetPasswordRequest(BaseModel):
    phone: str 
    sms_code: str = Field(min_length=4, max_length=6)
    new_password: str = Field(min_length=6, max_length=50)

    @field_validator('phone')
    def validate_phone_field(cls, v: str) -> str:
        return validate_phone(v)


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
