import struct
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.models import load_all_models
from app.models.knowledge_chunk import KnowledgeChunk
from app.models.knowledge_document import KnowledgeDocument
from app.models.scenic_area import ScenicArea
from app.tasks.knowledge_embedder import embed_all_chunks, embed_document_chunks


@pytest.fixture
def embed_db():
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
        scenic_area_id=area.id, title="测试文档", doc_type="text",
        source_name="test.txt", content_text="测试内容", status="active", version=1,
    )
    session.add(doc)
    session.flush()

    chunk1 = KnowledgeChunk(
        document_id=doc.id, chunk_index=0, chunk_text="灵山大佛高88米",
        token_count=10, status="active",
    )
    chunk2 = KnowledgeChunk(
        document_id=doc.id, chunk_index=1, chunk_text="位于江苏省无锡市",
        token_count=8, status="active",
    )
    session.add_all([chunk1, chunk2])
    session.commit()

    yield session
    session.close()


class TestKnowledgeEmbedder:
    @pytest.mark.asyncio
    async def test_embed_document_chunks(self, embed_db):
        mock_vectors = [[0.1] * 1024, [0.2] * 1024]

        with patch("app.tasks.knowledge_embedder.EmbeddingService.embed_batch", new_callable=AsyncMock, return_value=mock_vectors):
            count = await embed_document_chunks(embed_db, document_id=1)

        assert count == 2
        chunks = embed_db.query(KnowledgeChunk).all()
        assert all(c.embedding_vector is not None for c in chunks)

    @pytest.mark.asyncio
    async def test_embed_all_chunks(self, embed_db):
        mock_vectors = [[0.1] * 1024, [0.2] * 1024]

        with patch("app.tasks.knowledge_embedder.EmbeddingService.embed_batch", new_callable=AsyncMock, return_value=mock_vectors):
            count = await embed_all_chunks(embed_db)

        assert count == 2

    @pytest.mark.asyncio
    async def test_embed_skips_already_embedded(self, embed_db):
        chunk = embed_db.query(KnowledgeChunk).first()
        chunk.embedding_vector = struct.pack("1024f", *([0.5] * 1024))
        embed_db.commit()

        mock_vectors = [[0.3] * 1024]

        with patch("app.tasks.knowledge_embedder.EmbeddingService.embed_batch", new_callable=AsyncMock, return_value=mock_vectors):
            count = await embed_all_chunks(embed_db)

        assert count == 1
