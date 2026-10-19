import os
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:dev@localhost:5432/tasks")

# Normalize URL scheme if postgres:// is provided (standard SQLAlchemy/psycopg convention)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def get_connection():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)

def init_db():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            # Create tasks table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    done BOOLEAN NOT NULL DEFAULT FALSE
                );
            """)

            # Check if table is empty
            cursor.execute("SELECT COUNT(*) AS count FROM tasks;")
            result = cursor.fetchone()
            count = result["count"] if result else 0

            # Seed 3 example tasks only if the table is empty (seed-once rule)
            if count == 0:
                examples = [
                    ("Learn FastAPI", False),
                    ("Build CRUD API", False),
                    ("Push to GitHub", False)
                ]
                cursor.executemany(
                    "INSERT INTO tasks (title, done) VALUES (%s, %s);",
                    examples
                )
        conn.commit()

def get_all_tasks() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, title, done FROM tasks ORDER BY id ASC;")
            return cursor.fetchall()

def get_task_by_id(task_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, title, done FROM tasks WHERE id = %s;", (task_id,))
            return cursor.fetchone()

def create_task(title: str, done: bool = False) -> Dict[str, Any]:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id, title, done;",
                (title, done)
            )
            created = cursor.fetchone()
        conn.commit()
        return created

def update_task(task_id: int, title: Optional[str] = None, done: Optional[bool] = None) -> Optional[Dict[str, Any]]:
    existing = get_task_by_id(task_id)
    if existing is None:
        return None
    new_title = title if title is not None else existing["title"]
    new_done = done if done is not None else existing["done"]
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING id, title, done;",
                (new_title, new_done, task_id)
            )
            updated = cursor.fetchone()
        conn.commit()
        return updated

def delete_task(task_id: int) -> bool:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM tasks WHERE id = %s RETURNING id;", (task_id,))
            deleted = cursor.fetchone()
        conn.commit()
        return deleted is not None

def ping_db() -> bool:
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1;")
                return True
    except Exception:
        return False
