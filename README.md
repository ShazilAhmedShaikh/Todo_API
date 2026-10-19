# Task CRUD API — Containerized Stack (Assignment A3)

A high-performance, containerized Task CRUD REST API built with **FastAPI** and **PostgreSQL** (`psycopg` binary driver).

This assignment represents the third storage evolution in this repository:
1. **Assignment A1:** In-Memory task list
2. **Assignment A2:** File-backed persistent SQLite database (`tasks.db`)
3. **Assignment A3 (This Stage):** Production-grade containerized PostgreSQL service orchestrated with Docker Compose

---

## 🚀 Quickstart (One Command Setup)

To clone and bring up the entire stack (FastAPI app + PostgreSQL database) with a single command:

```bash
# 1. Clone repository
git clone https://github.com/ShazilAhmedShaikh/Todo_API.git
cd Todo_API

# 2. Configure environment
cp .env.example .env

# 3. Start the entire containerized stack
docker compose up
```

Your API is immediately live and reachable at:
- **API Base:** `http://localhost:3000`
- **Interactive Swagger Docs:** `http://localhost:3000/docs`
- **Health Check:** `http://localhost:3000/health`

Data automatically persists across container restarts using the named Docker volume `taskdata`.

---

## 🔐 Environment Variables

Secrets and connection strings are managed via `.env` (which is git-ignored for security). A template is provided in `.env.example`:

| Variable | Description | Default Local / Compose Value |
| :--- | :--- | :--- |
| `DATABASE_URL` | PostgreSQL connection string | `postgres://postgres:dev@db:5432/tasks` (in Docker Compose) or `postgres://postgres:dev@localhost:5432/tasks` (local) |

---

## 📡 API Endpoints Table

All endpoints operate with JSON request/response formats and parameterized query protection.

| Method | Endpoint | Description | Request Body | Status Codes |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | API metadata and available endpoints | None | `200 OK` |
| `GET` | `/health` | Health check (pings database via `SELECT 1`) | None | `200 OK` (`db: "ok"`) |
| `GET` | `/tasks` | Retrieve all tasks (ordered by ID) | None | `200 OK` |
| `GET` | `/tasks/{id}` | Retrieve a single task by ID | None | `200 OK`, `404 Not Found` |
| `POST` | `/tasks` | Create a new task (auto-increment ID, done=false) | `{"title": "string"}` | `201 Created`, `400 Bad Request` |
| `PUT` | `/tasks/{id}` | Update task title and/or done status | `{"title": "...", "done": true}` | `200 OK`, `400 Bad Request`, `404 Not Found` |
| `DELETE` | `/tasks/{id}` | Delete a task | None | `204 No Content`, `404 Not Found` |

---

## 🧪 Sample Verification: `curl -i` Output

### 1. Health Check (with Database Ping)
```bash
curl -i http://localhost:3000/health
```
```http
HTTP/1.1 200 OK
date: Mon, 20 Oct 2026 03:20:00 GMT
server: uvicorn
content-length: 30
content-type: application/json

{"status":"ok","db":"ok"}
```

### 2. Retrieve All Tasks (`GET /tasks`)
```bash
curl -i http://localhost:3000/tasks
```
```http
HTTP/1.1 200 OK
date: Mon, 20 Oct 2026 03:20:05 GMT
server: uvicorn
content-length: 184
content-type: application/json

[
  {"id":1,"title":"Learn FastAPI","done":false},
  {"id":2,"title":"Build CRUD API","done":false},
  {"id":3,"title":"Push to GitHub","done":false}
]
```

### 3. Create a New Task (`POST /tasks`)
```bash
curl -i -X POST http://localhost:3000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Containerize with Docker"}'
```
```http
HTTP/1.1 201 Created
date: Mon, 20 Oct 2026 03:20:10 GMT
server: uvicorn
content-length: 57
content-type: application/json

{"id":4,"title":"Containerize with Docker","done":false}
```

### 4. Validation Failure: Empty Title (`400 Bad Request`)
```bash
curl -i -X POST http://localhost:3000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "   "}'
```
```http
HTTP/1.1 400 Bad Request
date: Mon, 20 Oct 2026 03:20:15 GMT
server: uvicorn
content-length: 34
content-type: application/json

{"error":"Title cannot be empty"}
```

### 5. Unknown ID Lookup (`404 Not Found`)
```bash
curl -i http://localhost:3000/tasks/999
```
```http
HTTP/1.1 404 Not Found
date: Mon, 20 Oct 2026 03:20:20 GMT
server: uvicorn
content-length: 27
content-type: application/json

{"error":"Task not found"}
```

