from fastapi.testclient import TestClient

from app.main import app
from app.models.conversation_message import ConversationMessage
from app.models.conversation_session import ConversationSession
from app.models.scenic_area import ScenicArea
from app.models.scenic_spot import ScenicSpot
from app.models.service_poi import ServicePOI
from app.models.visitor import Visitor
from app.core.security import create_access_token


def _seed_prd_tourist_data(db):
    area = ScenicArea(code="LS", name="灵山胜境", description="Demo", status="active")
    db.add(area)
    db.flush()
    db.add_all(
        [
            ScenicSpot(
                scenic_area_id=area.id,
                spot_code="LS-001",
                name="灵山大佛",
                alias="大佛",
                latitude=31.430266,
                longitude=120.096427,
                detail_intro="世界最高露天青铜释迦牟尼立像。",
                highlights="登高抱佛脚，俯瞰太湖。",
                suggested_duration_minutes=60,
                open_status="open",
            ),
            ScenicSpot(
                scenic_area_id=area.id,
                spot_code="LS-002",
                name="灵山梵宫",
                latitude=31.428867,
                longitude=120.102472,
                detail_intro="佛教艺术殿堂。",
                suggested_duration_minutes=45,
                open_status="open",
            ),
        ]
    )
    db.add(
        ServicePOI(
            scenic_area_id=area.id,
            name="游客服务中心",
            category="service_center",
            area_text="入口服务区",
            description="咨询和失物招领。",
            open_hours="08:30-17:00",
            latitude=31.421805,
            longitude=120.10463,
            status="active",
        )
    )
    session = ConversationSession(
        scenic_area_id=area.id,
        session_key="tourist_demo_session",
        channel="miniprogram",
        visitor_id="visitor-001",
        status="active",
    )
    db.add(session)
    db.flush()
    db.add(
        ConversationMessage(
            session_id=session.id,
            question_text="灵山大佛多高？",
            answer_text="灵山大佛通高88米。",
            latency_ms=800,
        )
    )
    db.commit()
    return area


def test_tourist_home_config_exposes_prd_entry_points(test_db_session):
    _seed_prd_tourist_data(test_db_session)
    client = TestClient(app)

    response = client.get("/api/tourist/home?scenic_area_id=1")

    assert response.status_code == 200
    data = response.json()
    assert data["scenic_name"] == "灵山胜境"
    assert len(data["quick_questions"]) >= 4
    assert "推荐游览路线" in data["quick_questions"]
    assert [item["name"] for item in data["hot_spots"]] == ["灵山大佛", "灵山梵宫"]
    assert data["service_categories"][0]["value"] == "toilet"
    assert data["today_route"]["duration_minutes"] == 240


def test_tourist_spot_family_narration_is_chinese_and_child_friendly(test_db_session):
    _seed_prd_tourist_data(test_db_session)
    client = TestClient(app)

    response = client.get("/api/tourist/scenic-spots/1/narration?mode=family")

    assert response.status_code == 200
    narration = response.json()["narration"]
    assert "Children" not in narration
    assert "We can" not in narration
    assert "灵山大佛" in narration
    assert "小朋友" in narration
    assert "找一找" in narration
    assert "家长" in narration
    assert "抬头" in narration
    assert "莲花座" in narration


def test_tourist_spot_family_narration_varies_by_spot(test_db_session):
    _seed_prd_tourist_data(test_db_session)
    client = TestClient(app)

    buddha = client.get("/api/tourist/scenic-spots/1/narration?mode=family").json()["narration"]
    palace = client.get("/api/tourist/scenic-spots/2/narration?mode=family").json()["narration"]
    buddha_body = buddha.split("亲子讲解：", 1)[1]
    palace_body = palace.split("亲子讲解：", 1)[1]

    assert "小朋友可以把这里当成一个会讲故事的观察点" not in buddha
    assert "小朋友可以把这里当成一个会讲故事的观察点" not in palace
    assert "如果孩子问到文化含义" not in buddha
    assert "如果孩子问到文化含义" not in palace
    assert buddha_body.split("。")[0] != palace_body.split("。")[0]
    assert buddha_body.rstrip("。").split("。")[-1] != palace_body.rstrip("。").split("。")[-1]


def test_tourist_map_guide_supports_list_mode_without_location(test_db_session):
    _seed_prd_tourist_data(test_db_session)
    client = TestClient(app)

    response = client.get("/api/tourist/map-guide?scenic_area_id=1&location_available=false")

    assert response.status_code == 200
    data = response.json()
    assert data["fallback_mode"] == "list"
    assert data["center"]["latitude"] == 31.428076
    assert data["spots"][0]["narration_url"].endswith("/api/tourist/scenic-spots/1/narration")
    assert data["service_pois"][0]["name"] == "游客服务中心"


def test_tourist_recent_records_are_available_without_admin_auth(test_db_session):
    _seed_prd_tourist_data(test_db_session)
    visitor = Visitor(openid="wx-prd-recent-records", nickname="记录游客")
    test_db_session.add(visitor)
    test_db_session.flush()
    for session in test_db_session.query(ConversationSession).all():
        session.visitor_id = str(visitor.id)
    test_db_session.commit()
    client = TestClient(app)

    response = client.get(
        "/api/tourist/recent-records",
        headers={"Authorization": f"Bearer {create_access_token(f'visitor:{visitor.id}')}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["items"][0]["visitor_id"] == str(visitor.id)
    assert data["items"][0]["messages"][0]["question_text"] == "灵山大佛多高？"


def test_tourist_map_guide_returns_fallback_service_pois(test_db_session):
    area = ScenicArea(code="LS", name="灵山胜境", description="Demo", status="active")
    test_db_session.add(area)
    test_db_session.commit()
    client = TestClient(app)

    response = client.get(f"/api/tourist/map-guide?scenic_area_id={area.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["service_pois"]
    assert {"toilet", "service_center"}.issubset({item["category"] for item in data["service_pois"]})


def test_tourist_map_guide_enriches_known_spot_coordinates(test_db_session):
    area = ScenicArea(code="LS", name="灵山胜境", description="Demo", status="active")
    test_db_session.add(area)
    test_db_session.flush()
    test_db_session.add_all(
        [
            ScenicSpot(
                scenic_area_id=area.id,
                spot_code="LS-JLGY",
                name="九龙灌浴",
                detail_intro="动态表演景观。",
                open_status="open",
            ),
            ScenicSpot(
                scenic_area_id=area.id,
                spot_code="LS-DF",
                name="灵山大佛",
                detail_intro="核心地标。",
                open_status="open",
            ),
        ]
    )
    test_db_session.commit()
    client = TestClient(app)

    response = client.get(f"/api/tourist/map-guide?scenic_area_id={area.id}")

    assert response.status_code == 200
    data = response.json()
    spots = {item["name"]: item for item in data["spots"]}
    assert spots["九龙灌浴"]["latitude"] == 31.424835
    assert spots["九龙灌浴"]["longitude"] == 120.100154
    assert spots["九龙灌浴"]["coordinate_source"] == "preset_gcj02"
    assert spots["灵山大佛"]["latitude"] == 31.430266
    assert spots["灵山大佛"]["longitude"] == 120.096427
