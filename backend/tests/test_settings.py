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
