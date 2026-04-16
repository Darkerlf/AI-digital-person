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
