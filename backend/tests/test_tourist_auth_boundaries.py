from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.main import app
from app.models.conversation_session import ConversationSession
from app.models.scenic_area import ScenicArea
from app.models.scenic_spot import ScenicSpot
from app.models.visitor import Visitor
from app.services.intent_classifier import Intent


def _create_visitor(test_db_session, openid: str = "wx-auth-boundary") -> Visitor:
    visitor = Visitor(openid=openid, nickname="测试游客")
    test_db_session.add(visitor)
    test_db_session.commit()
    test_db_session.refresh(visitor)
    return visitor


def _visitor_headers(visitor: Visitor) -> dict[str, str]:
    token = create_access_token(f"visitor:{visitor.id}")
    return {"Authorization": f"Bearer {token}"}


def _seed_route_area(test_db_session) -> tuple[ScenicArea, ScenicSpot, ScenicSpot]:
    area = ScenicArea(code="AUTH-LS", name="灵山胜境", description="Demo", status="active")
    test_db_session.add(area)
    test_db_session.flush()
    first = ScenicSpot(
        scenic_area_id=area.id,
        spot_code="AUTH-1",
        name="灵山大照壁",
        latitude=31.421805,
        longitude=120.10463,
        open_status="open",
    )
    second = ScenicSpot(
        scenic_area_id=area.id,
        spot_code="AUTH-2",
        name="五印坛城",
        latitude=31.424856,
        longitude=120.103041,
        open_status="open",
    )
    test_db_session.add_all([first, second])
    test_db_session.commit()
    return area, first, second


def test_tourist_interaction_endpoints_require_visitor_token(test_db_session) -> None:
    area, first, second = _seed_route_area(test_db_session)
    client = TestClient(app)

    checks = [
        client.post("/api/tourist/chat", json={"message": "你好", "scenic_area_id": area.id}),
        client.post("/api/tourist/chat/stream", json={"message": "你好", "scenic_area_id": area.id}),
        client.get("/api/tourist/recent-records"),
        client.post(
            "/api/tourist/routes/recommend",
            json={"scenic_area_id": area.id, "duration_minutes": 120},
        ),
        client.post(
            "/api/tourist/routes/walk-guide",
            json={
                "scenic_area_id": area.id,
                "spots": [
                    {"scenic_spot_id": first.id, "name": first.name},
                    {"scenic_spot_id": second.id, "name": second.name},
                ],
            },
        ),
        client.post(
            "/api/tourist/feedback",
            json={"sentiment": "neutral", "score": 3, "content": "需要登录"},
        ),
    ]

    assert [response.status_code for response in checks] == [401, 401, 401, 401, 401, 401]


def test_tourist_chat_uses_authenticated_visitor_id_instead_of_payload(test_db_session) -> None:
    area, _, _ = _seed_route_area(test_db_session)
    visitor = _create_visitor(test_db_session)
    client = TestClient(app)
    mock_llm_result = MagicMock()
    mock_llm_result.text = "欢迎来到灵山胜境。"

    with patch("app.services.chat_service.IntentClassifier.classify", new_callable=AsyncMock, return_value=Intent.CHITCHAT):
        with patch("app.services.chat_service.RAGPipeline") as mock_rag:
            instance = mock_rag.return_value
            instance.answer = AsyncMock(return_value="欢迎来到灵山胜境。")
            instance.llm_client.generate = AsyncMock(return_value=mock_llm_result)

            response = client.post(
                "/api/tourist/chat",
                headers=_visitor_headers(visitor),
                json={"message": "你好", "scenic_area_id": area.id, "visitor_id": "spoofed-user"},
            )

    assert response.status_code == 200
    session = test_db_session.get(ConversationSession, response.json()["session_id"])
    assert session is not None
    assert session.visitor_id == str(visitor.id)


def test_recent_records_only_return_authenticated_visitor_sessions(test_db_session) -> None:
    visitor = _create_visitor(test_db_session)
    test_db_session.add_all(
        [
            ConversationSession(session_key="own-session", channel="miniprogram", visitor_id=str(visitor.id)),
            ConversationSession(session_key="other-session", channel="miniprogram", visitor_id="other-visitor"),
        ]
    )
    test_db_session.commit()

    response = TestClient(app).get("/api/tourist/recent-records", headers=_visitor_headers(visitor))

    assert response.status_code == 200
    data = response.json()
    assert [item["visitor_id"] for item in data["items"]] == [str(visitor.id)]
