from __future__ import annotations

from datetime import datetime


def read_calendar_busy(
    *,
    user_id: int | None,
    time_min: datetime,
    time_max: datetime,
    calendar_id: str = "primary",
) -> dict:
    # TODO: Implement Google Calendar integration (OAuth + freebusy/events.list).
    return {
        "ok": False,
        "error": "calendar_read not implemented yet",
        "calendar_id": calendar_id,
        "time_min": time_min.isoformat(),
        "time_max": time_max.isoformat(),
        "busy": [],
    }


def move_calendar_event(
    *,
    user_id: int | None,
    event_id: str,
    new_start: datetime,
    new_end: datetime,
    calendar_id: str = "primary",
) -> dict:
    # TODO: Implement Google Calendar integration (events.patch with user confirmation).
    return {
        "ok": False,
        "error": "calendar_move not implemented yet",
        "calendar_id": calendar_id,
        "event_id": event_id,
        "new_start": new_start.isoformat(),
        "new_end": new_end.isoformat(),
    }

