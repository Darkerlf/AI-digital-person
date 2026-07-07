from fastapi.testclient import TestClient

from app.main import app


def test_create_scenic_area_rejects_blank_required_fields(test_db_session, auth_headers) -> None:
    response = TestClient(app).post(
        "/api/scenic-areas",
        headers=auth_headers,
        json={"code": "   ", "name": "", "description": "", "status": "active"},
    )

    assert response.status_code == 422


def test_delete_scenic_area_removes_it_from_list(test_db_session, auth_headers) -> None:
    client = TestClient(app)
    create_response = client.post(
        "/api/scenic-areas",
        headers=auth_headers,
        json={"code": "DELETE-ME", "name": "Delete Me", "description": "temporary", "status": "active"},
    )
    assert create_response.status_code == 201
    area_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/scenic-areas/{area_id}", headers=auth_headers)
    list_response = client.get("/api/scenic-areas", headers=auth_headers)

    assert delete_response.status_code == 204
    assert all(item["id"] != area_id for item in list_response.json())
