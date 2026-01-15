import os
import json 
import sqlite3

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from typing import List, Dict
from pydantic import BaseModel


from dotenv import load_dotenv

from openai import OpenAI

from .schemas import ChatRequest, ChatResponse, Task, Message

from datetime import date

from .prompt_parts import build_system_prompt



TODAY = date.today().isoformat()

load_dotenv() 

SYSTEM_PROMPT: str = build_system_prompt(TODAY)
CONVERSATIONS: Dict[str, List[dict[str, str]]] = {}

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/add_task")
def add_task(task: Task):

    return {"message": "Task added successfully"}

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # Build messages array with system + history + latest user message
    session_id = request.session_id or "default"
    stored_history = CONVERSATIONS.get(session_id, [])
    request_history = (
        [{"role": m.role, "content": m.content} for m in request.history]
        if request.history
        else stored_history
    )

    chat_messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    chat_messages.extend(request_history)

    chat_messages.append({"role": "user", "content": request.message})

    try:
        completion = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=chat_messages,   # <-- use history-aware messages
            temperature=0,
        )

        raw_content = completion.choices[0].message.content

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"OpenAI API error: {e}",
        )

    try:
        data = json.loads(raw_content)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail=f"Model returned invalid JSON: {raw_content[:200]}",
        )

    tasks_data = data.get("tasks", []) or []
    tasks = []

    for t in tasks_data:
        task = Task(
            description=t.get("description", "") or "",
            date=t.get("date"),
            time=t.get("time"),
            duration_optimistic=t.get("optimistic duration"),
            duration_most_likely=t.get("most likely duration"),
            duration_pessimist=t.get("pessimistic duration"),            
            priority=t.get("priority"),
            importance=t.get("importance"),
            confidence=t.get("confidence"),
            additional_details=t.get("additional_details"),
            anyone_needed=t.get("anyone_needed"),
        )
        tasks.append(task)


  #      due_date_flexible: bool = True,
  #      required_resources: Optional[List[str]] = None,
  #      required_people: Optional[List[str]] = None,
  #      dependencies: Optional[List["ToDoTask"]] = None,
  #      recurring: bool = False
   # ):

    reply = data.get("reply", "") or ""
    # Persist conversation so follow-ups have context
    conversation_history = list(request_history)
    conversation_history.append({"role": "user", "content": request.message})
    conversation_history.append({"role": "assistant", "content": raw_content})
    CONVERSATIONS[session_id] = conversation_history
    return ChatResponse(reply=reply, tasks=tasks)
