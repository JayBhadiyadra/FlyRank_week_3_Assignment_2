"""PostgreSQL-backed task service containing all business logic."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import func, text
from sqlmodel import Session, col, select

from app.core.exceptions import TaskNotFoundError, ValidationError
from app.db.session import get_session, init_db
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate

SEED_TASKS: list[tuple[int, str, bool]] = [
    (1, "Buy groceries", False),
    (2, "Write documentation", True),
    (3, "Review pull request", False),
]


def _align_id_sequence(session: Session) -> None:
    """Align the tasks id sequence with the current MAX(id)."""
    session.execute(
        text(
            "SELECT setval("
            "pg_get_serial_sequence('tasks', 'id'), "
            "GREATEST((SELECT COALESCE(MAX(id), 1) FROM tasks), 1))"
        )
    )


def _seed_if_empty(session: Session) -> None:
    """Insert the three example tasks only when the table has no rows."""
    count = session.exec(select(func.count()).select_from(Task)).one()
    if count:
        return

    for task_id, title, done in SEED_TASKS:
        session.add(Task(id=task_id, title=title, done=done))
    session.flush()
    _align_id_sequence(session)


class TaskService:
    """Manage tasks using a PostgreSQL database.

    Data survives process restarts. This class stays free of FastAPI / HTTP
    concerns so route handlers remain thin.
    """

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
        """Return tasks, optionally filtered by status and/or title search.

        Args:
            done: If provided, keep only tasks matching this completion flag.
            search: If provided, keep only tasks whose title contains the
                search text (case-insensitive LIKE).

        Returns:
            A list of matching tasks sorted by id ascending.
        """
        with get_session() as session:
            statement = select(Task)

            if done is not None:
                statement = statement.where(Task.done == done)

            if search is not None:
                needle = search.strip()
                if needle:
                    statement = statement.where(
                        col(Task.title).ilike(f"%{needle}%")
                    )

            statement = statement.order_by(Task.id)
            return list(session.exec(statement).all())

    def get_task(self, task_id: int) -> Task:
        """Fetch a single task by id.

        Args:
            task_id: Identifier of the task to fetch.

        Returns:
            The matching task.

        Raises:
            TaskNotFoundError: If no task exists with the given id.
        """
        with get_session() as session:
            task = session.get(Task, task_id)
            if task is None:
                raise TaskNotFoundError(task_id)
            return task

    def create_task(self, payload: TaskCreate) -> Task:
        """Insert a new task row.

        Args:
            payload: Validated create payload.

        Returns:
            The newly created task.
        """
        title = payload.title.strip()
        if not title:
            raise ValidationError("title cannot be empty")

        with get_session() as session:
            task = Task(title=title, done=payload.done)
            session.add(task)
            session.flush()
            session.refresh(task)
            return task

    def update_task(self, task_id: int, payload: TaskUpdate) -> Task:
        """Update an existing task row.

        Args:
            task_id: Identifier of the task to update.
            payload: Validated update payload. Only provided fields are applied.

        Returns:
            The updated task.

        Raises:
            TaskNotFoundError: If no task exists with the given id.
            ValidationError: If a provided title is empty.
        """
        with get_session() as session:
            task = session.get(Task, task_id)
            if task is None:
                raise TaskNotFoundError(task_id)

            if payload.title is not None:
                title = payload.title.strip()
                if not title:
                    raise ValidationError("title cannot be empty")
                task.title = title

            if payload.done is not None:
                task.done = payload.done

            session.add(task)
            session.flush()
            session.refresh(task)
            return task

    def delete_task(self, task_id: int) -> None:
        """Delete a task row by id.

        Args:
            task_id: Identifier of the task to delete.

        Raises:
            TaskNotFoundError: If no task exists with the given id.
        """
        with get_session() as session:
            task = session.get(Task, task_id)
            if task is None:
                raise TaskNotFoundError(task_id)
            session.delete(task)

    def get_stats(self) -> dict[str, int]:
        """Compute aggregate task statistics with SQL COUNT.

        Returns:
            Dictionary with total, done, and pending counts.
        """
        with get_session() as session:
            total = session.exec(select(func.count()).select_from(Task)).one()
            done = session.exec(
                select(func.count())
                .select_from(Task)
                .where(Task.done.is_(True))
            ).one()
            pending = int(total) - int(done)
            return {
                "total": int(total),
                "done": int(done),
                "pending": pending,
            }

    def reset(self) -> None:
        """Clear all tasks and restore the three seed examples."""
        with get_session() as session:
            session.execute(text("DELETE FROM tasks"))
            for task_id, title, done in SEED_TASKS:
                session.add(Task(id=task_id, title=title, done=done))
            session.flush()
            _align_id_sequence(session)


# Shared singleton used by the API routes.
task_service = TaskService()
