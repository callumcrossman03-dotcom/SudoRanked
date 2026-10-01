import os

os.environ["SUDORANK_DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from fastapi.testclient import TestClient

from app import models
from app.database import engine
from app.main import app


@pytest.fixture(autouse=True)
def _fresh_db():
    """Give every test a clean, empty schema on the shared in-memory db."""
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def register_user(client):
    """Register + log in a user, returning an Authorization header dict."""

    def _register(username, password="hunter22"):
        resp = client.post(
            "/api/auth/register", json={"username": username, "password": password}
        )
        assert resp.status_code == 201, resp.text
        login_resp = client.post(
            "/api/auth/login", data={"username": username, "password": password}
        )
        assert login_resp.status_code == 200, login_resp.text
        token = login_resp.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _register
