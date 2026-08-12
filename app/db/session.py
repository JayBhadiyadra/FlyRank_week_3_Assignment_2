"""SQLAlchemy engine and session helpers for SQLite."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings

_engine = None


def get_engine():
    """Return a process-wide SQLAlchemy engine (created lazily)."""
    global _engine
    if _engine is None:
        connect_args = {}
        if settings.database_url.startswith("sqlite"):
            # Needed for FastAPI/TestClient using the DB across threads.
            connect_args["check_same_thread"] = False

        _engine = create_engine(
            settings.database_url,
            echo=False,
            connect_args=connect_args,
        )
    return _engine


def reset_engine() -> None:
    """Dispose and clear the cached engine (useful for tests)."""
    global _engine
    if _engine is not None:
        _engine.dispose()
        _engine = None


def init_db() -> None:
    """Create database tables if they do not already exist."""
    from app.models import task as _task  # noqa: F401

    SQLModel.metadata.create_all(get_engine())


@contextmanager
def get_session() -> Iterator[Session]:
    """Yield a short-lived database session that commits on success."""
    with Session(get_engine(), expire_on_commit=False) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
