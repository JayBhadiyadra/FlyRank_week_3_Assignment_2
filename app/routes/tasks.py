"""Task CRUD and helper endpoints."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.core.exceptions import TaskNotFoundError, ValidationError
from app.schemas.task import (
    ErrorResponse,
    MessageResponse,
    StatsResponse,
    TaskCreate,
    TaskResponse,
    TaskUpdate,
)
from app.services.task_service import task_service

router = APIRouter(tags=["Tasks"])


def _not_found(task_id: int) -> HTTPException:
    """Build a consistent 404 HTTPException for a missing task."""
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"error": f"Task {task_id} not found"},
    )


def _bad_request(message: str) -> HTTPException:
    """Build a consistent 400 HTTPException for validation failures."""
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={"error": message},
    )


@router.get(
    "/tasks",
    response_model=list[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="List tasks",
    description=(
        "Return all tasks from SQLite. "
        "Optionally filter by completion status with `done=true|false` "
        "and/or search titles with `search=<text>` (case-insensitive SQL LIKE)."
    ),
    responses={
        200: {
            "description": "List of tasks",
            "content": {
                "application/json": {
                    "example": [
                        {"id": 1, "title": "Buy groceries", "done": False},
                        {"id": 2, "title": "Write documentation", "done": True},
                        {"id": 3, "title": "Review pull request", "done": False},
                    ]
                }
            },
        }
    },
)
def list_tasks(
    done: Optional[bool] = Query(
        default=None,
        description="Filter by completion status. Example: `true` or `false`.",
        examples=[True],
    ),
    search: Optional[str] = Query(
        default=None,
        description="Case-insensitive substring match against task titles.",
        examples=["doc"],
    ),
) -> list[TaskResponse]:
    """List tasks with optional done filter and title search."""
    tasks = task_service.list_tasks(done=done, search=search)
    return [TaskResponse.model_validate(task) for task in tasks]


@router.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Get task by ID",
    description="Retrieve a single task by its integer identifier from SQLite.",
    responses={
        200: {
            "description": "Task found",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "title": "Buy groceries",
                        "done": False,
                    }
                }
            },
        },
        404: {
            "model": ErrorResponse,
            "description": "Task not found",
            "content": {
                "application/json": {
                    "example": {"error": "Task 99 not found"}
                }
            },
        },
    },
)
def get_task(task_id: int) -> TaskResponse:
    """Return a single task or raise 404 if it does not exist."""
    try:
        task = task_service.get_task(task_id)
    except TaskNotFoundError as exc:
        raise _not_found(exc.task_id) from exc
    return TaskResponse.model_validate(task)


@router.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create task",
    description=(
        "Insert a new task into SQLite. `title` is required and must be a "
        "non-empty string (whitespace-only titles are rejected). "
        "`done` defaults to `false`."
    ),
    responses={
        201: {
            "description": "Task created",
            "content": {
                "application/json": {
                    "example": {
                        "id": 4,
                        "title": "Ship feature",
                        "done": False,
                    }
                }
            },
        },
        400: {
            "model": ErrorResponse,
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {"error": "title cannot be empty"}
                }
            },
        },
        422: {
            "description": "Request body failed schema validation",
        },
    },
)
def create_task(payload: TaskCreate) -> TaskResponse:
    """Create a new task from a validated request body."""
    try:
        task = task_service.create_task(payload)
    except ValidationError as exc:
        raise _bad_request(exc.message) from exc
    return TaskResponse.model_validate(task)


@router.put(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Update task",
    description=(
        "Update an existing SQLite task row. Provide `title` and/or `done`. "
        "If `title` is provided it must be a non-empty string."
    ),
    responses={
        200: {
            "description": "Task updated",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "title": "Buy organic groceries",
                        "done": True,
                    }
                }
            },
        },
        400: {
            "model": ErrorResponse,
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {"error": "title cannot be empty"}
                }
            },
        },
        404: {
            "model": ErrorResponse,
            "description": "Task not found",
            "content": {
                "application/json": {
                    "example": {"error": "Task 99 not found"}
                }
            },
        },
        422: {
            "description": "Request body failed schema validation",
        },
    },
)
def update_task(task_id: int, payload: TaskUpdate) -> TaskResponse:
    """Update fields on an existing task."""
    try:
        task = task_service.update_task(task_id, payload)
    except TaskNotFoundError as exc:
        raise _not_found(exc.task_id) from exc
    except ValidationError as exc:
        raise _bad_request(exc.message) from exc
    return TaskResponse.model_validate(task)


@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task",
    description=(
        "Delete a task row from SQLite by its integer identifier. "
        "Returns 204 with no body on success."
    ),
    responses={
        204: {"description": "Task deleted"},
        404: {
            "model": ErrorResponse,
            "description": "Task not found",
            "content": {
                "application/json": {
                    "example": {"error": "Task 99 not found"}
                }
            },
        },
    },
)
def delete_task(task_id: int) -> None:
    """Delete a task or raise 404 if it does not exist."""
    try:
        task_service.delete_task(task_id)
    except TaskNotFoundError as exc:
        raise _not_found(exc.task_id) from exc


@router.get(
    "/stats",
    response_model=StatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Task statistics",
    description=(
        "Return aggregate counts using SQL COUNT(): "
        "`total`, `done`, and `pending`."
    ),
    responses={
        200: {
            "description": "Current statistics",
            "content": {
                "application/json": {
                    "example": {"total": 3, "done": 1, "pending": 2}
                }
            },
        }
    },
)
def get_stats() -> StatsResponse:
    """Return total / done / pending task counts."""
    return StatsResponse(**task_service.get_stats())


@router.post(
    "/reset",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Reset tasks",
    description=(
        "Delete all rows and restore the three seed example tasks in SQLite. "
        "Useful for demos and automated tests."
    ),
    responses={
        200: {
            "description": "Storage reset successfully",
            "content": {
                "application/json": {
                    "example": {"message": "All tasks have been reset"}
                }
            },
        }
    },
)
def reset_tasks() -> MessageResponse:
    """Restore the default seed tasks and clear any created data."""
    task_service.reset()
    return MessageResponse(message="All tasks have been reset")
