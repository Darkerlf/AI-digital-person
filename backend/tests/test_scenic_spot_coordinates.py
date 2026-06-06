from fastapi.testclient import TestClient

from app.main import app
from app.services import scenic_spot_coordinate_service


class FakeTencentMapClient:
    def search_places(self, *, keyword: str, latitude: float, longitude: float, radius: int):
        assert keyword == "Test Area Buddha Plaza"
        assert latitude == 31.428076
        assert longitude == 120.098006
        assert radius == 8000
        return [
            {
                "id": "poi-close",
                "title": "Buddha Plaza",
                "address": "Inside Test Area",
                "category": "tourism",
                "location": {"lat": 31.430266, "lng": 120.096427},
            },
            {
                "id": "poi-far",
                "title": "Another Plaza",
                "address": "Far away",
                "category": "tourism",
                "location": {"lat": 31.5, "lng": 120.2},
            },
        ]


def _create_spot(client: TestClient, auth_headers: dict[str, str]) -> int:
    area_response = client.post(
        "/api/scenic-areas",
        headers=auth_headers,
        json={"code": "TA", "name": "Test Area", "status": "active"},
    )
    assert area_response.status_code == 201
    spot_response = client.post(
        "/api/scenic-spots",
        headers=auth_headers,
        json={
            "scenic_area_id": area_response.json()["id"],
            "spot_code": "TA-001",
            "name": "Buddha Plaza",
            "open_status": "open",
            "tags": [],
        },
    )
    assert spot_response.status_code == 201
    return spot_response.json()["id"]


def test_scenic_spot_coordinate_candidates_use_tencent_place_search(
    test_db_session,
    auth_headers,
    monkeypatch,
) -> None:
    monkeypatch.setattr(scenic_spot_coordinate_service, "TencentMapClient", FakeTencentMapClient)
    client = TestClient(app)
    spot_id = _create_spot(client, auth_headers)

    response = client.get(f"/api/scenic-spots/{spot_id}/coordinate-candidates", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["spot_id"] == spot_id
    assert data["search_keyword"] == "Test Area Buddha Plaza"
    assert data["candidates"][0]["provider"] == "tencent_place"
    assert data["candidates"][0]["tencent_poi_id"] == "poi-close"
    assert data["candidates"][0]["latitude"] == 31.430266
    assert data["candidates"][0]["longitude"] == 120.096427
    assert data["candidates"][0]["confidence"] > data["candidates"][1]["confidence"]


def test_batch_coordinate_candidates_scan_unverified_spots(test_db_session, auth_headers, monkeypatch) -> None:
    monkeypatch.setattr(scenic_spot_coordinate_service, "TencentMapClient", FakeTencentMapClient)
    client = TestClient(app)
    spot_id = _create_spot(client, auth_headers)

    response = client.get("/api/scenic-spots/coordinate-candidates/batch", headers=auth_headers)

    assert response.status_code == 200
    items = response.json()["items"]
    assert items[0]["spot_id"] == spot_id
    assert items[0]["spot_name"] == "Buddha Plaza"
    assert items[0]["candidates"][0]["tencent_poi_id"] == "poi-close"


def test_confirm_scenic_spot_coordinate_candidate_updates_metadata(test_db_session, auth_headers) -> None:
    client = TestClient(app)
    spot_id = _create_spot(client, auth_headers)

    response = client.post(
        f"/api/scenic-spots/{spot_id}/coordinate-candidates/confirm",
        headers=auth_headers,
        json={
            "latitude": 31.430266,
            "longitude": 120.096427,
            "coordinate_source": "tencent_place",
            "coordinate_confidence": 92,
            "tencent_poi_id": "poi-close",
            "coordinate_address": "Inside Test Area",
            "coordinate_raw_json": {"id": "poi-close", "title": "Buddha Plaza"},
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["latitude"] == 31.430266
    assert data["longitude"] == 120.096427
    assert data["coordinate_source"] == "tencent_place"
    assert data["coordinate_confidence"] == 92
    assert data["coordinate_verified"] is True
    assert data["tencent_poi_id"] == "poi-close"
    assert data["coordinate_address"] == "Inside Test Area"


def test_tourist_map_guide_exposes_verified_tencent_coordinates(test_db_session, auth_headers) -> None:
    client = TestClient(app)
    spot_id = _create_spot(client, auth_headers)

    assert client.post(
        f"/api/scenic-spots/{spot_id}/coordinate-candidates/confirm",
        headers=auth_headers,
        json={
            "latitude": 31.430266,
            "longitude": 120.096427,
            "coordinate_source": "tencent_place",
            "coordinate_confidence": 92,
            "tencent_poi_id": "poi-close",
            "coordinate_address": "Inside Test Area",
            "coordinate_raw_json": {"id": "poi-close", "title": "Buddha Plaza"},
        },
    ).status_code == 200

    response = client.get("/api/tourist/map-guide?scenic_area_id=1")

    assert response.status_code == 200
    spot = response.json()["spots"][0]
    assert spot["coordinate_source"] == "tencent_place"
    assert spot["coordinate_verified"] is True
