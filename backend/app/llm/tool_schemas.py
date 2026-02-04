from __future__ import annotations


def get_tool_schemas() -> list[dict]:
    """
    OpenAI tool (function calling) schemas.

    Keep parameters flat (avoid nested objects) to reduce schema friction.
    """
    tools: list[dict] = []

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "create_task",
                "description": "Create a new task in the to-do list.",
                "parameters": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "title": {"type": "string", "description": "Short title (use description if no title)."},
                        "description": {"type": "string", "description": "Longer details."},
                        "status": {"type": "string", "description": "Task status (inbox/planned/in_progress/done/canceled)."},
                        "due_at": {"type": "string", "description": "ISO 8601 datetime, e.g. 2026-02-04T17:00:00Z"},
                        "urgency": {"type": "integer", "minimum": 0, "maximum": 10},
                        "importance": {"type": "integer", "minimum": 0, "maximum": 10},
                        "impact": {"type": "integer", "minimum": 0, "maximum": 10},
                        "effort_minutes": {"type": "integer", "minimum": 1},
                        "optimistic_minutes": {"type": "integer", "minimum": 1},
                        "most_likely_minutes": {"type": "integer", "minimum": 1},
                        "pessimistic_minutes": {"type": "integer", "minimum": 1},
                        "external_constraints": {"type": "string"},
                        "required_resources": {"type": "array", "items": {"type": "string"}},
                        "required_people": {"type": "array", "items": {"type": "string"}},
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "depends_on_ids": {"type": "array", "items": {"type": "integer", "minimum": 1}},
                    },
                    "required": ["title"],
                },
            },
        }
    )

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "update_task",
                "description": "Update an existing task by id.",
                "parameters": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "task_id": {"type": "integer", "minimum": 1},
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "status": {"type": "string"},
                        "due_at": {"type": "string", "description": "ISO 8601 datetime"},
                        "urgency": {"type": "integer", "minimum": 0, "maximum": 10},
                        "importance": {"type": "integer", "minimum": 0, "maximum": 10},
                        "impact": {"type": "integer", "minimum": 0, "maximum": 10},
                        "effort_minutes": {"type": "integer", "minimum": 1},
                        "optimistic_minutes": {"type": "integer", "minimum": 1},
                        "most_likely_minutes": {"type": "integer", "minimum": 1},
                        "pessimistic_minutes": {"type": "integer", "minimum": 1},
                        "external_constraints": {"type": "string"},
                        "required_resources": {"type": "array", "items": {"type": "string"}},
                        "required_people": {"type": "array", "items": {"type": "string"}},
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "depends_on_ids": {"type": "array", "items": {"type": "integer", "minimum": 1}},
                    },
                    "required": ["task_id"],
                },
            },
        }
    )

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": "List tasks.",
                "parameters": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "status": {"type": "string", "description": "Optional status filter."},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 500},
                    },
                },
            },
        }
    )

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "prioritize_tasks",
                "description": "Compute a prioritized ordering and completion chances for tasks.",
                "parameters": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "task_ids": {"type": "array", "items": {"type": "integer", "minimum": 1}},
                        "as_of": {"type": "string", "description": "ISO 8601 datetime; defaults to now."},
                    },
                },
            },
        }
    )

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "estimate_completion",
                "description": "Estimate chance of completion for a single task.",
                "parameters": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "task_id": {"type": "integer", "minimum": 1},
                        "as_of": {"type": "string", "description": "ISO 8601 datetime; defaults to now."},
                    },
                    "required": ["task_id"],
                },
            },
        }
    )

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "review_day",
                "description": "Upsert a daily score (planned vs completed).",
                "parameters": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "day": {"type": "string", "description": "YYYY-MM-DD; defaults to today."},
                        "planned_points": {"type": "number", "minimum": 0},
                        "completed_points": {"type": "number", "minimum": 0},
                        "notes": {"type": "string"},
                    },
                },
            },
        }
    )

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "calendar_read",
                "description": "Read calendar busy blocks between time_min and time_max.",
                "parameters": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "time_min": {"type": "string", "description": "ISO 8601 datetime"},
                        "time_max": {"type": "string", "description": "ISO 8601 datetime"},
                        "calendar_id": {"type": "string", "description": "Defaults to primary."},
                    },
                    "required": ["time_min", "time_max"],
                },
            },
        }
    )

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "calendar_move",
                "description": "Move a calendar event to a new start/end time (requires user confirmation).",
                "parameters": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "event_id": {"type": "string"},
                        "new_start": {"type": "string", "description": "ISO 8601 datetime"},
                        "new_end": {"type": "string", "description": "ISO 8601 datetime"},
                        "calendar_id": {"type": "string"},
                    },
                    "required": ["event_id", "new_start", "new_end"],
                },
            },
        }
    )

    return tools

