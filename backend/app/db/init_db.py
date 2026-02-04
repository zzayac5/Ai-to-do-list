from __future__ import annotations

from backend.app.core.config import settings
from backend.app.db.base import Base
from backend.app.db.session import engine

# Import models so they are registered on Base.metadata
from backend.app.db import models as _models  # noqa: F401


def init_db() -> None:
    """
    Lightweight bootstrap for local/dev.

    In production, prefer Alembic migrations. This exists so `uvicorn` can boot
    without an extra migration step while iterating.
    """
    if not settings.db_auto_create:
        return
    Base.metadata.create_all(bind=engine)

