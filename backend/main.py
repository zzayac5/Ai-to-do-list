"""
Compatibility entrypoint.

Keep `uvicorn backend.main:app` working while the real app lives in `backend/app`.
"""

from backend.app.main import app  # noqa: F401
