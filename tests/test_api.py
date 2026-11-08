import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    testing_session = sessionmaker(bind=engine, autoflush=False)

    def override_get_db():
        db = testing_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_ready(client):
    assert client.get("/ready").status_code == 200


def test_create_and_list(client):
    r = client.post("/tasks", json={"title": "learn docker"})
    assert r.status_code == 201
    assert r.json()["done"] is False
    tasks = client.get("/tasks").json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "learn docker"


def test_empty_title_rejected(client):
    r = client.post("/tasks", json={"title": ""})
    assert r.status_code == 422


def test_update(client):
    task_id = client.post("/tasks", json={"title": "a"}).json()["id"]
    r = client.patch(f"/tasks/{task_id}", json={"done": True})
    assert r.status_code == 200
    assert r.json()["done"] is True
    assert r.json()["title"] == "a"


def test_delete(client):
    task_id = client.post("/tasks", json={"title": "a"}).json()["id"]
    assert client.delete(f"/tasks/{task_id}").status_code == 204
    assert client.get("/tasks").json() == []


def test_missing_task_returns_404(client):
    assert client.patch("/tasks/999", json={"done": True}).status_code == 404
    assert client.delete("/tasks/999").status_code == 404
def test_update_with_null_is_ignored(client):
    task_id = client.post("/tasks", json={"title": "a"}).json()["id"]
    r = client.patch(f"/tasks/{task_id}", json={"title": None})
    assert r.status_code == 200
    assert r.json()["title"] == "a"    