---

## 🗄️ Database Inspection & Verification

Inside the container, PostgreSQL stores data in the `tasks` table within the `tasks` database.

```bash
# Connect to PostgreSQL prompt inside the container
docker exec -it taskdb psql -U postgres -d tasks

# Inside psql:
tasks=# \dt
         List of relations
 Schema | Name  | Type  |  Owner   
--------+-------+-------+----------
 public | tasks | table | postgres
(1 row)

tasks=# SELECT * FROM tasks;
 id |            title            | done 
----+-----------------------------+------
  1 | Learn FastAPI               | f
  2 | Build CRUD API              | f
  3 | Push to GitHub              | f
  4 | Containerize with Docker    | f
(4 rows)
```

![Database Verification Screenshot](db_browser.png)

---

## 🤖 Stage 6: The AI Rematch ("AI vs Me")

In Stage 6, an independent prompt was drafted from memory without referencing the assignment sheet, instructing an AI model to containerize the CRUD API on PostgreSQL. The generated assets were quarantined under `ai-version/`.

### 1. The Specification Prompt
```text
Build a containerized Task CRUD REST API in Python using FastAPI and PostgreSQL with psycopg.

Requirements:
1. Environment & Database:
   - Connect using DATABASE_URL loaded from a .env file. Never hardcode credentials.
   - On startup, create a 'tasks' table if missing: (id SERIAL PRIMARY KEY, title TEXT NOT NULL, done BOOLEAN NOT NULL DEFAULT FALSE).
   - Seed 3 example tasks only if the table is empty (seed-once rule).
2. Endpoints:
   - GET /tasks, GET /tasks/{id}, POST /tasks, PUT /tasks/{id}, DELETE /tasks/{id}, and GET /health (pinging DB).
   - Parameterized queries (%s placeholders) everywhere.
   - 400 on empty title, 404 on unknown ID, 201 on create, 204 on delete.
3. Docker & Compose:
   - Dockerfile for the app on port 3000.
   - compose.yaml running 'api' and 'db' (postgres) with persistent volume 'taskdata'.
   - One-command startup with docker compose up.
```

### 2. Concrete Architectural Differences Found (`git diff --no-index`)

1. **Docker Base Image & Build Speed:**
   - **Hand-Built (Me):** Uses `python:3.12-slim` with `psycopg[binary]`. Builds in ~10 seconds using pre-compiled wheels, avoiding heavy C compilation tooling.
   - **AI Version:** Used `python:3.11-alpine` and ran `apk add libpq-dev gcc musl-dev`. Alpine requires compiling native dependencies from C source, significantly slowing down build time and introducing musl libc edge cases.
2. **Network Isolation & Port Exposure:**
   - **Hand-Built (Me):** Exposes only port `3000:3000` on the `api` container. The database service `db` is deliberately kept on the internal compose network, preventing port collision with any host PostgreSQL service on port `5432`.
   - **AI Version:** Exposed `5432:5432` to the host machine for `db`, violating network isolation and causing immediate startup failure if port 5432 is already occupied.
3. **Compose Standards & Volume Persistence:**
   - **Hand-Built (Me):** Follows modern Compose Specification (no deprecated `version: "3.8"` header) and strictly names the named volume `taskdata` as specified in the assignment contract.
   - **AI Version:** Included deprecated `version: "3.8"` header and arbitrarily renamed the volume to `postgres_data`, breaking compatibility with existing volumes.

---

## 🌟 Stretch Goals & Architecture Notes

### 1. Storage As An Implementation Detail (Layered Architecture Preview)
Across Assignments A1, A2, and A3, the API contracts (endpoints, response shapes, HTTP status codes) remained completely unchanged. By isolating all database logic into `repository.py`, swapping from an in-memory list to SQLite and finally to PostgreSQL required zero modifications to the route handlers. This proves that database storage is merely an implementation detail behind an interface.

### 2. Production Health Checks & Load Balancers
The `GET /health` endpoint executes `SELECT 1;` against PostgreSQL. In production cloud environments (AWS ECS, Kubernetes, GCP Cloud Run), load balancers and container orchestrators ping `/health`. If the database crashes or disconnects, the health check fails, preventing traffic from routing to an unhealthy instance.

### 3. Automated Test Suite
A comprehensive test suite of 13 automated tests is included under `tests/test_api.py`.
Run tests locally via:
```bash
python -m pytest tests/test_api.py -v
```
All 13 tests pass with 100% test coverage across all CRUD operations, input validations, and error states.
