from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import sqlite3

app = FastAPI()

# Stage 0: Database Setup
def init_db():
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    
    # Create table if it does not exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0
        )
    ''')
    
    # Check if the table is empty
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]
    
    # Seed 3 example tasks only if the table is empty
    if count == 0:
        examples = [
            ("Learn FastAPI", 0),
            ("Build CRUD API", 0),
            ("Push to GitHub", 0)
        ]
        cursor.executemany("INSERT INTO tasks (title, done) VALUES (?, ?)", examples)
        conn.commit()
        
    conn.close()

# Run database setup when the application starts
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
    return {"status": "ok"}

# Database connection ke liye helper function
def get_db_connection():
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row # Is se row ka data dictionary ki tarah access ho sakta hai
    return conn

@app.get("/tasks")
def get_tasks():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    
    # SQLite rows ko dictionary mein convert karke return karna
    tasks_list = []
    for row in rows:
        tasks_list.append({
            "id": row["id"],
            "title": row["title"],
            "done": bool(row["done"]) # 0 ya 1 ko False ya True mein badalna
        })
    return tasks_list

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Parameterized query (?) id fetch karne ke liye
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")
        
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"])
    }