from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.models.visitor import Visitor
from app.utils.object_storage import StoredObject


def test_wx_login_persists_wechat_user_profile(test_db_session) -> None:
    client = TestClient(app)
    response_payload = {"openid": "wx-openid-001", "session_key": "session-key-001"}

    with patch("app.services.visitor_service.httpx.AsyncClient") as mock_client:
        client_instance = MagicMock()
        client_instance.get = AsyncMock(return_value=MagicMock(json=lambda: response_payload))
        mock_client.return_value.__aenter__.return_value = client_instance

        response = client.post(
            "/api/tourist/wx-login",
            json={
                "code": "wx-code-001",
                "user_info": {
                    "nickName": "灵山游客",
                    "avatarUrl": "https://example.test/avatar.png",
                },
            },
        )

    assert response.status_code == 200
    assert response.json()["nickname"] == "灵山游客"
    assert response.json()["avatar_url"] == "https://example.test/avatar.png"

    visitor = test_db_session.query(Visitor).filter(Visitor.openid == "wx-openid-001").one()
    assert visitor.session_key == "session-key-001"
    assert visitor.nickname == "灵山游客"
    assert visitor.avatar_url == "https://example.test/avatar.png"


def test_wx_login_updates_existing_profile_from_wechat_user_info(test_db_session) -> None:
    visitor = Visitor(
        openid="wx-openid-002",
        session_key="old-session-key",
        nickname="旧昵称",
        avatar_url="https://example.test/old.png",
    )
    test_db_session.add(visitor)
    test_db_session.commit()

    client = TestClient(app)
    response_payload = {"openid": "wx-openid-002", "session_key": "new-session-key"}

    with patch("app.services.visitor_service.httpx.AsyncClient") as mock_client:
        client_instance = MagicMock()
        client_instance.get = AsyncMock(return_value=MagicMock(json=lambda: response_payload))
        mock_client.return_value.__aenter__.return_value = client_instance

        response = client.post(
            "/api/tourist/wx-login",
            json={
                "code": "wx-code-002",
                "user_info": {
                    "nickName": "新昵称",
                    "avatarUrl": "https://example.test/new.png",
                },
            },
        )

    assert response.status_code == 200
    assert response.json()["visitor_id"] == visitor.id

    test_db_session.refresh(visitor)
    assert visitor.session_key == "new-session-key"
    assert visitor.nickname == "新昵称"
    assert visitor.avatar_url == "https://example.test/new.png"


def test_wx_login_uses_jscode2session_and_returns_blank_profile_without_user_info(test_db_session) -> None:
    client = TestClient(app)
    response_payload = {"openid": "wx-openid-003", "session_key": "session-key-003"}

    with patch("app.services.visitor_service.httpx.AsyncClient") as mock_client:
        client_instance = MagicMock()
        client_instance.get = AsyncMock(return_value=MagicMock(json=lambda: response_payload))
        mock_client.return_value.__aenter__.return_value = client_instance

        response = client.post("/api/tourist/wx-login", json={"code": "wx-code-003"})

    assert response.status_code == 200
    assert response.json()["nickname"] == ""
    assert response.json()["avatar_url"] == ""
    client_instance.get.assert_awaited_once()
    _, kwargs = client_instance.get.await_args
    assert kwargs["params"]["js_code"] == "wx-code-003"
    assert kwargs["params"]["grant_type"] == "authorization_code"

    visitor = test_db_session.query(Visitor).filter(Visitor.openid == "wx-openid-003").one()
    assert visitor.session_key == "session-key-003"
    assert visitor.nickname is None


