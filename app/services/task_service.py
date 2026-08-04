"""In-memory task service containing all business logic."""

from __future__ import annotations

from typing import Optional

from app.core.exceptions import TaskNotFoundError, ValidationError
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


def _seed_tasks() -> dict[int, Task]:
    """Return the default seed dataset of three example tasks."""
    return {
        1: Task(id=1, title="Buy groceries", done=False),
        2: Task(id=2, title="Write documentation", done=True),
        3: Task(id=3, title="Review pull request", done=False),
    }


class TaskService:
    """Manage tasks using process-local in-memory storage.

    All data is lost when the server restarts. This class is intentionally
    free of FastAPI / HTTP concerns so routes stay thin.
    """

    def __init__(self) -> None:
        self._tasks: dict[int, Task] = _seed_tasks()
        self._next_id: int = max(self._tasks.keys(), default=0) + 1

    def list_tasks(
        self,
        done: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> list[Task]:
        """Return tasks, optionally filtered by status and/or title search.

        Args:
            done: If provided, keep only tasks matching this completion flag.
            search: If provided, keep only tasks whose title contains the
                search text (case-insensitive).

        Returns:
            A list of matching tasks sorted by id ascending.
        """
        tasks = list(self._tasks.values())

        if done is not None:
            tasks = [task for task in tasks if task.done is done]

        if search is not None:
            needle = search.strip().lower()
            if needle:
                tasks = [task for task in tasks if needle in task.title.lower()]

        return sorted(tasks, key=lambda task: task.id)

    def get_task(self, task_id: int) -> Task:
        """Fetch a single task by id.

        Args:
            task_id: Identifier of the task to fetch.

        Returns:
            The matching task.

        Raises:
            TaskNotFoundError: If no task exists with the given id.
        """
        task = self._tasks.get(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    def create_task(self, payload: TaskCreate) -> Task:
        """Create and store a new task.

        Args:
            payload: Validated create payload.

        Returns:
            The newly created task.
        """
        title = payload.title.strip()
        if not title:
            raise ValidationError("title cannot be empty")

        task = Task(id=self._next_id, title=title, done=payload.done)
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    def update_task(self, task_id: int, payload: TaskUpdate) -> Task:
        """Update an existing task.

        Args:
            task_id: Identifier of the task to update.
            payload: Validated update payload. Only provided fields are applied.

        Returns:
            The updated task.

        Raises:
            TaskNotFoundError: If no task exists with the given id.
            ValidationError: If a provided title is empty.
        """
        task = self.get_task(task_id)

        if payload.title is not None:
            title = payload.title.strip()
            if not title:
                raise ValidationError("title cannot be empty")
            task.title = title

        if payload.done is not None:
            task.done = payload.done

        self._tasks[task_id] = task
        return task

    def delete_task(self, task_id: int) -> None:
        """Delete a task by id.

        Args:
            task_id: Identifier of the task to delete.

        Raises:
            TaskNotFoundError: If no task exists with the given id.
        """
        if task_id not in self._tasks:
            raise TaskNotFoundError(task_id)
        del self._tasks[task_id]

    def get_stats(self) -> dict[str, int]:
        """Compute aggregate task statistics.

        Returns:
            Dictionary with total, done, and pending counts.
        """
        total = len(self._tasks)
        done = sum(1 for task in self._tasks.values() if task.done)
        pending = total - done
        return {"total": total, "done": done, "pending": pending}

    def reset(self) -> None:
        """Reset storage back to the three seed tasks."""
        self._tasks = _seed_tasks()
        self._next_id = max(self._tasks.keys(), default=0) + 1


# Shared singleton used by the API routes.
task_service = TaskService()
