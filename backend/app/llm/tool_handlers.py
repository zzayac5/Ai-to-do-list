from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.db.models import Task, TaskDependency
from backend.app.schemas import PrioritizeResponse, TaskCreate, TaskUpdate
from backend.app.services import calendar_service, day_score_service, prioritizer, task_service


def _parse_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None
    v = value.strip()
    if v.endswith("Z"):
        v = v[:-1] + "+00:00"
    return datetime.fromisoformat(v)


def _parse_date(value: str | None) -> date | None:
    if value is None:
        return None
    return date.fromisoformat(value.strip())


def _now_utc() -> datetime:
    return datetime.now(tz=timezone.utc)


@dataclass(frozen=True)
class ToolContext:
    db: Session
    user_id: int | None = None


def execute_tool(ctx: ToolContext, *, name: str, arguments_json: str) -> dict[str, Any]:
    """
    Execute one tool call and return a JSON-serializable result.

    Return format:
      {"ok": bool, "result": ..., "error": "..."}
    """
    try:
        args = json.loads(arguments_json or "{}")
    except json.JSONDecodeError as e:
        return {"ok": False, "error": f"Invalid JSON arguments for {name}: {e}"}

    try:
        if name == "create_task":
            # Convert string datetimes to real datetimes for pydantic validation.
            if "due_at" in args:
                args["due_at"] = _parse_datetime(args.get("due_at"))
            data = TaskCreate(**args)
            task = task_service.create_task(ctx.db, data, user_id=ctx.user_id)
            return {"ok": True, "result": task.model_dump()}

        if name == "update_task":
            task_id = int(args["task_id"])
            if "due_at" in args:
                args["due_at"] = _parse_datetime(args.get("due_at"))
            if "task_id" in args:
                args.pop("task_id")
            data = TaskUpdate(**args)
            task = task_service.update_task(ctx.db, task_id, data)
            return {"ok": True, "result": task.model_dump()}

        if name == "list_tasks":
            status = args.get("status")
            limit = int(args.get("limit") or 200)
            tasks = task_service.list_tasks(ctx.db, user_id=ctx.user_id, status=status, limit=limit)
            return {"ok": True, "result": [t.model_dump() for t in tasks]}

        if name == "prioritize_tasks":
            task_ids = args.get("task_ids")
            as_of = _parse_datetime(args.get("as_of")) or _now_utc()

            if task_ids:
                tasks = [t for t in task_service.list_tasks(ctx.db, user_id=ctx.user_id) if t.id in set(task_ids)]
            else:
                tasks = task_service.list_tasks(ctx.db, user_id=ctx.user_id)

            # Count how many tasks each task unblocks (dependents).
            rows = ctx.db.execute(
                select(TaskDependency.depends_on_id, func.count(TaskDependency.task_id))
                .group_by(TaskDependency.depends_on_id)
            ).all()
            unblocks = {int(dep_id): int(cnt) for dep_id, cnt in rows}

            results = prioritizer.prioritize(tasks, unblocks_by_task_id=unblocks, as_of=as_of)
            payload = PrioritizeResponse(as_of=as_of, results=results)
            return {"ok": True, "result": payload.model_dump()}

        if name == "estimate_completion":
            task_id = int(args["task_id"])
            as_of = _parse_datetime(args.get("as_of")) or _now_utc()
            task = task_service.get_task(ctx.db, task_id)
            if task is None:
                return {"ok": False, "error": f"Task {task_id} not found."}
            chance = prioritizer.estimate_completion_chance(task, as_of=as_of)
            return {"ok": True, "result": {"task_id": task_id, "as_of": as_of.isoformat(), "completion_chance": chance}}

        if name == "review_day":
            day = _parse_date(args.get("day")) or date.today()
            planned_points = float(args.get("planned_points") or 0.0)
            completed_points = float(args.get("completed_points") or 0.0)
            notes = args.get("notes")
            resp = day_score_service.upsert_day_score(
                ctx.db,
                user_id=ctx.user_id,
                day=day,
                planned_points=planned_points,
                completed_points=completed_points,
                notes=notes,
            )
            return {"ok": True, "result": resp.model_dump()}

        if name == "calendar_read":
            time_min = _parse_datetime(args.get("time_min"))
            time_max = _parse_datetime(args.get("time_max"))
            if time_min is None or time_max is None:
                return {"ok": False, "error": "time_min and time_max are required ISO datetimes."}
            calendar_id = args.get("calendar_id") or "primary"
            result = calendar_service.read_calendar_busy(
                user_id=ctx.user_id,
                time_min=time_min,
                time_max=time_max,
                calendar_id=calendar_id,
            )
            return {"ok": True, "result": result}

        if name == "calendar_move":
            event_id = str(args.get("event_id") or "")
            new_start = _parse_datetime(args.get("new_start"))
            new_end = _parse_datetime(args.get("new_end"))
            if not event_id or new_start is None or new_end is None:
                return {"ok": False, "error": "event_id, new_start, new_end are required."}
            calendar_id = args.get("calendar_id") or "primary"
            result = calendar_service.move_calendar_event(
                user_id=ctx.user_id,
                event_id=event_id,
                new_start=new_start,
                new_end=new_end,
                calendar_id=calendar_id,
            )
            return {"ok": True, "result": result}

        return {"ok": False, "error": f"Unknown tool: {name}"}

    except Exception as e:
        return {"ok": False, "error": f"{name} failed: {type(e).__name__}: {e}"}

