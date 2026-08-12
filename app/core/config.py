"""Application configuration settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the Task Management API."""

    app_title: str = "Task Management API"
    app_description: str = (
        "A REST API for managing tasks backed by PostgreSQL. "
        "Built with FastAPI as part of the FlyRank backend assignment."
    )
    app_version: str = "2.0.0"
    api_prefix: str = ""
    # Local PostgreSQL (no Docker in this assignment — containers come in A3).
    database_url: str = (
        "postgresql+psycopg://postgres:postgres@localhost:5432/tasks"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="APP_",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()


def _apply_database_url_override() -> None:
    """Prefer a plain DATABASE_URL env var when present."""
    import os

    url = os.getenv("DATABASE_URL")
    if url:
        settings.database_url = url


_apply_database_url_override()
