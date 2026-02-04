from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv


# Load local development env vars from a `.env` file (no-op in production).
load_dotenv()


def _env(name: str, default: str | None = None) -> str | None:
    return os.getenv(name, default)


@dataclass(frozen=True)
class Settings:
    env: str = _env("ENV", "local") or "local"

    # DB
    database_url: str = _env("DATABASE_URL", "sqlite:///./app.db") or "sqlite:///./app.db"
    db_auto_create: bool = (_env("DB_AUTO_CREATE", "true") or "true").lower() in {"1", "true", "yes", "y"}

    # OpenAI
    openai_api_key: str | None = _env("OPENAI_API_KEY")
    openai_model: str = _env("OPENAI_MODEL", "gpt-4o-mini") or "gpt-4o-mini"

    # Twilio (optional until voice/SMS is wired)
    twilio_account_sid: str | None = _env("TWILIO_ACCOUNT_SID")
    twilio_auth_token: str | None = _env("TWILIO_AUTH_TOKEN")
    twilio_sms_from: str | None = _env("TWILIO_SMS_FROM")

    # Google OAuth / Calendar (optional until calendar is wired)
    google_client_id: str | None = _env("GOOGLE_CLIENT_ID")
    google_client_secret: str | None = _env("GOOGLE_CLIENT_SECRET")
    google_redirect_uri: str | None = _env("GOOGLE_REDIRECT_URI")
    google_calendar_id: str | None = _env("GOOGLE_CALENDAR_ID", "primary")

    # API
    cors_allow_origins: list[str] = field(
        default_factory=lambda: [
            o.strip()
            for o in (
                _env("CORS_ALLOW_ORIGINS", "http://127.0.0.1:5500,http://localhost:5500") or ""
            ).split(",")
            if o.strip()
        ]
    )


settings = Settings()

# Render commonly provides `postgres://...`, while SQLAlchemy expects `postgresql+psycopg://...`.
if settings.database_url.startswith("postgres://"):
    settings = Settings(database_url=settings.database_url.replace("postgres://", "postgresql+psycopg://", 1))
