# backend/schemas.py
from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    message: str

class Task(BaseModel):
    description: str                    # what to do
    date: Optional[str] = None          # e.g. "2025-11-27"
    time: Optional[str] = None          # e.g. "14:30"
    duration_minutes: Optional[int] = None
    priority: Optional[str] = None      # e.g. "high", "medium", "low"
    context: Optional[str] = None       # optional "why" or extra detail

class ChatResponse(BaseModel):
    reply: str                          # friendly natural-language reply
    tasks: List[Task]                   # structured list for automation
