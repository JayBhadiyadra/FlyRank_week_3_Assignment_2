"""Application configuration settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the Task Management API."""

    app_title: str = "Task Management API"
    app_description: str = (
        "A simple in-memory REST API for managing tasks. "
        "Built with FastAPI as part of the FlyRank backend assignment."
    )
    app_version: str = "1.0.0"
    api_prefix: str = ""

    model_config = SettingsConfigDict(env_prefix="APP_", case_sensitive=False)


settings = Settings()
