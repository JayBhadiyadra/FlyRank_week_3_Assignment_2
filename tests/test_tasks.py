"""Tests for task CRUD, filters, stats, and reset endpoints."""

from fastapi.testclient import TestClient


def test_list_tasks(client: TestClient) -> None:
    """GET /tasks should return the three seed tasks."""
    response = client.get("/tasks")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 3
    assert {task["id"] for task in tasks} == {1, 2, 3}
    assert all("title" in task and "done" in task for task in tasks)


def test_get_task(client: TestClient) -> None:
    """GET /tasks/{id} should return the matching seed task."""
    response = client.get("/tasks/1")
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "Buy groceries",
        "done": False,
    }


def test_get_task_not_found(client: TestClient) -> None:
    """GET /tasks/{id} should return 404 JSON for unknown ids."""
    response = client.get("/tasks/99")
    assert response.status_code == 404
    assert response.json() == {"error": "Task 99 not found"}


def test_create_task(client: TestClient) -> None:
    """POST /tasks should create a task and return 201."""
    response = client.post("/tasks", json={"title": "Ship feature"})
    assert response.status_code == 201
    payload = response.json()
    assert payload["id"] == 4
    assert payload["title"] == "Ship feature"
    assert payload["done"] is False

    listed = client.get("/tasks").json()
    assert len(listed) == 4


def test_create_task_missing_title(client: TestClient) -> None:
    """POST /tasks without title should return 400."""
    response = client.post("/tasks", json={})
    assert response.status_code == 400
    assert "error" in response.json()


def test_create_task_empty_title(client: TestClient) -> None:
    """POST /tasks with an empty title should return 400."""
    response = client.post("/tasks", json={"title": ""})
    assert response.status_code == 400
    assert response.json()["error"] == "title cannot be empty"


def test_create_task_whitespace_title(client: TestClient) -> None:
    """POST /tasks with a whitespace-only title should return 400."""
    response = client.post("/tasks", json={"title": "   "})
    assert response.status_code == 400
    assert response.json()["error"] == "title cannot be empty"


def test_update_task(client: TestClient) -> None:
    """PUT /tasks/{id} should update provided fields."""
    response = client.put(
        "/tasks/1",
        json={"title": "Buy organic groceries", "done": True},
    )
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "Buy organic groceries",
        "done": True,
    }


def test_update_task_partial(client: TestClient) -> None:
    """PUT /tasks/{id} should allow updating only done."""
    response = client.put("/tasks/1", json={"done": True})
    assert response.status_code == 200
    payload = response.json()
    assert payload["done"] is True
    assert payload["title"] == "Buy groceries"


def test_update_task_not_found(client: TestClient) -> None:
    """PUT /tasks/{id} should return 404 for unknown ids."""
    response = client.put("/tasks/99", json={"done": True})
    assert response.status_code == 404
    assert response.json() == {"error": "Task 99 not found"}


def test_update_task_empty_title(client: TestClient) -> None:
    """PUT /tasks/{id} with empty title should return 400."""
    response = client.put("/tasks/1", json={"title": ""})
    assert response.status_code == 400
    assert response.json()["error"] == "title cannot be empty"


def test_delete_task(client: TestClient) -> None:
    """DELETE /tasks/{id} should remove the task and return 204."""
    response = client.delete("/tasks/1")
    assert response.status_code == 204
    assert response.content == b""

    follow_up = client.get("/tasks/1")
    assert follow_up.status_code == 404


def test_delete_task_not_found(client: TestClient) -> None:
    """DELETE /tasks/{id} should return 404 for unknown ids."""
    response = client.delete("/tasks/99")
    assert response.status_code == 404
    assert response.json() == {"error": "Task 99 not found"}


def test_filter_done_true(client: TestClient) -> None:
    """GET /tasks?done=true should return only completed tasks."""
    response = client.get("/tasks", params={"done": True})
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert all(task["done"] is True for task in tasks)


def test_filter_done_false(client: TestClient) -> None:
    """GET /tasks?done=false should return only pending tasks."""
    response = client.get("/tasks", params={"done": False})
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 2
    assert all(task["done"] is False for task in tasks)


def test_search_tasks(client: TestClient) -> None:
    """GET /tasks?search=text should match titles case-insensitively."""
    response = client.get("/tasks", params={"search": "doc"})
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Write documentation"


def test_stats(client: TestClient) -> None:
    """GET /stats should return aggregate counts for seed data."""
    response = client.get("/stats")
    assert response.status_code == 200
    assert response.json() == {"total": 3, "done": 1, "pending": 2}


def test_reset(client: TestClient) -> None:
    """POST /reset should restore seed tasks after mutations."""
    client.post("/tasks", json={"title": "Temporary"})
    client.delete("/tasks/1")

    response = client.post("/reset")
    assert response.status_code == 200
    assert response.json() == {"message": "All tasks have been reset"}

    tasks = client.get("/tasks").json()
    assert len(tasks) == 3
    assert {task["id"] for task in tasks} == {1, 2, 3}

    stats = client.get("/stats").json()
    assert stats == {"total": 3, "done": 1, "pending": 2}
