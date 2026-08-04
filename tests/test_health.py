"""Tests for root and health endpoints."""

from fastapi.testclient import TestClient


def test_root(client: TestClient) -> None:
    """GET / should return a welcome message and docs pointer."""
    response = client.get("/")
    assert response.status_code == 200
    payload = response.json()
    assert payload["message"] == "Welcome to the Task Management API"
    assert payload["docs"] == "/docs"


def test_health(client: TestClient) -> None:
    """GET /health should report a healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
