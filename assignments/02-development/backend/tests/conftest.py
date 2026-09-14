import pytest
from fastapi.testclient import TestClient
import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app.auth import hash_password
from app.main import app
from app.store import store


@pytest.fixture()
def client() -> TestClient:
    store.reset(password_hash=hash_password("demo"))
    return TestClient(app)


@pytest.fixture()
def auth_headers(client: TestClient) -> dict[str, str]:
    response = client.post("/auth/login", json={"username": "demo", "password": "demo"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
