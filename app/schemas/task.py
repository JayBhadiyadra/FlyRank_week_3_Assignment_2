"""Pydantic schemas for task-related API contracts."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(
        ...,
        min_length=1,
        description="Title of the task. Must be a non-empty string.",
        examples=["Buy groceries"],
    )
    done: bool = Field(
        default=False,
        description="Whether the task is already completed.",
        examples=[False],
    )

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        """Reject titles that are empty or whitespace-only."""
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("title cannot be empty")
        return cleaned

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"title": "Buy groceries", "done": False},
                {"title": "Write documentation", "done": True},
            ]
        }
    )


class TaskUpdate(BaseModel):
    """Schema for updating an existing task. All fields optional for partial updates."""

    title: Optional[str] = Field(
        default=None,
        min_length=1,
        description="Updated title. Must be non-empty if provided.",
        examples=["Buy organic groceries"],
    )
    done: Optional[bool] = Field(
        default=None,
        description="Updated completion status.",
        examples=[True],
    )

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: Optional[str]) -> Optional[str]:
        """Reject titles that are empty or whitespace-only when provided."""
        if value is None:
            return value
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("title cannot be empty")
        return cleaned

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"title": "Buy organic groceries", "done": True},
                {"done": True},
                {"title": "Review pull request"},
            ]
        }
    )


class TaskResponse(BaseModel):
    """Schema returned for a single task."""

    id: int = Field(..., description="Unique task identifier.", examples=[1])
    title: str = Field(..., description="Task title.", examples=["Buy groceries"])
    done: bool = Field(..., description="Completion status.", examples=[False])

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {"id": 1, "title": "Buy groceries", "done": False},
            ]
        },
    )


class HealthResponse(BaseModel):
    """Schema for the health check endpoint."""

    status: str = Field(..., description="Service health status.", examples=["ok"])

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"status": "ok"}]}
    )


class RootResponse(BaseModel):
    """Schema for the API root welcome message."""

    message: str = Field(
        ...,
        description="Welcome message for the API.",
        examples=["Welcome to the Task Management API"],
    )
    docs: str = Field(
        ...,
        description="Path to interactive API documentation.",
        examples=["/docs"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "message": "Welcome to the Task Management API",
                    "docs": "/docs",
                }
            ]
        }
    )


class StatsResponse(BaseModel):
    """Schema for aggregated task statistics."""

    total: int = Field(..., description="Total number of tasks.", examples=[3])
    done: int = Field(..., description="Number of completed tasks.", examples=[1])
    pending: int = Field(..., description="Number of incomplete tasks.", examples=[2])

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"total": 3, "done": 1, "pending": 2}]
        }
    )


class ErrorResponse(BaseModel):
    """Standard JSON error body."""

    error: str = Field(
        ...,
        description="Human-readable error message.",
        examples=["Task 99 not found"],
    )

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"error": "Task 99 not found"}]}
    )


class MessageResponse(BaseModel):
    """Generic success message response."""

    message: str = Field(
        ...,
        description="Human-readable success message.",
        examples=["All tasks have been reset"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"message": "All tasks have been reset"}]
        }
    )
