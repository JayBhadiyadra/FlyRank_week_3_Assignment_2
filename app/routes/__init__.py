"""API route modules."""

from fastapi import APIRouter

from app.routes.health import router as health_router
from app.routes.tasks import router as tasks_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(tasks_router)

__all__ = ["api_router"]
