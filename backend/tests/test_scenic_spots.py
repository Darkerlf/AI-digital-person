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


def test_update_scenic_spot_coordinates(test_db_session, auth_headers) -> None:
    client = TestClient(app)

    area_response = client.post(
        "/api/scenic-areas",
        headers=auth_headers,
        json={"code": "LS", "name": "灵山胜境", "description": "示范景区", "status": "active"},
    )
    spot_response = client.post(
        "/api/scenic-spots",
        headers=auth_headers,
        json={
            "scenic_area_id": area_response.json()["id"],
            "spot_code": "LS-JLGY",
            "name": "九龙灌浴",
            "open_status": "open",
            "tags": [],
        },
    )

    response = client.put(
        f"/api/scenic-spots/{spot_response.json()['id']}",
        headers=auth_headers,
        json={"latitude": 31.424835, "longitude": 120.100154},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["latitude"] == 31.424835
    assert data["longitude"] == 120.100154


def test_update_scenic_spot_product_content_fields(test_db_session, auth_headers) -> None:
    client = TestClient(app)

    area_response = client.post(
        "/api/scenic-areas",
        headers=auth_headers,
        json={"code": "AREA-CONTENT", "name": "Content Area", "status": "active"},
    )
    spot_response = client.post(
        "/api/scenic-spots",
        headers=auth_headers,
        json={
            "scenic_area_id": area_response.json()["id"],
            "spot_code": "CONTENT-001",
            "name": "Content Spot",
            "open_status": "open",
            "tags": [],
        },
    )

    response = client.put(
        f"/api/scenic-spots/{spot_response.json()['id']}",
        headers=auth_headers,
        json={
            "cover_image_url": "https://example.com/cover.jpg",
            "guide_text": "A concise guide script for visitors.",
            "target_audience": "families, seniors",
            "parameters_text": "height 12m",
            "core_function": "landmark",
            "cultural_value": "local heritage",
            "detail_intro": "Detailed introduction",
            "highlights": "Best photo point",
            "performance_info": "10:00 show",
            "remarks": "Mind the steps",
            "suggested_duration_minutes": 35,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["cover_image_url"] == "https://example.com/cover.jpg"
    assert data["guide_text"] == "A concise guide script for visitors."
    assert data["target_audience"] == "families, seniors"
    assert data["parameters_text"] == "height 12m"
    assert data["performance_info"] == "10:00 show"
    assert data["remarks"] == "Mind the steps"
    assert data["suggested_duration_minutes"] == 35


def test_list_scenic_spots_filters_by_keyword_and_open_status(test_db_session, auth_headers) -> None:
    client = TestClient(app)

    area_response = client.post(
        "/api/scenic-areas",
        headers=auth_headers,
        json={"code": "AREA-FILTER", "name": "Filter Area", "status": "active"},
    )
    area_id = area_response.json()["id"]
    for payload in [
        {
            "scenic_area_id": area_id,
            "spot_code": "FILTER-OPEN",
            "name": "Lotus Garden",
            "alias": "Water Court",
            "open_status": "open",
            "tags": ["garden"],
        },
        {
            "scenic_area_id": area_id,
            "spot_code": "FILTER-CLOSED",
            "name": "Lotus Tower",
            "alias": "Closed Tower",
            "open_status": "closed",
            "tags": ["tower"],
        },
    ]:
        assert client.post("/api/scenic-spots", headers=auth_headers, json=payload).status_code == 201

    response = client.get("/api/scenic-spots?keyword=Lotus&open_status=open", headers=auth_headers)

    assert response.status_code == 200
    items = response.json()["items"]
    assert [item["spot_code"] for item in items] == ["FILTER-OPEN"]
