"""Custom application exceptions."""


class TaskNotFoundError(Exception):
    """Raised when a requested task does not exist."""

    def __init__(self, task_id: int) -> None:
        self.task_id = task_id
        self.message = f"Task {task_id} not found"
        super().__init__(self.message)


class ValidationError(Exception):
    """Raised when request data fails business validation."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)
