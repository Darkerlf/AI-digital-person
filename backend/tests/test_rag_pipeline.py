import asyncio
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
from app.models.scenic_spot import ScenicSpot
from app.services.rag_pipeline import RAGPipeline, SYSTEM_PROMPT
from app.services.route_rag_recommendation_service import ROUTE_SYSTEM_PROMPT


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

    spot = ScenicSpot(
        scenic_area_id=area.id,
        spot_code="LS-006",
        name="九龙灌浴",
        location_text="灵山胜境中轴线",
        detail_intro="大型音乐动态群雕。",
        highlights="莲花开合与九龙喷水",
        performance_info="每天10:00、11:30、14:00开放演出。",
        open_status="open",
    )
    session.add(spot)
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
    async def test_retrieve_includes_structured_scenic_spot_fields(self, rag_db):
        pipeline = RAGPipeline(rag_db)

        mock_embed = [0.1] * 1024
        with patch.object(pipeline.embedding_service, "embed_text", new_callable=AsyncMock, return_value=mock_embed):
            with patch.object(pipeline.vector_store, "search", return_value=[]):
                results = await pipeline.retrieve("九龙灌浴开放时间")

        spot_results = [r for r in results if r["source"] == "scenic_spot"]
        assert spot_results
        assert "每天10:00" in spot_results[0]["text"]

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

    def test_system_prompt_is_voice_friendly_guide_narration(self):
        assert "像一位真人导游" in SYSTEM_PROMPT
        assert "自然转场" in SYSTEM_PROMPT
        assert "不要使用emoji" in SYSTEM_PROMPT
        assert "Markdown" in SYSTEM_PROMPT

    def test_route_prompt_requires_connected_spoken_narration(self):
        assert "真人导览员" in ROUTE_SYSTEM_PROMPT
        assert "转场" in ROUTE_SYSTEM_PROMPT
        assert "语音播报" in ROUTE_SYSTEM_PROMPT


def test_retrieve_includes_structured_scenic_spot_fields_without_asyncio_plugin(rag_db):
    async def run_test():
        pipeline = RAGPipeline(rag_db)
        mock_embed = [0.1] * 1024
        with patch.object(pipeline.embedding_service, "embed_text", new_callable=AsyncMock, return_value=mock_embed):
            with patch.object(pipeline.vector_store, "search", return_value=[]):
                return await pipeline.retrieve("九龙灌浴开放时间")

    results = asyncio.run(run_test())
    spot_results = [r for r in results if r["source"] == "scenic_spot"]
    assert spot_results
    assert "每天10:00" in spot_results[0]["text"]


def test_retrieve_uses_keyword_match_for_unembedded_chunks(rag_db):
    doc = KnowledgeDocument(
        scenic_area_id=1,
        title="票务信息",
        doc_type="text",
        source_name="ticket.txt",
        content_text="门票信息",
        status="active",
        version=1,
    )
    rag_db.add(doc)
    rag_db.flush()
    rag_db.add(
        KnowledgeChunk(
            document_id=doc.id,
            chunk_index=0,
            chunk_text="门票信息：成人票参考价210元。",
            token_count=16,
            status="active",
            embedding_vector=None,
        )
    )
    rag_db.commit()

    async def run_test():
        pipeline = RAGPipeline(rag_db)
        mock_embed = [0.1] * 1024
        with patch.object(pipeline.embedding_service, "embed_text", new_callable=AsyncMock, return_value=mock_embed):
            with patch.object(pipeline.vector_store, "search", return_value=[]):
                return await pipeline.retrieve("门票多少钱")

    results = asyncio.run(run_test())
    keyword_results = [r for r in results if r["source"] == "document_keyword"]
    assert keyword_results
    assert "210元" in keyword_results[0]["text"]


def test_retrieve_falls_back_to_keyword_match_when_embedding_fails(rag_db):
    doc = KnowledgeDocument(
        scenic_area_id=1,
        title="票务信息",
        doc_type="text",
        source_name="ticket.txt",
        content_text="门票信息",
        status="active",
        version=1,
    )
    rag_db.add(doc)
    rag_db.flush()
    rag_db.add(
        KnowledgeChunk(
            document_id=doc.id,
            chunk_index=0,
            chunk_text="门票信息：成人票参考价210元。",
            token_count=16,
            status="active",
            embedding_vector=None,
        )
    )
    rag_db.commit()

    async def run_test():
        pipeline = RAGPipeline(rag_db)
        with patch.object(pipeline.embedding_service, "embed_text", new_callable=AsyncMock, side_effect=RuntimeError("offline")):
            return await pipeline.retrieve("门票多少钱")

    results = asyncio.run(run_test())
    assert any(r["source"] == "document_keyword" and "210元" in r["text"] for r in results)


def test_retrieve_skips_embedding_for_strong_keyword_answer(rag_db):
    doc = KnowledgeDocument(
        scenic_area_id=1,
        title="票务信息",
        doc_type="text",
        source_name="ticket.txt",
        content_text="门票信息",
        status="active",
        version=1,
    )
    rag_db.add(doc)
    rag_db.flush()
    rag_db.add(
        KnowledgeChunk(
            document_id=doc.id,
            chunk_index=0,
            chunk_text="门票信息：成人票参考价210元，儿童和老人以景区现场政策为准。",
            token_count=28,
            status="active",
            embedding_vector=None,
        )
    )
    rag_db.commit()

    async def run_test():
        pipeline = RAGPipeline(rag_db)
        mock_embed = AsyncMock(side_effect=AssertionError("Embedding should be skipped for strong keyword answers"))
        with patch.object(
            pipeline.embedding_service,
            "embed_text",
            mock_embed,
        ):
            results = await pipeline.retrieve("门票多少钱")
        mock_embed.assert_not_awaited()
        return results

    results = asyncio.run(run_test())

    assert any(r["source"] == "document_keyword" and "210元" in r["text"] for r in results)


def test_rag_pipeline_reuses_loaded_vector_store_across_instances(rag_db):
    from app.services.vector_store import VectorStore

    RAGPipeline.clear_shared_index_cache()
    vector_store = VectorStore(dimension=1024)
    rag_db.query(KnowledgeChunk).first().embedding_vector = vector_store.vector_to_bytes([0.1] * 1024)
    rag_db.commit()

    first = RAGPipeline(rag_db)
    second = RAGPipeline(rag_db)

    first._ensure_index_loaded()
    second._ensure_index_loaded()

    assert first.vector_store is second.vector_store
    assert first.vector_store.total == 1
