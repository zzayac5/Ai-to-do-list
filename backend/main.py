import os
import json 
import sqlite3

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from typing import List
from pydantic import BaseModel


from dotenv import load_dotenv

from openai import OpenAI

from .schemas import ChatRequest, ChatResponse, Task, Message

from datetime import date

from .prompt_parts import build_system_prompt



TODAY = date.today().isoformat()

load_dotenv() 

SYSTEM_PROMPT: str = build_system_prompt(TODAY)

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
    chat_messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    if request.history:
        for m in request.history:
            chat_messages.append({"role": m.role, "content": m.content})

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
            duration=t.get("duration"),
            priority=t.get("priority"),
            importance=t.get("importance"),
            confidence=t.get("confidence"),
            additional_details=t.get("additional_details"),
            anyone_needed=t.get("anyone_needed"),
        )
        tasks.append(task)

    reply = data.get("reply", "") or ""
    return ChatResponse(reply=reply, tasks=tasks)
