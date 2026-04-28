from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.knowledge_chunk import KnowledgeChunk
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore


async def embed_document_chunks(db: Session, document_id: int) -> int:
    chunks = db.execute(
        select(KnowledgeChunk).where(
            KnowledgeChunk.document_id == document_id,
            KnowledgeChunk.status == "active",
            KnowledgeChunk.embedding_vector.is_(None),
        ).order_by(KnowledgeChunk.chunk_index.asc())
    ).scalars().all()

    if not chunks:
        return 0

    embedding_service = EmbeddingService()
    vector_store = VectorStore()

    texts = [c.chunk_text for c in chunks]
    vectors = await embedding_service.embed_batch(texts)

    for chunk, vector in zip(chunks, vectors):
        chunk.embedding_vector = vector_store.vector_to_bytes(vector)

    db.commit()
    return len(chunks)


async def embed_all_chunks(db: Session) -> int:
    chunks = db.execute(
        select(KnowledgeChunk).where(
            KnowledgeChunk.status == "active",
            KnowledgeChunk.embedding_vector.is_(None),
        )
    ).scalars().all()

    if not chunks:
        return 0

    embedding_service = EmbeddingService()
    vector_store = VectorStore()

    batch_size = 10
    total = 0
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        texts = [c.chunk_text for c in batch]
        vectors = await embedding_service.embed_batch(texts)
        for chunk, vector in zip(batch, vectors):
            chunk.embedding_vector = vector_store.vector_to_bytes(vector)
        total += len(batch)

    db.commit()
    return total
