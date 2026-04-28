from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models import load_all_models
from app.models.scenic_area import ScenicArea
from app.services.intent_classifier import Intent


@pytest.fixture
def chat_db():
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


class TestChatService:
    @pytest.mark.asyncio
    async def test_handle_message_creates_session(self, chat_db):
        from app.services.chat_service import ChatService

        service = ChatService(chat_db)
        with patch.object(service.intent_classifier, "classify", new_callable=AsyncMock, return_value=Intent.SCENIC_QA):
            mock_chunks = [{"text": "灵山大佛高88米", "source": "faq", "title": "FAQ", "score": 1.0}]
            with patch.object(service.rag_pipeline, "retrieve", new_callable=AsyncMock, return_value=mock_chunks):
                mock_llm_result = MagicMock()
                mock_llm_result.text = "灵山大佛高88米"
                with patch.object(service.rag_pipeline.llm_client, "generate", new_callable=AsyncMock, return_value=mock_llm_result):
                    result = await service.handle_message(
                        message="灵山大佛多高？",
                        scenic_area_id=1,
                    )
        assert result.session_id is not None
        assert "88" in result.answer
        assert result.intent == "scenic_qa"

    @pytest.mark.asyncio
    async def test_handle_message_reuses_session(self, chat_db):
        from app.services.chat_service import ChatService

        service = ChatService(chat_db)
        mock_chunks = [{"text": "回答", "source": "faq", "title": "FAQ", "score": 1.0}]

        with patch.object(service.intent_classifier, "classify", new_callable=AsyncMock, return_value=Intent.SCENIC_QA):
            with patch.object(service.rag_pipeline, "retrieve", new_callable=AsyncMock, return_value=mock_chunks):
                mock_result1 = MagicMock()
                mock_result1.text = "回答1"
                with patch.object(service.rag_pipeline.llm_client, "generate", new_callable=AsyncMock, return_value=mock_result1):
                    r1 = await service.handle_message(message="问题1", scenic_area_id=1)

        with patch.object(service.intent_classifier, "classify", new_callable=AsyncMock, return_value=Intent.SCENIC_QA):
            with patch.object(service.rag_pipeline, "retrieve", new_callable=AsyncMock, return_value=mock_chunks):
                mock_result2 = MagicMock()
                mock_result2.text = "回答2"
                with patch.object(service.rag_pipeline.llm_client, "generate", new_callable=AsyncMock, return_value=mock_result2):
                    r2 = await service.handle_message(message="问题2", session_id=r1.session_id)

        assert r1.session_id == r2.session_id

    @pytest.mark.asyncio
    async def test_handle_route_recommend(self, chat_db):
        from app.services.chat_service import ChatService

        service = ChatService(chat_db)
        with patch.object(service.intent_classifier, "classify", new_callable=AsyncMock, return_value=Intent.ROUTE_RECOMMEND):
            with patch("app.services.chat_service.RouteRecommendationService") as MockRoute:
                MockRoute.return_value.generate.return_value = {
                    "matched_template": {"name": "经典路线"},
                    "summary": "经典灵山游览路线",
                    "spots": [],
                }
                result = await service.handle_message(message="推荐路线", scenic_area_id=1)
        assert result.intent == "route_recommend"

    @pytest.mark.asyncio
    async def test_handle_chitchat(self, chat_db):
        from app.services.chat_service import ChatService

        service = ChatService(chat_db)
        with patch.object(service.intent_classifier, "classify", new_callable=AsyncMock, return_value=Intent.CHITCHAT):
            with patch.object(service.rag_pipeline, "answer", new_callable=AsyncMock, return_value="你好！"):
                result = await service.handle_message(message="你好", scenic_area_id=1)
        assert result.intent == "chitchat"
