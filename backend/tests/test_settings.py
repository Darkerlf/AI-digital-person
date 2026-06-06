from fastapi.testclient import TestClient

from app.core.security import hash_password
from app.main import app
from app.models.admin_user import AdminUser


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


def test_get_active_digital_human_prefers_scenic_area_config(test_db_session, auth_headers) -> None:
    client = TestClient(app)

    area_response = client.post(
        "/api/scenic-areas",
        headers=auth_headers,
        json={"code": "AREA-A", "name": "Area A", "status": "active"},
    )
    assert area_response.status_code == 201
    scenic_area_id = area_response.json()["id"]

    global_response = client.post(
        "/api/digital-humans",
        headers=auth_headers,
        json={
            "name": "Global Guide",
            "avatar_url": "https://example.com/global.png",
            "default_mode": "chat",
            "config_json": {"pose": "idle"},
            "status": "active",
        },
    )
    assert global_response.status_code == 201
    area_response = client.post(
        "/api/digital-humans",
        headers=auth_headers,
        json={
            "scenic_area_id": scenic_area_id,
            "name": "Area Guide",
            "avatar_url": "https://example.com/area.png",
            "default_mode": "guide",
            "config_json": {"pose": "welcome"},
            "status": "active",
        },
    )
    assert area_response.status_code == 201

    response = client.get(f"/api/digital-humans/active?scenic_area_id={scenic_area_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Area Guide"
    assert data["avatar_url"] == "https://example.com/area.png"
    assert data["default_mode"] == "guide"
    assert data["config_json"] == {"pose": "welcome"}


def test_inactive_admin_user_cannot_login(test_db_session) -> None:
    client = TestClient(app)
    test_db_session.add(
        AdminUser(
            username="disabled_admin",
            password_hash=hash_password("disabled123"),
            role="content_admin",
            status="inactive",
        )
    )
    test_db_session.commit()

    response = client.post(
        "/api/auth/login",
        json={"username": "disabled_admin", "password": "disabled123"},
    )

    assert response.status_code == 401


def test_inactive_admin_user_token_is_rejected(test_db_session) -> None:
    client = TestClient(app)
    user = AdminUser(
        username="session_admin",
        password_hash=hash_password("session123"),
        role="content_admin",
        status="active",
    )
    test_db_session.add(user)
    test_db_session.commit()

    login_response = client.post(
        "/api/auth/login",
        json={"username": "session_admin", "password": "session123"},
    )
    user.status = "inactive"
    test_db_session.commit()

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {login_response.json()['access_token']}"},
    )

    assert response.status_code == 401


def test_update_admin_user_role_status_and_hides_password_hash(test_db_session, auth_headers) -> None:
    client = TestClient(app)
    test_db_session.add(
        AdminUser(
            username="editor_admin",
            password_hash=hash_password("editor123"),
            role="content_admin",
            status="active",
        )
    )
    test_db_session.commit()
    user_id = test_db_session.query(AdminUser).filter_by(username="editor_admin").one().id

    response = client.put(
        f"/api/settings/admin-users/{user_id}",
        headers=auth_headers,
        json={"role": "ops_admin", "status": "inactive"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "editor_admin"
    assert data["role"] == "ops_admin"
    assert data["status"] == "inactive"
    assert "password_hash" not in data


def test_reset_admin_user_password(test_db_session, auth_headers) -> None:
    client = TestClient(app)
    test_db_session.add(
        AdminUser(
            username="reset_admin",
            password_hash=hash_password("oldpass123"),
            role="content_admin",
            status="active",
        )
    )
    test_db_session.commit()
    user_id = test_db_session.query(AdminUser).filter_by(username="reset_admin").one().id

    response = client.put(
        f"/api/settings/admin-users/{user_id}",
        headers=auth_headers,
        json={"password": "newpass123"},
    )

    assert response.status_code == 200
    assert client.post("/api/auth/login", json={"username": "reset_admin", "password": "oldpass123"}).status_code == 401
    assert client.post("/api/auth/login", json={"username": "reset_admin", "password": "newpass123"}).status_code == 200
