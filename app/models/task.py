"""Task domain model for in-memory storage."""

from dataclasses import dataclass


@dataclass
class Task:
    """Represents a single task stored in memory.

    Attributes:
        id: Unique integer identifier.
        title: Short human-readable task title.
        done: Whether the task has been completed.
    """

    id: int
    title: str
    done: bool = False
