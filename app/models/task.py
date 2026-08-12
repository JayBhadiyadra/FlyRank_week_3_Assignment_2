"""Task SQLModel mapped to the PostgreSQL `tasks` table."""

from sqlmodel import Field, SQLModel


class Task(SQLModel, table=True):
    """Persistent task row stored in PostgreSQL.

    Attributes:
        id: Unique integer primary key (auto-increment).
        title: Short human-readable task title.
        done: Whether the task has been completed.
    """

    __tablename__ = "tasks"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(nullable=False, max_length=255)
    done: bool = Field(default=False, nullable=False)
