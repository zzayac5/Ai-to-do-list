# Deploy to Render

This repo includes a `render.yaml` blueprint that provisions:
- a Postgres database (`ai-todo-db`)
- a Python web service (`ai-todo-api`) running `uvicorn backend.main:app`

## Setup
1) In Render, choose **New +** -> **Blueprint** and point it at this repo.
2) After provisioning, open the `ai-todo-api` service -> **Environment** and set secrets:
   - `OPENAI_API_KEY`
   - `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_SMS_FROM` (optional until SMS is wired)
   - `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI` (optional until Calendar is wired)

## Notes
- Render's Postgres connection string is often `postgres://...`. The app rewrites it to
  `postgresql+psycopg://...` automatically for SQLAlchemy.
- `DB_AUTO_CREATE=true` creates tables on boot for MVP/dev. For production, switch to
  Alembic migrations and set `DB_AUTO_CREATE=false`.

