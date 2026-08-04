"""Root and health-check endpoints."""

from fastapi import APIRouter, status

from app.schemas.task import HealthResponse, RootResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/",
    response_model=RootResponse,
    status_code=status.HTTP_200_OK,
    summary="API root",
    description=(
        "Returns a welcome message and a pointer to the interactive "
        "Swagger documentation at `/docs`."
    ),
    responses={
        200: {
            "description": "Welcome payload",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Welcome to the Task Management API",
                        "docs": "/docs",
                    }
                }
            },
        }
    },
)
def root() -> RootResponse:
    """Return a welcome message for the API root."""
    return RootResponse(
        message="Welcome to the Task Management API",
        docs="/docs",
    )


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description=(
        "Lightweight liveness probe. Returns `{\"status\": \"ok\"}` when "
        "the service is running and able to accept requests."
    ),
    responses={
        200: {
            "description": "Service is healthy",
            "content": {
                "application/json": {
                    "example": {"status": "ok"}
                }
            },
        }
    },
)
def health() -> HealthResponse:
    """Return the current health status of the service."""
    return HealthResponse(status="ok")
