import pytest

import app as app_module


@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True
    app_module.TASKS.clear()
    with app_module.app.test_client() as test_client:
        yield test_client


def test_index(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.get_json()["message"] == "DevOps demo API"


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_list_tasks_empty(client):
    resp = client.get("/api/tasks")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_create_task(client):
    resp = client.post("/api/tasks", json={"title": "learn kubernetes"})
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["id"] == 1
    assert body["title"] == "learn kubernetes"
    assert body["done"] is False
    assert len(client.get("/api/tasks").get_json()) == 1


def test_create_task_requires_title(client):
    resp = client.post("/api/tasks", json={"title": "   "})
    assert resp.status_code == 400


def test_create_task_without_json_body(client):
    resp = client.post("/api/tasks")
    assert resp.status_code == 400


def test_error_endpoint_returns_500(client):
    assert client.get("/api/error").status_code == 500


def test_metrics_exposes_request_counter(client):
    client.get("/health")
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert b"http_requests_total" in resp.data
    assert b"http_request_duration_seconds" in resp.data
