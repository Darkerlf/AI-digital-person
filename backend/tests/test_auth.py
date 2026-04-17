from fastapi.testclient import TestClient

from app.main import app


def test_login_returns_access_token(test_db_session) -> None:
    client = TestClient(app)

    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "admin123"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "access_token" in payload
    assert payload["token_type"] == "bearer"


def test_auth_me_returns_username_and_role(test_db_session, auth_headers) -> None:
    client = TestClient(app)

    response = client.get("/api/auth/me", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["username"] == "admin"
    assert response.json()["role"] == "super_admin"
