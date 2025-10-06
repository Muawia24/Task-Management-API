import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta


class TestTasks:
    """Basic tests for task creation, retrieval, update, and deletion."""

    def test_create_task(self, client: TestClient):
        data = {"title": "Test Task"}
        response = client.post("/tasks/", json=data)
        assert response.status_code == 201
        result = response.json()
        assert result["title"] == "Test Task"
        assert result["status"] == "pending"

    def test_create_task_with_due_date(self, client: TestClient):
        due_date = (datetime.utcnow() + timedelta(days=3)).isoformat()
        data = {"title": "Task with Date", "due_date": due_date}
        response = client.post("/tasks/", json=data)
        assert response.status_code == 201
        response_date = response.json()["due_date"].replace("+00:00", "")
        assert response_date == due_date

    def test_create_task_invalid_data(self, client: TestClient):
        # Empty title
        response = client.post("/tasks/", json={"title": "  "})
        assert response.status_code == 422

    def test_get_tasks(self, client: TestClient):
        client.post("/tasks/", json={"title": "One"})
        client.post("/tasks/", json={"title": "Two"})
        response = client.get("/tasks?skip=0&limit=2")
        assert response.status_code == 200
        print(response.json())
        assert len(response.json()) >= 2

    def test_get_task_by_id(self, client: TestClient):
        create = client.post("/tasks/", json={"title": "Check by ID"})
        task_id = create.json()["id"]
        response = client.get(f"/tasks/{task_id}")
        assert response.status_code == 200
        assert response.json()["id"] == task_id

    def test_update_task(self, client: TestClient):
        task = client.post("/tasks/", json={"title": "Update Me"}).json()
        updated = client.put(f"/tasks/{task['id']}", json={"status": "completed"})
        assert updated.status_code == 200
        assert updated.json()["status"] == "completed"

    def test_delete_task(self, client: TestClient):
        task = client.post("/tasks/", json={"title": "Delete Me"}).json()
        delete = client.delete(f"/tasks/{task['id']}")
        assert delete.status_code == 204
        # Make sure it's really deleted
        check = client.get(f"/tasks/{task['id']}")
        assert check.status_code == 404

    def test_filter_tasks_by_priority_and_status(self, client: TestClient):
        client.post("/tasks/", json={"title": "High Priority", "priority": "high"})
        client.post("/tasks/", json={"title": "Low Priority", "priority": "low"})
        filtered_result = client.get("/tasks?priority=high&status=pending")
        print(filtered_result.json())
        assert filtered_result.status_code == 200
        for task in filtered_result.json():
            assert task["priority"] == "high"
            assert task["status"] == "pending"
