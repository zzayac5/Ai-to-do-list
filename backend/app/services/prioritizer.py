from __future__ import annotations

from datetime import datetime, timezone

from backend.app.schemas import PrioritizedTask, TaskRead


def _to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def estimate_completion_chance(task: TaskRead, *, as_of: datetime) -> float | None:
    """
    Heuristic MVP estimate. Replace later with a trained model using historical
    planned-vs-done data.
    """
    if task.status == "done":
        return 1.0
    if task.status == "canceled":
        return 0.0

    p = 0.65

    effort = task.effort_minutes or task.most_likely_minutes
    if effort:
        # 8h+ tasks are materially harder to finish in one day.
        p -= min(effort / 480.0, 1.0) * 0.35

    if task.due_at is not None:
        due = _to_utc(task.due_at)
        now = _to_utc(as_of)
        days_left = (due - now).total_seconds() / 86400.0
        if days_left < 0:
            p -= 0.25
        elif days_left < 1:
            p -= 0.10
        elif days_left > 7:
            p += 0.05

    if task.depends_on_ids:
        p -= 0.10

    return max(0.05, min(0.95, p))


def compute_priority_score(task: TaskRead, *, unblocks_count: int, as_of: datetime) -> float:
    if task.status in {"done", "canceled"}:
        return -1.0

    score = 0.0

    if task.urgency is not None:
        score += task.urgency * 1.5
    if task.importance is not None:
        score += task.importance * 2.0
    if task.impact is not None:
        score += task.impact * 1.0

    if task.due_at is not None:
        due = _to_utc(task.due_at)
        now = _to_utc(as_of)
        hours_left = (due - now).total_seconds() / 3600.0
        if hours_left <= 24:
            score += 10.0
        elif hours_left <= 72:
            score += 5.0
        elif hours_left <= 168:
            score += 2.0

    # A task that unlocks others is valuable even if not urgent.
    score += min(float(unblocks_count), 10.0) * 1.5

    # Slight penalty for tasks that are blocked (has unmet deps).
    if task.depends_on_ids:
        score -= 1.0

    return score


def prioritize(
    tasks: list[TaskRead],
    *,
    unblocks_by_task_id: dict[int, int],
    as_of: datetime,
) -> list[PrioritizedTask]:
    results: list[PrioritizedTask] = []
    for t in tasks:
        unblocks = unblocks_by_task_id.get(t.id, 0)
        score = compute_priority_score(t, unblocks_count=unblocks, as_of=as_of)
        chance = estimate_completion_chance(t, as_of=as_of)
        results.append(
            PrioritizedTask(
                task_id=t.id,
                priority_score=score,
                completion_chance=chance,
                rationale=None,
            )
        )

    results.sort(key=lambda r: r.priority_score, reverse=True)
    return results

