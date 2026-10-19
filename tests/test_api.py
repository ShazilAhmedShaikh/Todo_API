import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app

client = TestClient(app)

# 1. Health check test
def test_health_check_endpoint():
    with patch("main.ping_db", return_value=True):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["db"] == "ok"

# 2. Root endpoint test
def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Task API"
    assert "/tasks" in data["endpoints"]

# 3. GET /tasks (Success - 200)
def test_get_tasks():
    mock_tasks = [
        {"id": 1, "title": "Learn FastAPI", "done": False},
        {"id": 2, "title": "Build CRUD API", "done": False},
        {"id": 3, "title": "Push to GitHub", "done": False}
    ]
    with patch("main.get_all_tasks", return_value=mock_tasks):
        response = client.get("/tasks")
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 3
        assert tasks[0]["title"] == "Learn FastAPI"
        assert tasks[0]["done"] is False

# 4. GET /tasks/{id} (Success - 200)
def test_get_task_by_id_success():
    mock_task = {"id": 1, "title": "Learn FastAPI", "done": False}
    with patch("main.get_task_by_id", return_value=mock_task):
        response = client.get("/tasks/1")
        assert response.status_code == 200
        assert response.json() == mock_task

# 5. GET /tasks/{id} (Not Found - 404)
def test_get_task_by_id_not_found():
    with patch("main.get_task_by_id", return_value=None):
        response = client.get("/tasks/999")
        assert response.status_code == 404
        data = response.json()
        assert "error" in data or "detail" in data
        assert data.get("error") == "Task not found" or data.get("detail") == "Task not found"

# 6. POST /tasks (Success - 201)
def test_create_task_success():
    created_task = {"id": 4, "title": "Deploy to Docker", "done": False}
    with patch("main.create_task", return_value=created_task):
        response = client.post("/tasks", json={"title": "Deploy to Docker"})
        assert response.status_code == 201
        assert response.json() == created_task

# 7. POST /tasks (Validation failure - Empty title - 400)
def test_create_task_empty_title():
    response = client.post("/tasks", json={"title": "   "})
    assert response.status_code == 400
    data = response.json()
    assert "error" in data or "detail" in data

# 8. POST /tasks (Validation failure - Missing title - 422/400)
def test_create_task_missing_body():
    response = client.post("/tasks", json={})
    assert response.status_code in [400, 422]

# 9. PUT /tasks/{id} (Success - 200)
def test_update_task_success():
    updated_task = {"id": 1, "title": "Learn FastAPI Advanced", "done": True}
    with patch("main.update_task", return_value=updated_task):
        response = client.put("/tasks/1", json={"title": "Learn FastAPI Advanced", "done": True})
        assert response.status_code == 200
        assert response.json() == updated_task

# 10. PUT /tasks/{id} (Validation failure - Empty title - 400)
def test_update_task_empty_title():
    response = client.put("/tasks/1", json={"title": "  "})
    assert response.status_code == 400

# 11. PUT /tasks/{id} (Not Found - 404)
def test_update_task_not_found():
    with patch("main.update_task", return_value=None):
        response = client.put("/tasks/999", json={"title": "Non-existent", "done": True})
        assert response.status_code == 404
        data = response.json()
        assert "error" in data or "detail" in data

# 12. DELETE /tasks/{id} (Success - 204 No Content)
def test_delete_task_success():
    with patch("main.delete_task", return_value=True):
        response = client.delete("/tasks/1")
        assert response.status_code == 204
        assert response.text == ""

# 13. DELETE /tasks/{id} (Not Found - 404)
def test_delete_task_not_found():
    with patch("main.delete_task", return_value=False):
        response = client.delete("/tasks/999")
        assert response.status_code == 404
        data = response.json()
        assert "error" in data or "detail" in data
