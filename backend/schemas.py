# backend/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, time

class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Message]] = None
    session_id: Optional[str] = "default"


class TaskInput(BaseModel):
    description: str

    date_of_task: Optional[date] = None
    time_of_task: Optional[time] = None

    optimistic_minutes: Optional[int] = Field(None, gt=0)
    most_likely_minutes: Optional[int] = Field(None, gt=0)
    pessimistic_minutes: Optional[int] = Field(None, gt=0)

    importance: Optional[str] = None
    note: Optional[str] = None

    due_date_flexible: bool = True
    required_resources: List[str] = []
    required_people: List[str] = []
    dependencies: List[str] = []
    recurring: bool = False


class ChatResponse(BaseModel):
    reply: str
    tasks: List[TaskInput]
