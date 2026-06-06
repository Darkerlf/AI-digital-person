from fastapi.testclient import TestClient
from sqlalchemy import select

from app.main import app
from app.models.route_recommendation_record import RouteRecommendationRecord


def test_route_recommendation_generate_persists_record(test_db_session, auth_headers) -> None:
    client = TestClient(app)

    area_response = client.post(
        "/api/scenic-areas",
        headers=auth_headers,
        json={"code": "ROUTE-AREA", "name": "Route Area", "status": "active"},
    )
    area_id = area_response.json()["id"]
    spot_response = client.post(
        "/api/scenic-spots",
        headers=auth_headers,
        json={
            "scenic_area_id": area_id,
            "spot_code": "ROUTE-SPOT",
            "name": "Route Spot",
            "open_status": "open",
            "tags": ["history"],
        },
    )
    template_response = client.post(
        "/api/route-templates",
        headers=auth_headers,
        json={
            "scenic_area_id": area_id,
            "name": "Half Day Route",
            "template_type": "fixed",
            "interest_tags": ["history"],
            "audience_tags": ["family"],
            "duration_min_minutes": 90,
            "duration_max_minutes": 180,
            "summary": "A focused route.",
            "status": "active",
            "priority": 5,
            "spots": [
                {
                    "scenic_spot_id": spot_response.json()["id"],
                    "sort_order": 1,
                    "stay_minutes": 30,
                    "highlight": "Start here",
                }
            ],
        },
    )
    assert template_response.status_code == 201

    response = client.post(
        "/api/route-recommendations/generate",
        headers=auth_headers,
        json={
            "scenic_area_id": area_id,
            "interest_tags": ["history"],
            "audience_tags": ["family"],
            "duration_minutes": 120,
        },
    )

    assert response.status_code == 200
    record = test_db_session.execute(select(RouteRecommendationRecord)).scalar_one()
    assert record.scenic_area_id == area_id
    assert record.duration_minutes == 120
    assert record.matched_template_id == template_response.json()["id"]
    assert record.matched_template_name == "Half Day Route"
    assert record.fallback_used is False
    assert record.request_json["interest_tags"] == ["history"]
    assert record.response_json["matched_template"]["name"] == "Half Day Route"
