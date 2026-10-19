# AI Prompt Specification: Containerized Task CRUD API

```text
Build a containerized Task CRUD REST API in Python using FastAPI and PostgreSQL with psycopg.

Requirements:
1. Environment & Database:
   - Connect using DATABASE_URL loaded from a .env file (e.g. postgres://postgres:dev@db:5432/tasks). Never hardcode credentials.
   - On application startup, automatically create a 'tasks' table if it doesn't exist with columns:
     - id: SERIAL PRIMARY KEY
     - title: TEXT NOT NULL
     - done: BOOLEAN NOT NULL DEFAULT FALSE
   - Seed 3 example tasks ("Learn FastAPI", "Build CRUD API", "Push to GitHub") ONLY if the table is empty (seed-once rule).

2. Endpoints:
   - GET /tasks -> return all tasks (200 OK)
   - GET /tasks/{id} -> return single task by ID (200 OK) or 404 {"error": "Task not found"}
   - POST /tasks -> create task with title (201 Created), validate non-empty title (400 Bad Request)
   - PUT /tasks/{id} -> update task title/done (200 OK), validate non-empty title (400), or 404 if not found
   - DELETE /tasks/{id} -> delete task (204 No Content), or 404 if not found
   - GET /health -> return {"status": "ok", "db": "ok"} by executing SELECT 1
   - All SQL queries must strictly use parameterized queries (%s placeholders).

3. Containerization & Compose:
   - Provide a Dockerfile exposing port 3000 running uvicorn.
   - Provide a compose.yaml orchestrating two services:
     - 'api' built from Dockerfile, mapped port 3000:3000.
     - 'db' running the official postgres image with POSTGRES_PASSWORD=dev and POSTGRES_DB=tasks.
     - A persistent named volume 'taskdata' mapped to Postgres data directory so data survives container restarts.
   - Entire stack must start with one command: docker compose up.
```
