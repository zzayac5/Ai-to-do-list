from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    history: list[Message] | None = None
    session_id: str | None = "default"
    user_id: int | None = None


class ToolResult(BaseModel):
    name: str
    ok: bool = True
    result: dict[str, Any] | list[Any] | str | None = None
    error: str | None = None


class ChatResponse(BaseModel):
    reply: str
    tool_results: list[ToolResult] = []


class TaskBase(BaseModel):
    title: str = Field(default="", max_length=200)
    description: str | None = None
    status: str = "inbox"

    due_at: datetime | None = None

    urgency: int | None = Field(default=None, ge=0, le=10)
    importance: int | None = Field(default=None, ge=0, le=10)
    impact: int | None = Field(default=None, ge=0, le=10)

    effort_minutes: int | None = Field(default=None, gt=0)
    optimistic_minutes: int | None = Field(default=None, gt=0)
    most_likely_minutes: int | None = Field(default=None, gt=0)
    pessimistic_minutes: int | None = Field(default=None, gt=0)

    external_constraints: str | None = None
    required_resources: list[str] = []
    required_people: list[str] = []
    tags: list[str] = []
    depends_on_ids: list[int] = []


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    description: str | None = None
    status: str | None = None

    due_at: datetime | None = None

    urgency: int | None = Field(default=None, ge=0, le=10)
    importance: int | None = Field(default=None, ge=0, le=10)
    impact: int | None = Field(default=None, ge=0, le=10)

    effort_minutes: int | None = Field(default=None, gt=0)
    optimistic_minutes: int | None = Field(default=None, gt=0)
    most_likely_minutes: int | None = Field(default=None, gt=0)
    pessimistic_minutes: int | None = Field(default=None, gt=0)

    external_constraints: str | None = None
    required_resources: list[str] | None = None
    required_people: list[str] | None = None
    tags: list[str] | None = None
    depends_on_ids: list[int] | None = None


class TaskRead(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None


class PrioritizeRequest(BaseModel):
    task_ids: list[int] | None = None
    as_of: datetime | None = None


class PrioritizedTask(BaseModel):
    task_id: int
    priority_score: float
    completion_chance: float | None = None
    rationale: str | None = None


class PrioritizeResponse(BaseModel):
    as_of: datetime
    results: list[PrioritizedTask]


class ReviewDayRequest(BaseModel):
    day: date | None = None
    planned_points: float | None = None
    completed_points: float | None = None
    notes: str | None = None


class ReviewDayResponse(BaseModel):
    day: date
    planned_points: float
    completed_points: float
    score: float
    notes: str | None = None

