from typing import Optional
from fastapi import FastAPI, HTTPException, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from repository import (
    init_db,
    get_all_tasks,
    get_task_by_id,
    create_task,
    update_task,
    delete_task,
    ping_db
)

app = FastAPI()

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "detail": exc.detail}
    )

# Run database setup when application starts
init_db()

# Pydantic models for incoming data validation
class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

@app.get("/")
def read_root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
def health_check():
    db_ok = ping_db()
    return {"status": "ok", "db": "ok" if db_ok else "unavailable"}

# Stage 2: Read from Postgres
@app.get("/tasks")
def get_tasks():
    return get_all_tasks()

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# Stage 3: Create, update, delete on Postgres
@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_new_task(task: TaskCreate):
    if not task.title or not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    return create_task(title=task.title.strip())

@app.put("/tasks/{task_id}")
def update_existing_task(task_id: int, task_update: TaskUpdate):
    if task_update.title is not None and not task_update.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    
    clean_title = task_update.title.strip() if task_update.title is not None else None
    updated = update_task(task_id, title=clean_title, done=task_update.done)
    if updated is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_task(task_id: int):
    deleted = delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)