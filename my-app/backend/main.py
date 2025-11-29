from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from fastapi.middleware.cors import CORSMiddleware


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
