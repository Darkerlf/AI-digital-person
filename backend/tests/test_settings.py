from fastapi.testclient import TestClient

from app.main import app


def test_create_ai_provider_config(test_db_session, auth_headers) -> None:
    client = TestClient(app)

    response = client.post(
        "/api/settings/ai-providers",
        headers=auth_headers,
        json={
            "provider_name": "qwen",
            "model_type": "chat",
            "endpoint": "https://example.com",
            "api_key_masked": "****abcd",
            "status": "active",
        },
    )

    assert response.status_code == 201
    assert response.json()["provider_name"] == "qwen"


def test_create_digital_human_writes_operation_log(test_db_session, auth_headers) -> None:
    client = TestClient(app)

    create_response = client.post(
        "/api/digital-humans",
        headers=auth_headers,
        json={
            "name": "灵山小导",
            "voice_style": "warm",
            "welcome_text": "欢迎来到灵山胜境",
            "default_mode": "guide",
            "status": "active",
        },
    )

    assert create_response.status_code == 201
    assert create_response.json()["name"] == "灵山小导"

    log_response = client.get("/api/operation-logs", headers=auth_headers)

    assert log_response.status_code == 200
    assert log_response.json()["items"][0]["module"] == "digital_humans"
    assert log_response.json()["items"][0]["action"] == "create_digital_human"
