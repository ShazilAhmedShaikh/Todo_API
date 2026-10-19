from fastapi import FastAPI, HTTPException

app = FastAPI()

# In-memory list (Stage 2)
tasks = [
    {"id": 1, "title": "Learn FastAPI", "done": False},
    {"id": 2, "title": "Build CRUD API", "done": False},
    {"id": 3, "title": "Push to GitHub", "done": False}
]

@app.get("/")
def read_root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
def health_check():
    return {"status": "ok"}

# GET all tasks
@app.get("/tasks")
def get_tasks():
    return tasks

# GET a single task by ID
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    # Agar task na mile toh 404 error return karein
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")