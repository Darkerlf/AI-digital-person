from fastapi.testclient import TestClient

from app.main import app


def _create_area_and_spot(client: TestClient, auth_headers: dict[str, str], area_code: str):
    area_response = client.post(
        "/api/scenic-areas",
        headers=auth_headers,
        json={
            "code": area_code,
            "name": f"{area_code} area",
            "description": "test area",
            "status": "active",
        },
    )
    assert area_response.status_code == 201
    scenic_area_id = area_response.json()["id"]

    spot_response = client.post(
        "/api/scenic-spots",
        headers=auth_headers,
        json={
            "scenic_area_id": scenic_area_id,
            "spot_code": f"{area_code}-SPOT-001",
            "name": f"{area_code} spot",
            "open_status": "open",
            "tags": ["culture"],
        },
    )
    assert spot_response.status_code == 201
    return scenic_area_id, spot_response.json()["id"]


def test_route_template_rejects_blank_name_and_empty_spots(test_db_session, auth_headers) -> None:
    client = TestClient(app)
    scenic_area_id, _ = _create_area_and_spot(client, auth_headers, "VALIDATE-A")

    response = client.post(
        "/api/route-templates",
        headers=auth_headers,
        json={
            "scenic_area_id": scenic_area_id,
            "name": "   ",
            "template_type": "fixed",
            "duration_min_minutes": 60,
            "duration_max_minutes": 120,
            "status": "active",
            "spots": [],
        },
    )

    assert response.status_code == 422


def test_route_template_rejects_invalid_duration_range(test_db_session, auth_headers) -> None:
    client = TestClient(app)
    scenic_area_id, spot_id = _create_area_and_spot(client, auth_headers, "VALIDATE-B")

    response = client.post(
        "/api/route-templates",
        headers=auth_headers,
        json={
            "scenic_area_id": scenic_area_id,
            "name": "Invalid duration",
            "template_type": "fixed",
            "duration_min_minutes": 180,
            "duration_max_minutes": 120,
            "status": "active",
            "spots": [{"scenic_spot_id": spot_id, "sort_order": 1, "stay_minutes": 30}],
        },
    )

    assert response.status_code == 422


def test_route_template_rejects_spots_from_other_scenic_area(test_db_session, auth_headers) -> None:
    client = TestClient(app)
    scenic_area_id, _ = _create_area_and_spot(client, auth_headers, "VALIDATE-C")
    _, other_spot_id = _create_area_and_spot(client, auth_headers, "VALIDATE-D")

    response = client.post(
        "/api/route-templates",
        headers=auth_headers,
        json={
            "scenic_area_id": scenic_area_id,
            "name": "Cross area route",
            "template_type": "fixed",
            "duration_min_minutes": 60,
            "duration_max_minutes": 120,
            "status": "active",
            "spots": [{"scenic_spot_id": other_spot_id, "sort_order": 1, "stay_minutes": 30}],
        },
    )

    assert response.status_code == 400


def test_route_template_update_rejects_removing_all_spots(test_db_session, auth_headers) -> None:
    client = TestClient(app)
    scenic_area_id, spot_id = _create_area_and_spot(client, auth_headers, "VALIDATE-E")

    create_response = client.post(
        "/api/route-templates",
        headers=auth_headers,
        json={
            "scenic_area_id": scenic_area_id,
            "name": "Valid route",
            "template_type": "fixed",
            "duration_min_minutes": 60,
            "duration_max_minutes": 120,
            "status": "active",
            "spots": [{"scenic_spot_id": spot_id, "sort_order": 1, "stay_minutes": 30}],
        },
    )
    assert create_response.status_code == 201

    response = client.put(
        f"/api/route-templates/{create_response.json()['id']}",
        headers=auth_headers,
        json={"spots": []},
    )

    assert response.status_code == 422
