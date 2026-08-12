"""Application configuration settings."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root (Assignment_2/) so the SQLite file lands next to the app package.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SQLITE_PATH = PROJECT_ROOT / "tasks.db"


class Settings(BaseSettings):
    """Runtime configuration for the Task Management API."""

    app_title: str = "Task Management API"
    app_description: str = (
        "A REST API for managing tasks backed by SQLite. "
        "Built with FastAPI as part of the FlyRank backend assignment."
    )
    app_version: str = "2.0.0"
    api_prefix: str = ""
    database_url: str = f"sqlite:///{DEFAULT_SQLITE_PATH.as_posix()}"

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
