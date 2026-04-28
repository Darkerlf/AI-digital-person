from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models import load_all_models
from app.models.scenic_area import ScenicArea
from app.services.intent_classifier import Intent


@pytest.fixture
def api_db():
    load_all_models()
    engine = create_engine(
        "sqlite://",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)()

    area = ScenicArea(code="LS", name="灵山胜境", description="test", status="active")
    session.add(area)
    session.commit()

    def override_get_db():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield session
    session.close()
    app.dependency_overrides.clear()


class TestTouristChatAPI:
    def test_chat_endpoint_returns_answer(self, api_db):
        client = TestClient(app)
        mock_chunks = [{"text": "灵山大佛高88米", "source": "faq", "title": "FAQ", "score": 1.0}]
        mock_llm_result = MagicMock()
        mock_llm_result.text = "灵山大佛高88米"

        with patch("app.services.chat_service.IntentClassifier.classify", new_callable=AsyncMock, return_value=Intent.SCENIC_QA):
            with patch("app.services.chat_service.RAGPipeline") as MockRAG:
                instance = MockRAG.return_value
                instance.retrieve = AsyncMock(return_value=mock_chunks)
                instance.build_context.return_value = "灵山大佛高88米"
                instance.llm_client.generate = AsyncMock(return_value=mock_llm_result)
                instance.answer = AsyncMock(return_value="灵山大佛高88米")

                response = client.post(
                    "/api/tourist/chat",
                    json={"message": "灵山大佛多高？", "scenic_area_id": 1},
                )
        assert response.status_code == 200
        data = response.json()
        assert "88" in data["answer"]
        assert data["intent"] == "scenic_qa"
        assert data["session_id"] is not None

    def test_chat_stream_endpoint_returns_sse(self, api_db):
        client = TestClient(app)

        with patch("app.services.chat_service.IntentClassifier.classify", new_callable=AsyncMock, return_value=Intent.SCENIC_QA):
            with patch("app.services.chat_service.RAGPipeline") as MockRAG:
                instance = MockRAG.return_value

                async def fake_stream(*args, **kwargs):
                    yield "你好"
                    yield "世界"

                instance.answer_stream = fake_stream

                with client.stream("POST", "/api/tourist/chat/stream", json={"message": "你好"}) as response:
                    assert response.status_code == 200
                    response.read()
                    content = response.text
                    assert "你好" in content
