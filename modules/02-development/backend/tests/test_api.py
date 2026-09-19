from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.store import store


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_store() -> None:
    store.reset()


def test_root_route() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "System Design Interview Platform API"}


def auth_headers() -> dict[str, str]:
    response = client.post(
        "/v1/auth/login",
        json={"email": "interviewer@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['accessToken']}"}


def test_public_metadata_and_auth_required_for_sessions() -> None:
    defaults = client.get("/v1/component-defaults")
    assert defaults.status_code == 200
    assert defaults.json()["service"]["label"] == "Service"

    unauthorized = client.get("/v1/sessions")
    assert unauthorized.status_code == 401
    assert unauthorized.json()["code"] == "unauthorized"


def test_login_rejects_bad_password() -> None:
    response = client.post(
        "/v1/auth/login",
        json={"email": "interviewer@example.com", "password": "wrong"},
    )
    assert response.status_code == 401
    assert response.json()["message"] == "Invalid email or password."


def test_session_lifecycle_and_link_management() -> None:
    headers = auth_headers()

    listed = client.get("/v1/sessions", headers=headers)
    assert listed.status_code == 200
    assert listed.json()[0]["id"] == "session-demo"

    created = client.post(
        "/v1/sessions",
        headers=headers,
        json={"title": "Design a chat app", "prompt": "Build reliable group chat."},
    )
    assert created.status_code == 201
    session = created.json()
    assert session["state"] == "draft"
    assert session["canvas"]["elements"] == []

    link = client.post(f"/v1/sessions/{session['id']}/candidate-link", headers=headers)
    assert link.status_code == 201
    assert link.json()["token"]

    revoked = client.delete(f"/v1/sessions/{session['id']}/candidate-link", headers=headers)
    assert revoked.status_code == 200
    assert revoked.json()["revokedAt"] is not None


def test_candidate_join_receives_participant_token_and_can_edit_canvas() -> None:
    joined = client.post("/v1/join/candidate-demo-link", json={"displayName": "Alex Candidate"})
    assert joined.status_code == 200
    participant_token = joined.json()["participantToken"]
    headers = {"Authorization": f"Bearer {participant_token}"}

    read = client.get("/v1/sessions/session-demo", headers=headers)
    assert read.status_code == 200
    assert read.json()["id"] == "session-demo"

    added = client.post(
        "/v1/sessions/session-demo/canvas/elements",
        headers=headers,
        json={"type": "service", "x": 44, "y": 55},
    )
    assert added.status_code == 201
    assert added.json()["label"] == "Service"

    updated = client.patch(
        f"/v1/sessions/session-demo/canvas/elements/{added.json()['id']}",
        headers=headers,
        json={"label": "Realtime API"},
    )
    assert updated.status_code == 200
    assert updated.json()["label"] == "Realtime API"


def test_candidate_cannot_edit_when_locked() -> None:
    user_headers = auth_headers()
    joined = client.post("/v1/join/candidate-demo-link", json={"displayName": "Locked Candidate"})
    assert joined.status_code == 200
    participant_headers = {"Authorization": f"Bearer {joined.json()['participantToken']}"}

    locked = client.patch(
        "/v1/sessions/session-demo",
        headers=user_headers,
        json={"candidateEditingEnabled": False},
    )
    assert locked.status_code == 200

    denied = client.post(
        "/v1/sessions/session-demo/canvas/elements",
        headers=participant_headers,
        json={"type": "cache", "x": 10, "y": 10},
    )
    assert denied.status_code == 403
    assert denied.json()["code"] == "forbidden"

    client.patch(
        "/v1/sessions/session-demo",
        headers=user_headers,
        json={"candidateEditingEnabled": True},
    )


def test_canvas_connections_strokes_delete_and_export() -> None:
    headers = auth_headers()

    connection = client.post(
        "/v1/sessions/session-demo/canvas/connections",
        headers=headers,
        json={"from": "el-1", "to": "el-2", "label": "TLS"},
    )
    assert connection.status_code == 201
    assert connection.json()["from"] == "el-1"

    stroke = client.post(
        "/v1/sessions/session-demo/canvas/strokes",
        headers=headers,
        json={"color": "#0f766e", "width": 4, "points": [[1, 2], [3, 4]]},
    )
    assert stroke.status_code == 201

    canvas = client.delete("/v1/sessions/session-demo/canvas/elements/el-8", headers=headers)
    assert canvas.status_code == 200
    assert all(element["id"] != "el-8" for element in canvas.json()["elements"])

    exported = client.get("/v1/sessions/session-demo/export.json", headers=headers)
    assert exported.status_code == 200
    assert exported.json()["canvas"]["connections"]
