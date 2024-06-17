from pydantic import ConfigDict, field_validator, EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str = 'postgresql+asyncpg://postgres:admin@localhost:5432/hw_13'
    SECRET_KEY_JWT: str = "1234567890"
    ALGORITHM: str = "HS256"
    MAIL_USERNAME: EmailStr = "admin@localhost.com"
    MAIL_PASSWORD: str = "1234567890"
    MAIL_FROM: str = "localhost"
    MAIL_PORT: int = 56723498
    MAIL_SERVER: str = "localhost"
    REDIS_DOMAIN: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None
    CLD_NAME: str = "homework"
    CLD_API_KEY: int = 521545939732659
    CLD_API_SECRET: str = 'secret'

    @field_validator("ALGORITHM")
    @classmethod
    def validate_algorythm(cls, v):
        if v not in ["HS256", "HS512"]:
            raise ValueError("Invalid algorithm")
        return v

    model_config = ConfigDict(extra="ignore", env_file=".env", env_file_encoding="utf-8")


config = Settings()