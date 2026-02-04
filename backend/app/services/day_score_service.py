from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.db.models import DayScore
from backend.app.schemas import ReviewDayResponse


def upsert_day_score(
    db: Session,
    *,
    user_id: int | None,
    day: date,
    planned_points: float,
    completed_points: float,
    notes: str | None,
) -> ReviewDayResponse:
    score = 0.0
    if planned_points > 0:
        score = max(0.0, min(1.0, completed_points / planned_points))

    existing = db.execute(
        select(DayScore).where(DayScore.user_id == user_id, DayScore.day == day)
    ).scalar_one_or_none()

    if existing is None:
        existing = DayScore(
            user_id=user_id,
            day=day,
            planned_points=planned_points,
            completed_points=completed_points,
            score=score,
            notes=notes,
        )
        db.add(existing)
    else:
        existing.planned_points = planned_points
        existing.completed_points = completed_points
        existing.score = score
        existing.notes = notes
        db.add(existing)

    db.commit()
    db.refresh(existing)

    return ReviewDayResponse(
        day=existing.day,
        planned_points=existing.planned_points,
        completed_points=existing.completed_points,
        score=existing.score,
        notes=existing.notes,
    )

