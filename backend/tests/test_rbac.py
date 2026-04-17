from fastapi.testclient import TestClient

from app.main import app


def test_content_admin_is_blocked_from_ops_routes(test_db_session, content_auth_headers) -> None:
    client = TestClient(app)

    response = client.get("/api/dashboard/overview", headers=content_auth_headers)

    assert response.status_code == 403


def test_content_admin_can_access_content_routes(test_db_session, content_auth_headers) -> None:
    client = TestClient(app)

    response = client.get("/api/scenic-areas", headers=content_auth_headers)

    assert response.status_code == 200


def test_ops_admin_is_blocked_from_content_routes(test_db_session, ops_auth_headers) -> None:
    client = TestClient(app)

    response = client.get("/api/knowledge/documents", headers=ops_auth_headers)

    assert response.status_code == 403


def test_ops_admin_can_access_ops_routes(test_db_session, ops_auth_headers) -> None:
    client = TestClient(app)

    response = client.get("/api/operation-logs", headers=ops_auth_headers)

    assert response.status_code == 200


def test_super_admin_can_access_settings_routes(test_db_session, auth_headers) -> None:
    client = TestClient(app)

    response = client.get("/api/settings/ai-providers", headers=auth_headers)

    assert response.status_code == 200
