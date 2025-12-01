import os
import json 
import sqlite3

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from typing import List
from pydantic import BaseModel


from dotenv import load_dotenv
from openai import OpenAI
from .schemas import ChatRequest, ChatResponse, Task
from datetime import date
from .prompt_parts import build_system_prompt



TODAY = date.today().isoformat()

load_dotenv() 

SYSTEM_PROMPT: str = build_system_prompt(TODAY)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# route to add a task
@app.post("/add_task")
def add_task(task: Task):

    return {"message": "Task added successfully"}

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # 1. Call OpenAI with the system prompt + user message
    try:
        completion = client.chat.completions.create(
            model="gpt-4.1-mini",  # or any other model you prefer
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": request.message},
            ],
            temperature=0,
        )

        # 2. Extract the model's reply text
        raw_content = completion.choices[0].message.content

    except Exception as e:
        # If the OpenAI call fails for any reason
        raise HTTPException(
            status_code=500,
            detail=f"OpenAI API error: {e}",
        )

    # 3. Parse the JSON the model returned
    try:
        data = json.loads(raw_content)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail=f"Model returned invalid JSON: {raw_content[:200]}",
        )

# 4. Map JSON "tasks" into your Pydantic Task models
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