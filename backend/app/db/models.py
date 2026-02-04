from __future__ import annotations

import enum
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from backend.app.db.base import Base


class TaskStatus(str, enum.Enum):
    inbox = "inbox"
    planned = "planned"
    in_progress = "in_progress"
    done = "done"
    canceled = "canceled"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    phone_number: Mapped[str | None] = mapped_column(String(32), unique=True, nullable=True)
    email: Mapped[str | None] = mapped_column(String(320), unique=True, nullable=True)
    timezone: Mapped[str] = mapped_column(String(64), default="UTC")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    tasks: Mapped[list["Task"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    sessions: Mapped[list["ConversationSession"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    day_scores: Mapped[list["DayScore"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class TaskDependency(Base):
    __tablename__ = "task_dependencies"

    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True)
    depends_on_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True)


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    title: Mapped[str] = mapped_column(String(200), default="", nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default=TaskStatus.inbox.value, nullable=False)

    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # 0-10 scales (nullable until user/LLM provides)
    urgency: Mapped[int | None] = mapped_column(Integer, nullable=True)
    importance: Mapped[int | None] = mapped_column(Integer, nullable=True)
    impact: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Effort estimates in minutes
    effort_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    optimistic_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    most_likely_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pessimistic_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    external_constraints: Mapped[str | None] = mapped_column(Text, nullable=True)

    required_resources: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    required_people: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[User | None] = relationship(back_populates="tasks")

    depends_on: Mapped[list["Task"]] = relationship(
        "Task",
        secondary="task_dependencies",
        primaryjoin=(id == TaskDependency.task_id),
        secondaryjoin=(id == TaskDependency.depends_on_id),
        viewonly=True,
        lazy="selectin",
    )


class ConversationSession(Base):
    __tablename__ = "sessions"

    # Client chooses the id (uuid recommended). Using string keeps it simple across channels (SMS/voice/web).
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Lightweight persistence; keep transcripts summarized in production to control size.
    transcript: Mapped[list[dict]] = mapped_column(JSON, default=list, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    llm_plan_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    user: Mapped[User | None] = relationship(back_populates="sessions")


class DayScore(Base):
    __tablename__ = "day_scores"
    __table_args__ = (UniqueConstraint("user_id", "day", name="uq_day_scores_user_day"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    day: Mapped[date] = mapped_column(Date, nullable=False)

    planned_points: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    completed_points: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user: Mapped[User | None] = relationship(back_populates="day_scores")


class CalendarEventCache(Base):
    __tablename__ = "calendar_event_cache"
    __table_args__ = (UniqueConstraint("user_id", "event_id", name="uq_calendar_event_cache_user_event"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    event_id: Mapped[str] = mapped_column(String(256), nullable=False)

    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    summary: Mapped[str | None] = mapped_column(String(512), nullable=True)
    busy: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    raw: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

