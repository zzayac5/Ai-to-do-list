# backend/schemas.py
from pydantic import BaseModel
from typing import List, Optional, Union 


class ChatRequest(BaseModel):
    message: str


class Task(BaseModel):
    # Required
    description: str

    # Optional fields, all default to None
    date: Optional[str] = None             # "2025-12-01" or None
    time: Optional[str] = None             # "14:30" or None
    duration: Optional[int] = None         # minutes or None
    priority: Optional[Union[str, int]] = None         # "High" | "Medium" | "Low" | "None"
    importance: Optional[str] = None       # Eisenhower quadrant or None
    confidence: Optional[int] = None       # 1–10 or None
    additional_details: Optional[str] = None
    anyone_needed: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    tasks: List[Task]
