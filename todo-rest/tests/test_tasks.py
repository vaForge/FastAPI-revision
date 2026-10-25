
import pytest
from fastapi.testclient import TestClient

from main import app
from service import reset_tasks


@pytest.fixture(autouse=True)
def clean_storage():
    # Give every test a fresh, predictable in-memory store.
    reset_tasks()
    yield
    reset_tasks()


client = TestClient(app)


def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "Todo API is running"


def test_create_task():
    response = client.post(
        "/tasks",
        json={"title": "Learn FastAPI", "completed": False},
    )

    assert response.status_code == 201
    assert response.json()["id"] == 1
    assert response.json()["title"] == "Learn FastAPI"


def test_list_and_filter_tasks():
    client.post("/tasks", json={"title": "Learn FastAPI"})
    client.post("/tasks", json={"title": "Build API", "completed": True})

    response = client.get("/tasks?completed=true")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Build API"


def test_update_task():
    created = client.post("/tasks", json={"title": "Old title"})
    task_id = created.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        json={"completed": True},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Old title"
    assert response.json()["completed"] is True


def test_delete_task():
    created = client.post("/tasks", json={"title": "Temporary"})
    task_id = created.json()["id"]

    response = client.delete(f"/tasks/{task_id}")

    assert response.status_code == 204
    assert response.content == b""

    missing = client.get(f"/tasks/{task_id}")
    assert missing.status_code == 404


def test_invalid_title():
    response = client.post("/tasks", json={"title": ""})

    assert response.status_code == 422


def test_missing_task():
    response = client.get("/tasks/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"
