import os
import json 
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel
import sqlite3
from fastapi.middleware.cors import CORSMiddleware

from openai import OpenAI
from schemas import ChatRequest, ChatResponse, Task 


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Define your task model
class Task(BaseModel):
    description: str
    priority: int
    importance: str
    duration: int
    confidence: int
    due_date: str

# Example route to add a task
@app.post("/add_task")
def add_task(task: Task):
    # Here you would insert the task into SQLite
    # For example, open a connection, insert the task, and close the connection
    return {"message": "Task added successfully"}

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are an executive assistant that helps prioritize tasks based on the Eisenhower Matrix but always outputs strict JSON objects.

Users will talk about what they need to get done (tasks, projects, errands, goals, deadlines, etc).

Your Job: 

1. Respond with a naturals language reply summarizing what you understand the user wants to accomplish.
2. Extract tasks and represent them as JSON objects with the following schema without any deviation:

{
    "reply" : "<natural language reply summarizing what you understand the user wants to accomplish>",
    "tasks": [
        {
            "description": "<short description of the task>",
            "date": "<due date in YYYY-MM-DD format or null if not specified>",
            "time": "HH:MM format or null if not specified",
            "duration": <estimated duration in minutes or null if not specified>,
            "priority": <"High" | "Medium" | "Low" | "None", or null if not specified>,
            "importance": <"Urgent and Important" | "Not Urgent but Important" | "Urgent but Not Important" | "Not Urgent and Not Important", or null if not specified>,
            "confidence": <integer from 1 to 10 indicating confidence in the task details, or null if not specified>
            "additional_details": "<any additional details or context about the task>"
            "anyone_needed": "<list of people needed for the task or null if not specified>"
        }
    ]
}
Rules: 
- If the user does not provide enough information about a task, fill the missing fields with null DO NOT GUESS. You will have an opportunity to ask follow-up questions later.
- You MAY infer rough priority and importance based on context, but if unsure (confidence in task details falls below 80 percent as you assess them), set to null.
- if the user mentions "tomorrow", "next week", "in 3 days", etc, convert to exact date based on current date.
-ALWAYS respond with valid JSON. DO NOT RESPOND WITH PLAIN TEXT.

"""
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        data = json.loads(raw_content)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail=f"Model returned invalid JSON: {raw_content[:200]}",
        )
    
    reply = data.get("reply", "")
    tasks_data = data.get("tasks", [])
    tasks = [
        Task(
                description=t.get("description", ""),
                priority=t.get("priority"),
                importance=t.get("importance"),
                duration=t.get("duration"),
                confidence=t.get("confidence"),
                due_date=t.get("date", "")
        )
        for t in tasks_data
    ]
    return ChatResponse(reply=reply, tasks=tasks)
