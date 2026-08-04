"""Shared pytest fixtures."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.task_service import task_service


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
