from fastapi.testclient import TestClient

from app.main import app
from app.models.scenic_area import ScenicArea
from app.models.scenic_spot import ScenicSpot
from app.models.service_poi import ServicePOI
from app.services.walk_guide_service import WalkGuideService


class FakeWalkingClient:
    def direction_walking(self, *, from_point: dict, to_point: dict):
        return {
            "distance_meters": 200,
            "duration_minutes": 5,
            "polyline": [from_point, to_point],
            "provider": "tencent_walking",
            "raw": {"distance": 200},
        }


class EmptyWalkingClient:
    def direction_walking(self, *, from_point: dict, to_point: dict):
        return None


class InvalidPolylineClient:
    def direction_walking(self, *, from_point: dict, to_point: dict):
        return {
            "distance_meters": 200,
            "duration_minutes": 5,
            "polyline": [from_point, {"latitude": to_point["latitude"], "longitude": 999}],
            "provider": "tencent_walking",
            "raw": {"distance": 200},
        }


def _seed_walk_guide_data(test_db_session) -> tuple[int, int, int]:
    area = ScenicArea(code="WG", name="Walk Guide Area", status="active")
    test_db_session.add(area)
    test_db_session.flush()
    first = ScenicSpot(
        scenic_area_id=area.id,
        spot_code="WG-1",
        name="Start Gate",
        latitude=31.0,
        longitude=120.0,
        coordinate_source="tencent_place",
        coordinate_verified=True,
        open_status="open",
    )
    second = ScenicSpot(
        scenic_area_id=area.id,
        spot_code="WG-2",
        name="Buddha Hall",
        latitude=31.001,
        longitude=120.001,
        coordinate_source="tencent_place",
        coordinate_verified=True,
        open_status="open",
    )
    poi = ServicePOI(
        scenic_area_id=area.id,
        name="沿途卫生间",
        category="toilet",
        area_text="主路旁",
        latitude=31.0005,
        longitude=120.0005,
        status="active",
    )
    far_poi = ServicePOI(
        scenic_area_id=area.id,
        name="远处餐饮",
        category="restaurant",
        area_text="远处",
        latitude=31.02,
        longitude=120.02,
        status="active",
    )
    test_db_session.add_all([first, second, poi, far_poi])
    test_db_session.commit()
    return area.id, first.id, second.id


def test_walk_guide_service_builds_legs_and_filters_along_route_pois(test_db_session):
    area_id, first_id, second_id = _seed_walk_guide_data(test_db_session)

    result = WalkGuideService(test_db_session, map_client=FakeWalkingClient()).build(
        {
            "scenic_area_id": area_id,
            "spots": [
                {"scenic_spot_id": first_id, "name": "Start Gate"},
                {"scenic_spot_id": second_id, "name": "Buddha Hall"},
            ],
            "service_needs": ["卫生间"],
        }
    )

    assert result["total_distance_meters"] == 200
    assert result["total_duration_minutes"] == 5
    assert result["legs"][0]["provider"] == "tencent_walking"
    assert result["polyline"] == [
        {"latitude": 31.0, "longitude": 120.0},
        {"latitude": 31.001, "longitude": 120.001},
    ]
    assert [poi["name"] for poi in result["service_pois"]] == ["沿途卫生间"]
    assert result["fallback_used"] is False
    assert result["warnings"] == []


def test_walk_guide_service_falls_back_to_straight_line_when_tencent_has_no_route(test_db_session):
    area_id, first_id, second_id = _seed_walk_guide_data(test_db_session)

    result = WalkGuideService(test_db_session, map_client=EmptyWalkingClient()).build(
        {
            "scenic_area_id": area_id,
            "spots": [
                {"scenic_spot_id": first_id, "name": "Start Gate"},
                {"scenic_spot_id": second_id, "name": "Buddha Hall"},
            ],
        }
    )

    assert result["fallback_used"] is True
    assert result["legs"][0]["provider"] == "straight_line_fallback"
    assert result["legs"][0]["distance_meters"] > 0
    assert "腾讯步行路线暂不可用" in result["warnings"][0]


def test_walk_guide_service_ignores_invalid_current_location(test_db_session):
    area_id, first_id, second_id = _seed_walk_guide_data(test_db_session)

    result = WalkGuideService(test_db_session, map_client=FakeWalkingClient()).build(
        {
            "scenic_area_id": area_id,
            "spots": [
                {"scenic_spot_id": first_id, "name": "Start Gate"},
                {"scenic_spot_id": second_id, "name": "Buddha Hall"},
            ],
            "start_location": {"latitude": 31.0, "longitude": 999},
        }
    )

    assert [stop["name"] for stop in result["stops"]] == ["Start Gate", "Buddha Hall"]
    assert result["fallback_used"] is False
    assert any("当前位置坐标异常" in item for item in result["warnings"])
    assert all(-180 <= point["longitude"] <= 180 for point in result["polyline"])


def test_walk_guide_service_rejects_invalid_provider_polyline(test_db_session):
    area_id, first_id, second_id = _seed_walk_guide_data(test_db_session)

    result = WalkGuideService(test_db_session, map_client=InvalidPolylineClient()).build(
        {
            "scenic_area_id": area_id,
            "spots": [
                {"scenic_spot_id": first_id, "name": "Start Gate"},
                {"scenic_spot_id": second_id, "name": "Buddha Hall"},
            ],
        }
    )

    assert result["fallback_used"] is True
    assert result["legs"][0]["provider"] == "straight_line_fallback"
    assert all(-180 <= point["longitude"] <= 180 for point in result["polyline"])


def test_tourist_walk_guide_endpoint_returns_walkable_route(test_db_session, monkeypatch, visitor_auth_headers):
    area_id, first_id, second_id = _seed_walk_guide_data(test_db_session)
    monkeypatch.setattr(
        "app.api.routers.tourist_chat.WalkGuideService",
        lambda db: WalkGuideService(db, map_client=FakeWalkingClient()),
    )

    response = TestClient(app).post(
        "/api/tourist/routes/walk-guide",
        headers=visitor_auth_headers,
        json={
            "scenic_area_id": area_id,
            "spots": [
                {"scenic_spot_id": first_id, "name": "Start Gate"},
                {"scenic_spot_id": second_id, "name": "Buddha Hall"},
            ],
            "service_needs": ["卫生间"],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total_distance_meters"] == 200
    assert data["legs"][0]["from_name"] == "Start Gate"
    assert data["legs"][0]["to_name"] == "Buddha Hall"
    assert data["stops"][0]["scenic_spot_id"] == first_id
