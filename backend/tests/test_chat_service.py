import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models import load_all_models
from app.models.digital_human_config import DigitalHumanConfig
from app.models.conversation_message import ConversationMessage
from app.models.faq_item import FAQItem
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
            with patch("app.services.chat_service.RouteRAGRecommendationService") as MockRoute:
                MockRoute.return_value.generate_answer = AsyncMock(return_value="经典灵山游览路线")
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


    @pytest.mark.asyncio
    async def test_identity_question_uses_active_digital_human_name(self, chat_db):
        from app.services.chat_service import ChatService

        chat_db.add(
            DigitalHumanConfig(
                scenic_area_id=1,
                name="\u7075\u7075",
                welcome_text="\u4f60\u597d\uff0c\u6211\u662f\u7075\u7075\u3002",
                status="active",
            )
        )
        chat_db.commit()

        service = ChatService(chat_db)
        with patch.object(service.rag_pipeline, "answer", new_callable=AsyncMock) as mock_answer:
            result = await service.handle_message(message="\u4f60\u662f\u8c01\uff1f", scenic_area_id=1)

        mock_answer.assert_not_called()
        assert "\u7075\u7075" in result.answer
        assert result.intent == "chitchat"

    @pytest.mark.asyncio
    async def test_identity_question_stream_uses_active_digital_human_name(self, chat_db):
        from app.services.chat_service import ChatService

        chat_db.add(
            DigitalHumanConfig(
                scenic_area_id=1,
                name="\u7075\u7075",
                welcome_text="\u4f60\u597d\uff0c\u6211\u662f\u7075\u7075\u3002",
                status="active",
            )
        )
        chat_db.commit()

        service = ChatService(chat_db)
        with patch.object(service.rag_pipeline, "answer_stream", side_effect=AssertionError("identity answer should not use RAG")):
            chunks = []
            async for chunk in service.handle_message_stream(message="\u4f60\u597d\uff0c\u4f60\u662f\u8c01", scenic_area_id=1):
                chunks.append(chunk)

        answer = "".join(chunk for chunk in chunks if not chunk.startswith("\n__meta__:"))
        assert "\u7075\u7075" in answer
        assert "\u6211\u662f\u7075\u5c71\u80dc\u5883\u7684AI\u6570\u5b57\u4eba\u5bfc\u6e38" not in answer


def test_handle_message_returns_exact_faq_without_rag_or_llm(chat_db):
    from app.services.chat_service import ChatService

    chat_db.add(
        FAQItem(
            scenic_area_id=1,
            question="\u95e8\u7968\u591a\u5c11\u94b1",
            answer="\u6210\u4eba\u7968\u53c2\u8003\u4ef7\u662f210\u5143\u3002",
            category="\u7968\u52a1",
            priority=100,
            status="active",
        )
    )
    chat_db.commit()

    async def run_test():
        service = ChatService(chat_db)
        with patch.object(service.intent_classifier, "classify", new_callable=AsyncMock, return_value=Intent.SCENIC_QA):
            with patch.object(
                service.rag_pipeline,
                "retrieve",
                new_callable=AsyncMock,
                side_effect=AssertionError("RAG should be skipped for exact FAQ hit"),
            ):
                return await service.handle_message(message="\u95e8\u7968\u591a\u5c11\u94b1", scenic_area_id=1)

    result = asyncio.run(run_test())

    assert result.intent == "scenic_qa"
    assert "210" in result.answer


def test_handle_message_persists_exact_faq_hit_as_resolved(chat_db):
    from app.services.chat_service import ChatService

    chat_db.add(
        FAQItem(
            scenic_area_id=1,
            question="\u95e8\u7968\u591a\u5c11\u94b1",
            answer="\u6210\u4eba\u7968\u53c2\u8003\u4ef7\u662f210\u5143\u3002",
            category="\u7968\u52a1",
            priority=100,
            status="active",
        )
    )
    chat_db.commit()

    async def run_test():
        service = ChatService(chat_db)
        with patch.object(service.intent_classifier, "classify", new_callable=AsyncMock, return_value=Intent.SCENIC_QA):
            return await service.handle_message(message="\u95e8\u7968\u591a\u5c11\u94b1", scenic_area_id=1)

    result = asyncio.run(run_test())
    message = chat_db.query(ConversationMessage).filter_by(session_id=result.session_id).one()

    assert message.matched_document_title == "FAQ"
    assert message.is_missed is False
    assert message.resolution_status == "resolved"


def test_handle_message_persists_rag_miss_as_pending(chat_db):
    from app.services.chat_service import ChatService

    async def run_test():
        service = ChatService(chat_db)
        with patch.object(service.intent_classifier, "classify", new_callable=AsyncMock, return_value=Intent.SCENIC_QA):
            with patch.object(service.rag_pipeline, "retrieve", new_callable=AsyncMock, return_value=[]):
                mock_llm_result = MagicMock()
                mock_llm_result.text = "\u6682\u65f6\u6ca1\u6709\u627e\u5230\u76f8\u5173\u8d44\u6599\u3002"
                with patch.object(service.rag_pipeline.llm_client, "generate", new_callable=AsyncMock, return_value=mock_llm_result):
                    return await service.handle_message(message="\u51b7\u95e8\u95ee\u9898", scenic_area_id=1)

    result = asyncio.run(run_test())
    message = chat_db.query(ConversationMessage).filter_by(session_id=result.session_id).one()

    assert message.matched_document_title is None
    assert message.is_missed is True
    assert message.resolution_status == "pending"


def test_handle_message_stream_persists_rag_hit_as_resolved(chat_db):
    from app.services.chat_service import ChatService

    async def run_test():
        service = ChatService(chat_db)
        mock_chunks = [
            {
                "text": "\u7075\u5c71\u5927\u4f5b\u662f\u666f\u533a\u5730\u6807\u3002",
                "source": "scenic_spot",
                "title": "\u7075\u5c71\u5927\u4f5b",
                "score": 0.95,
            }
        ]
        with patch.object(service.intent_classifier, "classify", new_callable=AsyncMock, return_value=Intent.SCENIC_QA):
            with patch.object(service.rag_pipeline, "retrieve", new_callable=AsyncMock, return_value=mock_chunks):
                with patch.object(
                    service.rag_pipeline.llm_client,
                    "generate_stream",
                    return_value=_async_chunks(["\u7075\u5c71\u5927\u4f5b", "\u503c\u5f97\u53c2\u89c2"]),
                ):
                    return [chunk async for chunk in service.handle_message_stream(message="\u4ecb\u7ecd\u7075\u5c71\u5927\u4f5b", scenic_area_id=1)]

    chunks = asyncio.run(run_test())
    meta = next(chunk for chunk in chunks if chunk.startswith("\n__meta__:"))
    message_id = __import__("json").loads(meta.removeprefix("\n__meta__:"))["message_id"]
    message = chat_db.get(ConversationMessage, message_id)

    assert message.matched_document_title == "\u7075\u5c71\u5927\u4f5b"
    assert message.is_missed is False
    assert message.resolution_status == "resolved"


async def _async_chunks(chunks: list[str]):
    for chunk in chunks:
        yield chunk
