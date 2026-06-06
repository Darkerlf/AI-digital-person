from fastapi.testclient import TestClient

from app.main import app


def test_scenic_spot_update_writes_operation_log(test_db_session, auth_headers) -> None:
    client = TestClient(app)

    area_response = client.post(
        "/api/scenic-areas",
        headers=auth_headers,
        json={"code": "AUDIT", "name": "Audit Area", "description": "Audit seed", "status": "active"},
    )
    assert area_response.status_code == 201

    spot_response = client.post(
        "/api/scenic-spots",
        headers=auth_headers,
        json={
            "scenic_area_id": area_response.json()["id"],
            "spot_code": "AUDIT-001",
            "name": "Audit Spot",
            "open_status": "open",
            "tags": [],
        },
    )
    assert spot_response.status_code == 201

    update_response = client.put(
        f"/api/scenic-spots/{spot_response.json()['id']}",
        headers=auth_headers,
        json={"name": "Audit Spot Updated"},
    )
    assert update_response.status_code == 200

    logs_response = client.get("/api/operation-logs", headers=auth_headers)
    assert logs_response.status_code == 200
    logs = logs_response.json()["items"]

    assert logs[0]["module"] == "scenic"
    assert logs[0]["action"] == "update"
    assert logs[0]["target_type"] == "scenic_spot"
    assert logs[0]["target_id"] == spot_response.json()["id"]
    assert logs[0]["detail_json"]["changed_fields"] == ["name"]


def test_faq_create_writes_operation_log(test_db_session, auth_headers) -> None:
    client = TestClient(app)

    area_response = client.post(
        "/api/scenic-areas",
        headers=auth_headers,
        json={"code": "FAQAUD", "name": "FAQ Audit Area", "description": "Audit seed", "status": "active"},
    )
    assert area_response.status_code == 201

    faq_response = client.post(
        "/api/knowledge/faqs",
        headers=auth_headers,
        json={
            "scenic_area_id": area_response.json()["id"],
            "question": "Where is the visitor center?",
            "answer": "Near the main gate.",
            "category": "service",
            "priority": 3,
            "status": "active",
            "source": "manual",
        },
    )
    assert faq_response.status_code == 201

    logs_response = client.get("/api/operation-logs", headers=auth_headers)
    assert logs_response.status_code == 200
    logs = logs_response.json()["items"]

    assert logs[0]["module"] == "knowledge"
    assert logs[0]["action"] == "create"
    assert logs[0]["target_type"] == "faq"
    assert logs[0]["target_id"] == faq_response.json()["id"]
    assert logs[0]["detail_json"]["question"] == "Where is the visitor center?"
