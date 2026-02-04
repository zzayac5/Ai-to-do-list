# AI To-Do List (FastAPI + LLM Tool Calling)

FastAPI backend that can capture tasks via chat and (optionally) use OpenAI function calling to persist + prioritize tasks.

## Prereqs
- Python 3.11+ (tested locally with Python 3.13)

## Local Setup (Backend)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Run the API:
```bash
uvicorn backend.main:app --reload --port 8000
```

By default, the backend runs with a **mock LLM** so it boots without API keys. To use the real model:
- set `OPENAI_API_KEY` in `.env`
- set `MOCK_LLM=false` (or delete it)
- optionally set `OPENAI_MODEL` (default: `gpt-4o-mini`)

Health check:
```bash
curl http://127.0.0.1:8000/health
```

## Use It Right Now (No API Keys)
The mock LLM shows the end-to-end tool loop: it will call tools like `create_task`, `list_tasks`, and `prioritize_tasks`.

1) Start the server:
```bash
uvicorn backend.main:app --reload --port 8000
```

2) Send a message (creates a task via tool calling):
```bash
curl -sS http://127.0.0.1:8000/chat \\
  -H "Content-Type: application/json" \\
  -d '{"message":"Tomorrow I need to call the bank about my car loan."}' | python3 -m json.tool
```

3) List tasks:
```bash
curl -sS http://127.0.0.1:8000/v1/tasks | python3 -m json.tool
```

4) Prioritize tasks:
```bash
curl -sS http://127.0.0.1:8000/v1/prioritize \\
  -H "Content-Type: application/json" \\
  -d '{}' | python3 -m json.tool
```

## Local Setup (Frontend)
The frontend is a static page that calls the backend.

From the repo root:
```bash
cd frontend
python3 -m http.server 5500
```

Then open:
- http://127.0.0.1:5500

## Quick Demo Script (No API Keys)
Runs a short mock conversation directly against the orchestrator + local DB:
```bash
python3 -m backend.scripts.conversation_test
```

## Using the Real OpenAI API
1) Put your key in `.env`:
```bash
OPENAI_API_KEY=...
MOCK_LLM=false
```

2) Restart the backend and use the same `/chat` endpoint. The model can now decide which tools to call.

## API Endpoints
- `GET /health`
- `POST /chat` (LLM tool-calling loop; persists tasks via tools)
- `POST /v1/tasks`, `GET /v1/tasks`, `GET /v1/tasks/{id}`, `PATCH /v1/tasks/{id}`
- `POST /v1/prioritize`
- `POST /v1/review_day`

## Notes
- Local DB defaults to SQLite at `./app.db` (ignored by git). Override with `DATABASE_URL`.
- Google Calendar + Twilio are stubbed right now (env vars are in `.env.example` for later).

## Deployment (Render)
This repo includes `render.yaml` (web service + Postgres). See `docs/deploy_render.md`.
