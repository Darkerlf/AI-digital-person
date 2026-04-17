from fastapi.testclient import TestClient

from app.main import app


def create_route_template_seed(client: TestClient, auth_headers: dict[str, str]) -> tuple[int, list[int]]:
    area_response = client.post(
        "/api/scenic-areas",
        headers=auth_headers,
        json={"code": "LS", "name": "灵山胜境", "description": "示范景区", "status": "active"},
    )
    scenic_area_id = area_response.json()["id"]

    spot_one = client.post(
        "/api/scenic-spots",
        headers=auth_headers,
        json={
            "scenic_area_id": scenic_area_id,
            "spot_code": "LS-001",
            "name": "灵山大佛",
            "alias": None,
            "location_text": "核心游览区",
            "open_status": "open",
            "tags": ["文化", "经典"],
        },
    ).json()
    spot_two = client.post(
        "/api/scenic-spots",
        headers=auth_headers,
        json={
            "scenic_area_id": scenic_area_id,
            "spot_code": "LS-002",
            "name": "梵宫",
            "alias": None,
            "location_text": "文化展示区",
            "open_status": "open",
            "tags": ["艺术", "拍照"],
        },
    ).json()
    spot_three = client.post(
        "/api/scenic-spots",
        headers=auth_headers,
        json={
            "scenic_area_id": scenic_area_id,
            "spot_code": "LS-003",
            "name": "五印坛城",
            "alias": None,
            "location_text": "体验区",
            "open_status": "open",
            "tags": ["禅意", "休闲"],
        },
    ).json()

    primary_template_response = client.post(
        "/api/route-templates",
        headers=auth_headers,
        json={
            "scenic_area_id": scenic_area_id,
            "name": "经典半日游",
            "template_type": "fixed",
            "interest_tags": ["文化", "经典"],
            "audience_tags": ["亲子"],
            "duration_min_minutes": 180,
            "duration_max_minutes": 240,
            "summary": "覆盖核心文化景点的半日路线。",
            "status": "active",
            "priority": 10,
            "rule_notes": "优先给首次来访游客。",
            "spots": [
                {
                    "scenic_spot_id": spot_one["id"],
                    "sort_order": 1,
                    "stay_minutes": 90,
                    "highlight": "核心地标",
                },
                {
                    "scenic_spot_id": spot_two["id"],
                    "sort_order": 2,
                    "stay_minutes": 60,
                    "highlight": "建筑与演艺",
                },
            ],
        },
    )
    assert primary_template_response.status_code == 201

    secondary_template_response = client.post(
        "/api/route-templates",
        headers=auth_headers,
        json={
            "scenic_area_id": scenic_area_id,
            "name": "轻松观景游",
            "template_type": "hybrid",
            "interest_tags": ["休闲", "拍照"],
            "audience_tags": ["情侣"],
            "duration_min_minutes": 120,
            "duration_max_minutes": 180,
            "summary": "面向轻松拍照和慢游人群。",
            "status": "active",
            "priority": 5,
            "rule_notes": "偏向非高峰时段。",
            "spots": [
                {
                    "scenic_spot_id": spot_two["id"],
                    "sort_order": 1,
                    "stay_minutes": 50,
                    "highlight": "建筑打卡",
                },
                {
                    "scenic_spot_id": spot_three["id"],
                    "sort_order": 2,
                    "stay_minutes": 45,
                    "highlight": "放松体验",
                },
            ],
        },
    )
    assert secondary_template_response.status_code == 201

    return scenic_area_id, [spot_one["id"], spot_two["id"], spot_three["id"]]


