from fastapi.testclient import TestClient

from app.main import app


def test_backend_smoke_flow(test_db_session, auth_headers) -> None:
    client = TestClient(app)

    overview = client.get("/api/dashboard/overview", headers=auth_headers)

    assert overview.status_code == 200
    assert "total_events" in overview.json()
