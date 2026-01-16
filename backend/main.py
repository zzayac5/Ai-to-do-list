# backend/main.py
from fastapi import FastAPI, HTTPException
from schemas import ChatRequest, ChatResponse, TaskInput
from task_formats import ToDoTask

app = FastAPI()

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    For now, assume the LLM already returned structured JSON
    and we are focusing on pipeline correctness.
    """

    tasks = []
    for task_input in request.tasks:
        try:
            task = ToDoTask(task_input)
            tasks.append(task.summary())
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    return ChatResponse(
        reply="Tasks processed successfully.",
        tasks=request.tasks
    )