def test_route_template_crud_returns_nested_spots(test_db_session, auth_headers) -> None:
    client = TestClient(app)

    area_response = client.post(
        "/api/scenic-areas",
        headers=auth_headers,
        json={"code": "LS", "name": "灵山胜境", "description": "示范景区", "status": "active"},
    )
    assert area_response.status_code == 201
    scenic_area_id = area_response.json()["id"]

    spot_one_response = client.post(
        "/api/scenic-spots",
        headers=auth_headers,
        json={
            "scenic_area_id": scenic_area_id,
            "spot_code": "LS-001",
            "name": "灵山大佛",
            "alias": None,
            "location_text": "核心游览区",
            "open_status": "open",
            "tags": ["文化", "经典"],
        },
    )
    assert spot_one_response.status_code == 201
    spot_one = spot_one_response.json()

    spot_two_response = client.post(
        "/api/scenic-spots",
        headers=auth_headers,
        json={
            "scenic_area_id": scenic_area_id,
            "spot_code": "LS-002",
            "name": "梵宫",
            "alias": None,
            "location_text": "文化展示区",
            "open_status": "open",
            "tags": ["艺术"],
        },
    )
    assert spot_two_response.status_code == 201
    spot_two = spot_two_response.json()

    create_response = client.post(
        "/api/route-templates",
        headers=auth_headers,
        json={
            "scenic_area_id": scenic_area_id,
            "name": "经典半日游",
            "template_type": "fixed",
            "interest_tags": ["文化", "经典"],
            "audience_tags": ["亲子"],
            "duration_min_minutes": 180,
            "duration_max_minutes": 240,
            "summary": "覆盖核心文化景点的半日路线。",
            "status": "active",
            "priority": 10,
            "rule_notes": "优先给首次来访游客。",
            "spots": [
                {
                    "scenic_spot_id": spot_one["id"],
                    "sort_order": 1,
                    "stay_minutes": 90,
                    "highlight": "核心地标",
                },
                {
                    "scenic_spot_id": spot_two["id"],
                    "sort_order": 2,
                    "stay_minutes": 60,
                    "highlight": "建筑与演艺",
                },
            ],
        },
    )

    assert create_response.status_code == 201
    created_template = create_response.json()
    assert created_template["name"] == "经典半日游"
    assert created_template["spots"][0]["name"] == "灵山大佛"
    assert created_template["spots"][1]["sort_order"] == 2

    list_response = client.get("/api/route-templates", headers=auth_headers)
    assert list_response.status_code == 200
    assert list_response.json()["items"][0]["name"] == "经典半日游"

    detail_response = client.get(f"/api/route-templates/{created_template['id']}", headers=auth_headers)
    assert detail_response.status_code == 200
    assert detail_response.json()["spots"][0]["stay_minutes"] == 90

    update_response = client.put(
        f"/api/route-templates/{created_template['id']}",
        headers=auth_headers,
        json={
            "priority": 20,
            "summary": "更新后的半日路线。",
            "spots": [
                {
                    "scenic_spot_id": spot_two["id"],
                    "sort_order": 1,
                    "stay_minutes": 70,
                    "highlight": "先看梵宫",
                }
            ],
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["priority"] == 20
    assert update_response.json()["spots"][0]["name"] == "梵宫"

    delete_response = client.delete(f"/api/route-templates/{created_template['id']}", headers=auth_headers)
    assert delete_response.status_code == 204

    deleted_detail_response = client.get(f"/api/route-templates/{created_template['id']}", headers=auth_headers)
    assert deleted_detail_response.status_code == 404


def test_generate_route_recommendation_exact_match(test_db_session, auth_headers) -> None:
    client = TestClient(app)
    scenic_area_id, spot_ids = create_route_template_seed(client, auth_headers)

    response = client.post(
        "/api/route-recommendations/generate",
        headers=auth_headers,
        json={
            "scenic_area_id": scenic_area_id,
            "interest_tags": ["文化"],
            "duration_minutes": 210,
            "audience_tags": ["亲子"],
        },
    )

    assert response.status_code == 200
    assert response.json()["fallback_used"] is False
    assert response.json()["matched_template"]["name"] == "经典半日游"
    assert response.json()["summary"] == "覆盖核心文化景点的半日路线。"
    assert response.json()["spots"][0]["scenic_spot_id"] == spot_ids[0]


def test_generate_route_recommendation_falls_back_to_nearest_template(test_db_session, auth_headers) -> None:
    client = TestClient(app)
    scenic_area_id, _ = create_route_template_seed(client, auth_headers)

    response = client.post(
        "/api/route-recommendations/generate",
        headers=auth_headers,
        json={
            "scenic_area_id": scenic_area_id,
            "interest_tags": ["禅修"],
            "duration_minutes": 300,
            "audience_tags": ["老人"],
        },
    )

    assert response.status_code == 200
    assert response.json()["fallback_used"] is True
    assert response.json()["matched_template"]["name"] == "经典半日游"
    assert "时长" in response.json()["match_reason"]
