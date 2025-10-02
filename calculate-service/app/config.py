from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Calculate Service"
    app_description: str = "초등수학 문제 제공 API 및 웹 서비스"
    app_version: str = "1.0.0"
    enable_openapi: bool = True
    allowed_problem_categories: List[str] | None = None
    invite_token_ttl_minutes: int = 180
    invite_token_bytes: int = 16

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()  # type: ignore[call-arg]


__all__ = ["Settings", "get_settings"]