def test_upload_avatar_persists_oss_url_for_authenticated_visitor(test_db_session, monkeypatch) -> None:
    visitor = Visitor(openid="wx-avatar-upload", nickname="visitor")
    test_db_session.add(visitor)
    test_db_session.commit()
    test_db_session.refresh(visitor)

    class FakeStorage:
        is_enabled = True

        def upload_bytes(self, data: bytes, *, filename: str, prefix: str, content_type: str | None = None):
            assert data == b"fake-jpeg"
            assert filename == "avatar.jpeg"
            assert prefix == "visitor-avatars"
            assert content_type == "image/jpeg"
            return StoredObject(
                key="scenic-guide/visitor-avatars/avatar.jpeg",
                url="https://digital-person-ai.oss-cn-beijing.aliyuncs.com/scenic-guide/visitor-avatars/avatar.jpeg",
            )

    monkeypatch.setattr("app.api.routers.visitor_auth.get_object_storage", lambda: FakeStorage())

    from app.core.security import create_access_token

    token = create_access_token(f"visitor:{visitor.id}")
    with TestClient(app) as client:
        response = client.post(
            "/api/tourist/profile/avatar",
            headers={"Authorization": f"Bearer {token}"},
            files={"avatar": ("avatar.jpeg", b"fake-jpeg", "image/jpeg")},
        )

    assert response.status_code == 200
    assert response.json()["avatar_url"].startswith("https://digital-person-ai.oss-cn-beijing.aliyuncs.com/")
    test_db_session.refresh(visitor)
    assert response.json()["avatar_url"] == visitor.avatar_url


def test_upload_avatar_rejects_invalid_content_type(test_db_session) -> None:
    visitor = Visitor(openid="wx-avatar-invalid-type")
    test_db_session.add(visitor)
    test_db_session.commit()
    test_db_session.refresh(visitor)

    from app.core.security import create_access_token

    token = create_access_token(f"visitor:{visitor.id}")
    with TestClient(app) as client:
        response = client.post(
            "/api/tourist/profile/avatar",
            headers={"Authorization": f"Bearer {token}"},
            files={"avatar": ("avatar.gif", b"fake-gif", "image/gif")},
        )

    assert response.status_code == 400


def test_upload_avatar_rejects_file_larger_than_two_mib(test_db_session) -> None:
    visitor = Visitor(openid="wx-avatar-too-large")
    test_db_session.add(visitor)
    test_db_session.commit()
    test_db_session.refresh(visitor)

    from app.core.security import create_access_token

    token = create_access_token(f"visitor:{visitor.id}")
    with TestClient(app) as client:
        response = client.post(
            "/api/tourist/profile/avatar",
            headers={"Authorization": f"Bearer {token}"},
            files={"avatar": ("avatar.png", b"x" * (2 * 1024 * 1024 + 1), "image/png")},
        )

    assert response.status_code == 400


def test_upload_avatar_rejects_disabled_oss(test_db_session, monkeypatch) -> None:
    visitor = Visitor(openid="wx-avatar-disabled-oss")
    test_db_session.add(visitor)
    test_db_session.commit()
    test_db_session.refresh(visitor)

    class DisabledStorage:
        is_enabled = False

    monkeypatch.setattr("app.api.routers.visitor_auth.get_object_storage", lambda: DisabledStorage())

    from app.core.security import create_access_token

    token = create_access_token(f"visitor:{visitor.id}")
    with TestClient(app) as client:
        response = client.post(
            "/api/tourist/profile/avatar",
            headers={"Authorization": f"Bearer {token}"},
            files={"avatar": ("avatar.png", b"fake-png", "image/png")},
        )

    assert response.status_code == 503


def test_upload_avatar_requires_authentication() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/tourist/profile/avatar",
            files={"avatar": ("avatar.png", b"fake-png", "image/png")},
        )

    assert response.status_code == 401


def test_update_profile_rejects_temporary_avatar_url(test_db_session) -> None:
    visitor = Visitor(openid="wx-profile-temp-avatar")
    test_db_session.add(visitor)
    test_db_session.commit()
    test_db_session.refresh(visitor)

    from app.core.security import create_access_token

    token = create_access_token(f"visitor:{visitor.id}")
    with TestClient(app) as client:
        response = client.put(
            "/api/tourist/profile",
            headers={"Authorization": f"Bearer {token}"},
            json={"avatar_url": "http://tmp/expired-avatar.jpeg"},
        )

    assert response.status_code == 400
    test_db_session.refresh(visitor)
    assert visitor.avatar_url is None
