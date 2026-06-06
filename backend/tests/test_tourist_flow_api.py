from fastapi.testclient import TestClient

from app.main import app
from app.models.route_template import RouteTemplate
from app.models.route_template_spot import RouteTemplateSpot
from app.models.scenic_area import ScenicArea
from app.models.scenic_spot import ScenicSpot


def _seed_scenic_data(test_db_session):
    area = ScenicArea(code="LS", name="Lingshan", description="Demo area", status="active")
    test_db_session.add(area)
    test_db_session.flush()

    buddha = ScenicSpot(
        scenic_area_id=area.id,
        spot_code="LS-001",
        name="Lingshan Grand Buddha",
        alias="Grand Buddha",
        location_text="Core north axis",
        detail_intro="A landmark bronze Buddha statue.",
        highlights="Iconic photo spot and Buddhist culture.",
        cultural_value="Represents Buddhist culture and blessing.",
        suggested_duration_minutes=60,
        open_status="open",
    )
    palace = ScenicSpot(
        scenic_area_id=area.id,
        spot_code="LS-002",
        name="Brahma Palace",
        location_text="West cultural zone",
        detail_intro="A palace-style Buddhist art hall.",
        highlights="Architecture and performance hall.",
        suggested_duration_minutes=45,
        open_status="open",
    )
    test_db_session.add_all([buddha, palace])
    test_db_session.flush()

    template = RouteTemplate(
        scenic_area_id=area.id,
        name="Classic Half Day",
        template_type="fixed",
        interest_tags_json='["culture"]',
        audience_tags_json='["family"]',
        duration_min_minutes=120,
        duration_max_minutes=240,
        summary="A compact route for first-time visitors.",
        status="active",
        priority=10,
    )
    test_db_session.add(template)
    test_db_session.flush()
    test_db_session.add_all(
        [
            RouteTemplateSpot(
                template_id=template.id,
                scenic_spot_id=buddha.id,
                sort_order=1,
                stay_minutes=60,
                highlight="Landmark stop",
            ),
            RouteTemplateSpot(
                template_id=template.id,
                scenic_spot_id=palace.id,
                sort_order=2,
                stay_minutes=45,
                highlight="Indoor art stop",
            ),
        ]
    )
    test_db_session.commit()
    return area, buddha


def test_tourist_route_recommendation_does_not_require_admin_auth(test_db_session) -> None:
    area, _ = _seed_scenic_data(test_db_session)
    client = TestClient(app)

    response = client.post(
        "/api/tourist/routes/recommend",
        json={
            "scenic_area_id": area.id,
            "duration_minutes": 180,
            "interest_tags": ["culture"],
            "audience_tags": ["family"],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["matched_template"]["name"] == "Classic Half Day"
    assert [spot["name"] for spot in data["spots"]] == ["Lingshan Grand Buddha", "Brahma Palace"]


def test_tourist_scenic_spot_narration_supports_modes(test_db_session) -> None:
    _, spot = _seed_scenic_data(test_db_session)
    client = TestClient(app)

    response = client.get(f"/api/tourist/scenic-spots/{spot.id}/narration?mode=family")

    assert response.status_code == 200
    data = response.json()
    assert data["spot_id"] == spot.id
    assert data["mode"] == "family"
    assert "Lingshan Grand Buddha" in data["title"]
    assert "children" in data["narration"].lower()


def test_tourist_service_pois_returns_fallback_items(test_db_session) -> None:
    client = TestClient(app)

    response = client.get("/api/tourist/service-pois?category=toilet")

    assert response.status_code == 200
    data = response.json()
    assert data["items"]
    assert data["items"][0]["category"] == "toilet"
    assert "name" in data["items"][0]
    assert data["items"][0]["name"] == "公共厕所"
    assert data["items"][0]["latitude"] == 31.421872
    assert data["items"][0]["longitude"] == 120.103365


def test_tourist_feedback_accepts_score_and_content(test_db_session) -> None:
    client = TestClient(app)

    response = client.post(
        "/api/tourist/feedback",
        json={
            "sentiment": "negative",
            "score": 2,
            "content": "The route was too long.",
            "scenic_area_id": None,
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
