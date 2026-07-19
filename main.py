import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List

from repositories.in_memory_repository import InMemoryTaskRepository
from repositories.postgres_repository import PostgresTaskRepository

load_dotenv()

app = FastAPI(title="CRUD API", version="1.0")

# --- Repository selection ---
# Uses Postgres if DATABASE_URL is set (e.g. via docker-compose / .env),
# otherwise falls back to the original in-memory store for local dev.
if os.environ.get("DATABASE_URL"):
    repo = PostgresTaskRepository()
else:
    repo = InMemoryTaskRepository()


# --- Schemas ---
class Task(BaseModel):
    task: str = Field(..., example="Write unit tests")
    status: bool = Field(default=False, example=False)

class TaskUpdate(BaseModel):
    task: Optional[str] = None
    status: Optional[bool] = None


# --- Routes ---
@app.get("/", summary="API metadata")
def get_metadata():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/tasks", response_model=List[dict], summary="List all tasks")
def get_tasks():
    return repo.list_all()


@app.get("/tasks/{task_id}", summary="Get a single task by ID")
def get_task(task_id: int):
    task = repo.get(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@app.post("/tasks", status_code=status.HTTP_201_CREATED, summary="Create a new task")
def create_task(task: Task):
    return repo.create(task.task, task.status)


@app.put("/tasks/{task_id}", summary="Update an existing task")
def update_task(task_id: int, update: TaskUpdate):
    task = repo.update(task_id, task=update.task, status=update.status)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@app.delete("/tasks/{task_id}", summary="Delete a task")
def delete_task(task_id: int):
    deleted = repo.delete(task_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return {"message": f"Task {task_id} deleted successfully"}
