# Task CRUD API (Containerized)

FastAPI Task Management CRUD API backed by a containerized PostgreSQL database.

## Stage 0: Postgres in Docker

Run the standalone PostgreSQL database container:

```bash
docker run --name taskdb -e POSTGRES_PASSWORD=dev -e POSTGRES_DB=tasks \
  -p 5432:5432 -v taskdata:/var/lib/postgresql/data -d postgres
```

Verify the container is running and open a SQL prompt:

```bash
docker ps
docker exec -it taskdb psql -U postgres -d tasks
```
Inside `psql`:
- `\dt` (lists tables)
- `\q` (exits psql)
