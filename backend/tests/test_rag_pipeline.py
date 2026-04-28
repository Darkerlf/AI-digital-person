from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models import load_all_models
from app.models.faq_item import FAQItem
from app.models.knowledge_chunk import KnowledgeChunk
from app.models.knowledge_document import KnowledgeDocument
from app.models.scenic_area import ScenicArea
from app.services.rag_pipeline import RAGPipeline


@pytest.fixture
def rag_db():
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
    session.flush()

    doc = KnowledgeDocument(
        scenic_area_id=area.id, title="灵山大佛介绍", doc_type="text",
        source_name="灵山大佛介绍.txt",
        content_text="灵山大佛是世界上最高的青铜佛像", status="active", version=1,
    )
    session.add(doc)
    session.flush()

    chunk = KnowledgeChunk(
        document_id=doc.id, chunk_index=0,
        chunk_text="灵山大佛高88米，位于江苏省无锡市滨湖区马山灵山路",
        token_count=30, status="active",
    )
    session.add(chunk)

    faq = FAQItem(
        scenic_area_id=area.id, question="灵山大佛多高？",
        answer="灵山大佛高88米", category="景点", priority=10, status="active",
    )
    session.add(faq)
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


class TestRAGPipeline:
    @pytest.mark.asyncio
    async def test_retrieve_finds_relevant_chunks(self, rag_db):
        pipeline = RAGPipeline(rag_db)

        mock_embed = [0.1] * 1024
        with patch.object(pipeline.embedding_service, "embed_text", new_callable=AsyncMock, return_value=mock_embed):
            with patch.object(pipeline.vector_store, "search", return_value=[(1, 0.95)]):
                results = await pipeline.retrieve("灵山大佛多高")
        assert len(results) > 0
        assert any("灵山大佛" in r["text"] for r in results)

    @pytest.mark.asyncio
    async def test_retrieve_includes_faqs(self, rag_db):
        pipeline = RAGPipeline(rag_db)

        mock_embed = [0.1] * 1024
        with patch.object(pipeline.embedding_service, "embed_text", new_callable=AsyncMock, return_value=mock_embed):
            with patch.object(pipeline.vector_store, "search", return_value=[]):
                results = await pipeline.retrieve("灵山大佛多高")
        faq_results = [r for r in results if r["source"] == "faq"]
        assert len(faq_results) > 0

    @pytest.mark.asyncio
    async def test_generate_returns_answer(self, rag_db):
        pipeline = RAGPipeline(rag_db)

        mock_context = [{"text": "灵山大佛高88米", "source": "faq", "title": "FAQ", "score": 1.0}]
        mock_llm_result = MagicMock()
        mock_llm_result.text = "灵山大佛高88米"

        with patch.object(pipeline, "retrieve", new_callable=AsyncMock, return_value=mock_context):
            with patch.object(pipeline.llm_client, "generate", new_callable=AsyncMock, return_value=mock_llm_result):
                answer = await pipeline.answer("灵山大佛多高？")
        assert "88" in answer

    @pytest.mark.asyncio
    async def test_build_context_formats_chunks(self, rag_db):
        pipeline = RAGPipeline(rag_db)
        chunks = [
            {"text": "片段1", "source": "document", "title": "文档A", "score": 0.9},
            {"text": "片段2", "source": "faq", "title": "FAQ", "score": 0.8},
        ]
        context = pipeline.build_context(chunks)
        assert "片段1" in context
        assert "片段2" in context
