from fastapi.testclient import TestClient

from app.main import app


def test_create_and_list_scenic_spots(test_db_session, auth_headers) -> None:
    client = TestClient(app)

    area_response = client.post(
        "/api/scenic-areas",
        headers=auth_headers,
        json={"code": "LS", "name": "灵山胜境", "description": "示范景区", "status": "active"},
    )
    assert area_response.status_code == 201

    spot_response = client.post(
        "/api/scenic-spots",
        headers=auth_headers,
        json={
            "scenic_area_id": area_response.json()["id"],
            "spot_code": "LS-001",
            "name": "灵山大照壁",
            "alias": "华夏第一壁",
            "location_text": "景区入口处",
            "open_status": "open",
            "tags": ["历史", "拍照"],
        },
    )
    assert spot_response.status_code == 201

    list_response = client.get("/api/scenic-spots", headers=auth_headers)
    assert list_response.status_code == 200
    assert list_response.json()["items"][0]["spot_code"] == "LS-001"
