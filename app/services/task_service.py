"""Task service during Stage 0: PostgreSQL bootstrap + in-memory CRUD.

The database table and first-run seed are created on startup. Request handlers
still use the in-memory store until later stages switch them to SQL.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import func, text
from sqlmodel import Session, select

from app.core.exceptions import TaskNotFoundError, ValidationError
from app.db.session import get_session, init_db
from app.models.task import Task as DbTask
from app.schemas.task import TaskCreate, TaskUpdate


class Task:
    """Simple in-memory task object used until SQL CRUD is wired up."""

    def __init__(self, id: int, title: str, done: bool = False) -> None:
        self.id = id
        self.title = title
        self.done = done


SEED_TASKS: list[tuple[int, str, bool]] = [
    (1, "Buy groceries", False),
    (2, "Write documentation", True),
    (3, "Review pull request", False),
]


def _seed_tasks() -> dict[int, Task]:
    return {
        task_id: Task(id=task_id, title=title, done=done)
        for task_id, title, done in SEED_TASKS
    }


def _align_id_sequence(session: Session) -> None:
    session.execute(
        text(
            "SELECT setval("
            "pg_get_serial_sequence('tasks', 'id'), "
            "GREATEST((SELECT COALESCE(MAX(id), 1) FROM tasks), 1))"
        )
    )


def _seed_if_empty(session: Session) -> None:
    count = session.exec(select(func.count()).select_from(DbTask)).one()
    if count:
        return
    for task_id, title, done in SEED_TASKS:
        session.add(DbTask(id=task_id, title=title, done=done))
    session.flush()
    _align_id_sequence(session)


class TaskService:
    """Stage 0 service: DB bootstrap on start, in-memory request handling."""

    def __init__(self) -> None:
        self._tasks: dict[int, Task] = _seed_tasks()
        self._next_id: int = max(self._tasks.keys(), default=0) + 1

    def bootstrap(self) -> None:
        """Create the schema if needed and seed example tasks once."""
        init_db()
        with get_session() as session:
            _seed_if_empty(session)

    def list_tasks(
        self,
        done: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> list[Task]:
        tasks = list(self._tasks.values())
        if done is not None:
            tasks = [task for task in tasks if task.done is done]
        if search is not None:
            needle = search.strip().lower()
            if needle:
                tasks = [task for task in tasks if needle in task.title.lower()]
        return sorted(tasks, key=lambda task: task.id)

    def get_task(self, task_id: int) -> Task:
        task = self._tasks.get(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    def create_task(self, payload: TaskCreate) -> Task:
        title = payload.title.strip()
        if not title:
            raise ValidationError("title cannot be empty")
        task = Task(id=self._next_id, title=title, done=payload.done)
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    def update_task(self, task_id: int, payload: TaskUpdate) -> Task:
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
        if task_id not in self._tasks:
            raise TaskNotFoundError(task_id)
        del self._tasks[task_id]

    def get_stats(self) -> dict[str, int]:
        total = len(self._tasks)
        done = sum(1 for task in self._tasks.values() if task.done)
        return {"total": total, "done": done, "pending": total - done}

    def reset(self) -> None:
        self._tasks = _seed_tasks()
        self._next_id = max(self._tasks.keys(), default=0) + 1


task_service = TaskService()
