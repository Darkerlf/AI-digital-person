from fastapi.testclient import TestClient

from app.main import app
from app.models.service_poi import ServicePOI


def test_service_poi_coordinates_use_double_precision() -> None:
    assert ServicePOI.__table__.c.latitude.type.precision == 53
    assert ServicePOI.__table__.c.longitude.type.precision == 53


def test_admin_manages_service_pois_and_tourist_api_reads_database(test_db_session, auth_headers) -> None:
    client = TestClient(app)

    area_response = client.post(
        "/api/scenic-areas",
        headers=auth_headers,
        json={"code": "LS", "name": "Lingshan", "description": "Demo area", "status": "active"},
    )
    assert area_response.status_code == 201

    create_response = client.post(
        "/api/service-pois",
        headers=auth_headers,
        json={
            "scenic_area_id": area_response.json()["id"],
            "name": "Visitor Center",
            "category": "service_center",
            "area_text": "Main entrance",
            "description": "Information and lost-and-found.",
            "open_hours": "08:30-17:00",
            "latitude": 31.42034,
            "longitude": 120.10355,
            "status": "active",
        },
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["id"]
    assert created["name"] == "Visitor Center"

    list_response = client.get("/api/service-pois", headers=auth_headers)
    assert list_response.status_code == 200
    assert list_response.json()["items"][0]["name"] == "Visitor Center"

    update_response = client.put(
        f"/api/service-pois/{created['id']}",
        headers=auth_headers,
        json={"latitude": 31.421872, "longitude": 120.103365, "category": "toilet"},
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["category"] == "toilet"
    assert updated["latitude"] == 31.421872

    tourist_response = client.get("/api/tourist/service-pois?category=toilet")
    assert tourist_response.status_code == 200
    tourist_items = tourist_response.json()["items"]
    assert len(tourist_items) == 1
    assert tourist_items[0]["id"] == created["id"]
    assert tourist_items[0]["name"] == "Visitor Center"


def test_service_poi_delete_removes_item_from_admin_list(test_db_session, auth_headers) -> None:
    client = TestClient(app)

    create_response = client.post(
        "/api/service-pois",
        headers=auth_headers,
        json={
            "name": "Parking Entrance",
            "category": "parking",
            "latitude": 31.42349,
            "longitude": 120.104927,
            "status": "active",
        },
    )
    assert create_response.status_code == 201

    delete_response = client.delete(f"/api/service-pois/{create_response.json()['id']}", headers=auth_headers)
    assert delete_response.status_code == 204

    list_response = client.get("/api/service-pois", headers=auth_headers)
    assert list_response.status_code == 200
    assert list_response.json()["items"] == []


def test_tourist_service_pois_fallback_only_when_database_has_no_service_pois(test_db_session, auth_headers) -> None:
    client = TestClient(app)
    create_response = client.post(
        "/api/service-pois",
        headers=auth_headers,
        json={
            "name": "Brahma Palace Restaurant",
            "category": "restaurant",
            "latitude": 31.428762,
            "longitude": 120.102357,
            "status": "active",
        },
    )
    assert create_response.status_code == 201

    response = client.get("/api/tourist/service-pois?category=toilet")

    assert response.status_code == 200
    assert response.json()["items"] == []
