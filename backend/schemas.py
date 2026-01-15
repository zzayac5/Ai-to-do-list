# backend/schemas.py
from pydantic import BaseModel
from typing import List, Optional, Union, Literal

class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    
class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Message]] = None
    session_id: Optional[str] = "default"

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


#        date_of_task: dgiate,
#        time_of_task: time,
#        description: str,

#        optimistic_minutes: int,
#        most_likely_minutes: int,
#        pessimistic_minutes: int,

#        importance: str,
#        note: str,

#        due_date_flexible: bool = True,
#        required_resources: Optional[List[str]] = None,
#        required_people: Optional[List[str]] = None,
#        dependencies: Optional[List["ToDoTask"]] = None,
#        recurring: bool = False