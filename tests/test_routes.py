import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from app.models.Task import TaskPriority, TaskStatus


def future_time_iso(hours: int = 1) -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()


def create_payload(**overrides):
    data = {
        "title": "Route task",
        "description": "desc",
        "status": TaskStatus.pending.value,
        "priority": TaskPriority.medium.value,
        "due_date": future_time_iso(),
        "assigned_to": "bob",
    }
    data.update(overrides)
    return data


def test_create_task_route_success(client: TestClient):
    res = client.post("/tasks/", json=create_payload())
    assert res.status_code == 201
    body = res.json()
    assert body["id"] > 0
    assert body["title"] == "Route task"


def test_create_task_route_validation_error(client: TestClient):
    bad = create_payload(title="   ")
    res = client.post("/tasks/", json=bad)
    assert res.status_code == 400 or res.status_code == 422


def test_list_tasks_with_pagination_and_filters(client: TestClient):
    # seed
    client.post("/tasks/", json=create_payload(title="t1", priority=TaskPriority.low.value))
    client.post("/tasks/", json=create_payload(title="t2", priority=TaskPriority.high.value))
    client.post("/tasks/", json=create_payload(title="t3", status=TaskStatus.completed.value))

    res = client.get("/tasks/?skip=0&limit=2")
    assert res.status_code == 200
    assert len(res.json()) == 2

    res2 = client.get(f"/tasks/?priority={TaskPriority.high.value}")
    assert res2.status_code == 200

    res3 = client.get(f"/tasks/?status={TaskStatus.completed.value}")
    assert res3.status_code == 200


def test_get_task_by_id_found_and_404(client: TestClient):
    created = client.post("/tasks/", json=create_payload(title="find-me")).json()
    res = client.get(f"/tasks/{created['id']}")
    assert res.status_code == 200
    assert res.json()["title"] == "find-me"

    res404 = client.get("/tasks/999999")
    assert res404.status_code == 404


def test_update_task_success_and_404(client: TestClient):
    created = client.post("/tasks/", json=create_payload()).json()
    res = client.put(f"/tasks/{created['id']}", json={"title": "updated", "status": TaskStatus.in_progress.value})
    assert res.status_code == 200
    body = res.json()
    assert body["title"] == "updated"
    assert body["status"] == TaskStatus.in_progress.value

    res404 = client.put("/tasks/999999", json={"title": "x"})
    assert res404.status_code == 404


def test_delete_task_success_and_404(client: TestClient):
    created = client.post("/tasks/", json=create_payload()).json()
    res = client.delete(f"/tasks/{created['id']}")
    assert res.status_code == 204
    res404 = client.delete(f"/tasks/{created['id']}")
    assert res404.status_code == 404


def test_sort_tasks_valid_and_invalid(client: TestClient):
    # seed
    client.post("/tasks/", json=create_payload(title="a", priority=TaskPriority.low.value))
    client.post("/tasks/", json=create_payload(title="b", priority=TaskPriority.high.value))
    client.post("/tasks/", json=create_payload(title="c", priority=TaskPriority.urgent.value))

    for field in ["title", "created_at", "due_date", "priority", "status"]:
        res = client.get(f"/tasks/sort-by/{field}")
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    res_bad = client.get("/tasks/sort-by/unknown")
    # Router turns exceptions into 500 for now
    assert res_bad.status_code in (400, 500)


def test_search_tasks_title_match_case_insensitive(client: TestClient):
    client.post("/tasks/", json=create_payload(title="Refactor Parser"))
    client.post("/tasks/", json=create_payload(title="write docs"))
    res = client.get("/tasks/search", params={"text": "parser"})
    assert res.status_code == 200
    data = res.json()
    assert any("Refactor Parser" == t["title"] for t in data)


def test_search_tasks_description_match(client: TestClient):
    client.post("/tasks/", json=create_payload(title="a", description="Implement fuzzy SEARCH"))
    client.post("/tasks/", json=create_payload(title="b", description="nothing relevant"))
    res = client.get("/tasks/search", params={"text": "search"})
    assert res.status_code == 200
    titles = [t["title"] for t in res.json()]
    assert "a" in titles


def test_search_tasks_pagination(client: TestClient):
    for i in range(5):
        client.post("/tasks/", json=create_payload(title=f"Feature {i}", description="feature work"))
    res1 = client.get("/tasks/search", params={"text": "feature", "skip": 0, "limit": 2})
    res2 = client.get("/tasks/search", params={"text": "feature", "skip": 2, "limit": 2})
    assert res1.status_code == 200 and res2.status_code == 200
    assert len(res1.json()) == 2
    assert len(res2.json()) == 2
    ids1 = {t["id"] for t in res1.json()}
    ids2 = {t["id"] for t in res2.json()}
    assert ids1.isdisjoint(ids2)


def test_search_tasks_empty_text_400(client: TestClient):
    # text provided but empty should trigger 400 from DB layer
    res = client.get("/tasks/search", params={"text": ""})
    assert res.status_code == 400


def test_search_tasks_no_results_404(client: TestClient):
    client.post("/tasks/", json=create_payload(title="Alpha"))
    res = client.get("/tasks/search", params={"text": "ZZZ_not_found"})
    assert res.status_code == 404


