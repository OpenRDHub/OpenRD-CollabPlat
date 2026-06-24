from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # 应用
    app_env: str = "development"
    app_port: int = 8000

    # 数据库
    database_url: str = "postgresql+asyncpg://localhost:5432/openrd"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # 文件存储
    storage_backend: str = "local"
    upload_dir: str = "./uploads"
    max_file_size_mb: int = 20

    # 阿里云 OSS
    oss_access_key_id: str = ""
    oss_access_key_secret: str = ""
    oss_bucket_name: str = ""
    oss_endpoint: str = ""
    oss_public_url: str = ""

    # 阿里云短信
    sms_access_key_id: str = ""
    sms_access_key_secret: str = ""
    sms_sign_name: str = ""
    sms_template_register: str = ""
    sms_template_reset_password: str = ""
    sms_code_expire_minutes: int = 5
    sms_code_cooldown_seconds: int = 60


@lru_cache
def get_settings() -> Settings:
    return Settings()
