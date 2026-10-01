def test_register_then_login(client):
    resp = client.post(
        "/api/auth/register", json={"username": "alice", "password": "hunter22"}
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["username"] == "alice"
    assert "id" in body

    resp = client.post(
        "/api/auth/login", data={"username": "alice", "password": "hunter22"}
    )
    assert resp.status_code == 200
    assert resp.json()["token_type"] == "bearer"
    assert resp.json()["access_token"]


def test_register_rejects_duplicate_username(client):
    client.post("/api/auth/register", json={"username": "alice", "password": "hunter22"})
    resp = client.post(
        "/api/auth/register", json={"username": "alice", "password": "different"}
    )
    assert resp.status_code == 400


def test_register_rejects_short_password(client):
    resp = client.post(
        "/api/auth/register", json={"username": "alice", "password": "123"}
    )
    assert resp.status_code == 422


def test_login_rejects_wrong_password(client):
    client.post("/api/auth/register", json={"username": "alice", "password": "hunter22"})
    resp = client.post(
        "/api/auth/login", data={"username": "alice", "password": "wrong"}
    )
    assert resp.status_code == 401


def test_login_rejects_unknown_user(client):
    resp = client.post(
        "/api/auth/login", data={"username": "ghost", "password": "whatever"}
    )
    assert resp.status_code == 401


def test_me_requires_token(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_me_rejects_garbage_token(client):
    resp = client.get("/api/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert resp.status_code == 401


def test_me_returns_current_user(client, register_user):
    headers = register_user("alice")
    resp = client.get("/api/auth/me", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["username"] == "alice"
