from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.db.init_db import init_db
from backend.app.db.session import get_db
from backend.app.llm.orchestrator import run_chat
from backend.app.schemas import (
    ChatRequest,
    ChatResponse,
    PrioritizeRequest,
    PrioritizeResponse,
    ReviewDayRequest,
    ReviewDayResponse,
    TaskCreate,
    TaskRead,
    TaskUpdate,
)
from backend.app.services import day_score_service, prioritizer, task_service
from backend.app.db.models import TaskDependency
from sqlalchemy import func, select


app = FastAPI(title="AI To-Do Backend", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    try:
        return run_chat(db, request=request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/tasks", response_model=TaskRead)
def create_task(request: TaskCreate, db: Session = Depends(get_db)) -> TaskRead:
    try:
        return task_service.create_task(db, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/v1/tasks", response_model=list[TaskRead])
def list_tasks(status: str | None = None, limit: int = 200, db: Session = Depends(get_db)) -> list[TaskRead]:
    return task_service.list_tasks(db, status=status, limit=limit)


@app.get("/v1/tasks/{task_id}", response_model=TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db)) -> TaskRead:
    task = task_service.get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.patch("/v1/tasks/{task_id}", response_model=TaskRead)
def patch_task(task_id: int, request: TaskUpdate, db: Session = Depends(get_db)) -> TaskRead:
    try:
        return task_service.update_task(db, task_id, request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/v1/prioritize", response_model=PrioritizeResponse)
def prioritize(request: PrioritizeRequest, db: Session = Depends(get_db)) -> PrioritizeResponse:
    as_of = request.as_of
    if as_of is None:
        from datetime import datetime, timezone

        as_of = datetime.now(tz=timezone.utc)

    tasks = task_service.list_tasks(db)
    if request.task_ids:
        wanted = set(request.task_ids)
        tasks = [t for t in tasks if t.id in wanted]

    rows = db.execute(
        select(TaskDependency.depends_on_id, func.count(TaskDependency.task_id)).group_by(TaskDependency.depends_on_id)
    ).all()
    unblocks = {int(dep_id): int(cnt) for dep_id, cnt in rows}

    results = prioritizer.prioritize(tasks, unblocks_by_task_id=unblocks, as_of=as_of)
    return PrioritizeResponse(as_of=as_of, results=results)


@app.post("/v1/review_day", response_model=ReviewDayResponse)
def review_day(request: ReviewDayRequest, db: Session = Depends(get_db)) -> ReviewDayResponse:
    from datetime import date as _date

    day = request.day or _date.today()
    planned = float(request.planned_points or 0.0)
    completed = float(request.completed_points or 0.0)
    return day_score_service.upsert_day_score(
        db,
        user_id=None,
        day=day,
        planned_points=planned,
        completed_points=completed,
        notes=request.notes,
    )

