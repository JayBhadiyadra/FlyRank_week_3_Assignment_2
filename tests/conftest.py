"""Shared pytest fixtures."""

import os

import pytest
from fastapi.testclient import TestClient

# Default to local PostgreSQL unless the environment already sets DATABASE_URL.
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/tasks",
)

from app.main import app  # noqa: E402
from app.services.task_service import task_service  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def prepare_database() -> None:
    """Create schema once for the whole test session."""
    task_service.bootstrap()


@pytest.fixture(autouse=True)
def reset_storage() -> None:
    """Ensure each test starts from the three seed tasks."""
    task_service.reset()
    yield
    task_service.reset()


@pytest.fixture
def client() -> TestClient:
    """Return a FastAPI test client bound to the application."""
    return TestClient(app)
