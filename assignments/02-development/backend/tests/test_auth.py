def test_login_returns_bearer_token_and_user(client):
    response = client.post("/auth/login", json={"username": "demo", "password": "demo"})

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["user"] == {"id": "user-1", "name": "Demo User"}


def test_invalid_login_is_rejected(client):
    response = client.post("/auth/login", json={"username": "demo", "password": "wrong"})

    assert response.status_code == 401


def test_protected_endpoints_require_bearer_token(client):
    response = client.get("/board")

    assert response.status_code == 401


def test_current_user_uses_bearer_token(client, auth_headers):
    response = client.get("/auth/me", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == {"id": "user-1", "name": "Demo User"}
