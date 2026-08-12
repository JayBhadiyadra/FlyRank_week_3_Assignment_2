"""Shared pytest fixtures."""

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Use a dedicated SQLite file for tests so local `tasks.db` is untouched.
TEST_DB = Path(__file__).resolve().parent / "test_tasks.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB.as_posix()}"

from app.db.session import reset_engine  # noqa: E402
from app.main import app  # noqa: E402
from app.services.task_service import task_service  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def prepare_database() -> None:
    """Create schema once for the whole test session."""
    reset_engine()
    if TEST_DB.exists():
        TEST_DB.unlink()
    task_service.bootstrap()
    yield
    reset_engine()
    if TEST_DB.exists():
        TEST_DB.unlink()


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
