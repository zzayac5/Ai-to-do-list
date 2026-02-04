from __future__ import annotations

from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from backend.app.db.models import Task, TaskDependency
from backend.app.schemas import TaskCreate, TaskRead, TaskUpdate


def _task_to_read(db: Session, task: Task) -> TaskRead:
    depends_on_ids = list(
        db.execute(select(TaskDependency.depends_on_id).where(TaskDependency.task_id == task.id)).scalars().all()
    )
    return TaskRead(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        due_at=task.due_at,
        urgency=task.urgency,
        importance=task.importance,
        impact=task.impact,
        effort_minutes=task.effort_minutes,
        optimistic_minutes=task.optimistic_minutes,
        most_likely_minutes=task.most_likely_minutes,
        pessimistic_minutes=task.pessimistic_minutes,
        external_constraints=task.external_constraints,
        required_resources=task.required_resources or [],
        required_people=task.required_people or [],
        tags=task.tags or [],
        depends_on_ids=depends_on_ids,
        created_at=task.created_at,
        updated_at=task.updated_at,
        completed_at=task.completed_at,
    )


def create_task(db: Session, data: TaskCreate, user_id: int | None = None) -> TaskRead:
    title = (data.title or "").strip()
    description = (data.description or "").strip() or None
    if not title:
        title = (description or "").strip()
    if not title:
        raise ValueError("Task must have at least a title or description.")

    task = Task(
        user_id=user_id,
        title=title[:200],
        description=description,
        status=data.status or "inbox",
        due_at=data.due_at,
        urgency=data.urgency,
        importance=data.importance,
        impact=data.impact,
        effort_minutes=data.effort_minutes,
        optimistic_minutes=data.optimistic_minutes,
        most_likely_minutes=data.most_likely_minutes,
        pessimistic_minutes=data.pessimistic_minutes,
        external_constraints=data.external_constraints,
        required_resources=list(data.required_resources or []),
        required_people=list(data.required_people or []),
        tags=list(data.tags or []),
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    _set_dependencies(db, task.id, list(data.depends_on_ids or []))
    db.refresh(task)
    return _task_to_read(db, task)


def get_task(db: Session, task_id: int) -> TaskRead | None:
    task = db.get(Task, task_id)
    if task is None:
        return None
    return _task_to_read(db, task)


def list_tasks(db: Session, user_id: int | None = None, status: str | None = None, limit: int = 200) -> list[TaskRead]:
    stmt = select(Task).order_by(Task.created_at.desc()).limit(limit)
    if user_id is not None:
        stmt = stmt.where(Task.user_id == user_id)
    if status is not None:
        stmt = stmt.where(Task.status == status)
    tasks = list(db.execute(stmt).scalars().all())
    return [_task_to_read(db, t) for t in tasks]


def update_task(db: Session, task_id: int, data: TaskUpdate) -> TaskRead:
    task = db.get(Task, task_id)
    if task is None:
        raise ValueError(f"Task {task_id} not found.")

    if data.title is not None:
        task.title = data.title.strip()[:200]
    if data.description is not None:
        task.description = data.description.strip() or None
    if data.status is not None:
        task.status = data.status
        if data.status == "done" and task.completed_at is None:
            task.completed_at = datetime.utcnow()
        if data.status != "done":
            task.completed_at = None

    if data.due_at is not None:
        task.due_at = data.due_at

    for field in ("urgency", "importance", "impact", "effort_minutes", "optimistic_minutes", "most_likely_minutes", "pessimistic_minutes"):
        val = getattr(data, field)
        if val is not None:
            setattr(task, field, val)

    if data.external_constraints is not None:
        task.external_constraints = data.external_constraints

    if data.required_resources is not None:
        task.required_resources = list(data.required_resources)
    if data.required_people is not None:
        task.required_people = list(data.required_people)
    if data.tags is not None:
        task.tags = list(data.tags)

    db.add(task)
    db.commit()
    db.refresh(task)

    if data.depends_on_ids is not None:
        _set_dependencies(db, task.id, list(data.depends_on_ids))
        db.refresh(task)

    return _task_to_read(db, task)


def _set_dependencies(db: Session, task_id: int, depends_on_ids: list[int]) -> None:
    # Replace strategy keeps it simple (fine for MVP).
    db.execute(delete(TaskDependency).where(TaskDependency.task_id == task_id))
    for dep_id in sorted({i for i in depends_on_ids if i != task_id}):
        db.add(TaskDependency(task_id=task_id, depends_on_id=dep_id))
    db.commit()

