from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from enum import StrEnum


class Environment(StrEnum):
    LOCAL = "LOCAL"
    STAGE = "STAGE"
    PROD = "PROD"


class Settings(BaseSettings):
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432

    S3_ENDPOINT_URL: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_BUCKET_NAME: str

    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    RABBITMQ_USER: str
    RABBITMQ_PASS: str
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int = 5672

    ENVIRONMENT: Environment = Environment.LOCAL
    DEBUG: bool = False

    @property
    def DATABASE_URL_ASYNC(self) -> str:
        # for FastAPI runtime (async SQLAlchemy)
        return (
            f"postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def RABBITMQ_URL(self) -> str:
        return f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASS}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/"

    @model_validator(mode='after')
    def set_debug_default(self):
        if self.DEBUG is None:
            if self.ENVIRONMENT == Environment.PROD:
                self.DEBUG = False
            else:
                self.DEBUG = True
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()  # type: ignore
