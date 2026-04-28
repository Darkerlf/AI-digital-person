import jieba
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.faq_item import FAQItem
from app.models.knowledge_chunk import KnowledgeChunk
from app.services.embedding_service import EmbeddingService
from app.services.llm_client import LLMClient
from app.services.vector_store import VectorStore

SYSTEM_PROMPT = """你是灵山胜境景区的AI数字人导游。你的职责是为游客提供准确、友好的景区导览服务。

回答规则：
1. 只回答与灵山胜境景区相关的问题
2. 基于提供的参考资料回答，不要编造信息
3. 如果参考资料中没有相关信息，礼貌地告知游客
4. 回答要简洁、友好、易懂
5. 适当使用emoji让回答更生动"""


class RAGPipeline:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.llm_client = LLMClient()
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore(dimension=settings.embedding_dimension)
        self._loaded = False

    def _ensure_index_loaded(self) -> None:
        if self._loaded:
            return
        chunks = self.db.execute(
            select(KnowledgeChunk).where(
                KnowledgeChunk.status == "active",
                KnowledgeChunk.embedding_vector.isnot(None),
            )
        ).scalars().all()
        if chunks:
            vectors = []
            ids = []
            for chunk in chunks:
                vec = self.vector_store.bytes_to_vector(chunk.embedding_vector)
                vectors.append(vec)
                ids.append(chunk.id)
            self.vector_store.add(vectors, ids)
        self._loaded = True

    async def retrieve(self, query: str) -> list[dict]:
        self._ensure_index_loaded()
        query_vector = await self.embedding_service.embed_text(query)
        raw_results = self.vector_store.search(query_vector, top_k=settings.rag_top_k)

        chunks_map: dict[int, KnowledgeChunk] = {}
        if raw_results:
            chunk_ids = [r[0] for r in raw_results]
            chunks = self.db.execute(
                select(KnowledgeChunk).where(KnowledgeChunk.id.in_(chunk_ids))
            ).scalars().all()
            chunks_map = {c.id: c for c in chunks}

        results = []
        for chunk_id, score in raw_results:
            if score < settings.rag_score_threshold:
                continue
            chunk = chunks_map.get(chunk_id)
            if chunk:
                results.append({
                    "text": chunk.chunk_text,
                    "source": "document",
                    "title": f"文档片段#{chunk.chunk_index}",
                    "score": score,
                })

        faq_results = self._search_faqs(query)
        results.extend(faq_results)

        return results

    def _search_faqs(self, query: str) -> list[dict]:
        keywords = set(jieba.cut(query))
        keywords = {w for w in keywords if len(w) > 1}
        if not keywords:
            return []

        faqs = self.db.execute(
            select(FAQItem).where(FAQItem.status == "active")
        ).scalars().all()

        scored = []
        for faq in faqs:
            question_words = set(jieba.cut(faq.question))
            overlap = len(keywords & question_words)
            if overlap > 0:
                scored.append((faq, overlap))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [
            {
                "text": f"问：{faq.question}\n答：{faq.answer}",
                "source": "faq",
                "title": "FAQ",
                "score": min(0.95, 0.7 + count * 0.1),
            }
            for faq, count in scored[:3]
        ]

    def build_context(self, chunks: list[dict]) -> str:
        parts = []
        for i, chunk in enumerate(chunks, 1):
            parts.append(f"[{i}] ({chunk['source']}) {chunk['text']}")
        return "\n\n".join(parts)

    async def answer(self, question: str, history: list[dict[str, str]] | None = None) -> str:
        chunks = await self.retrieve(question)
        context = self.build_context(chunks) if chunks else None
        result = await self.llm_client.generate(
            system_prompt=SYSTEM_PROMPT,
            user_message=question,
            context=context,
            history=history,
        )
        return result.text

    async def answer_stream(self, question: str, history: list[dict[str, str]] | None = None):
        chunks = await self.retrieve(question)
        context = self.build_context(chunks) if chunks else None
        async for chunk in self.llm_client.generate_stream(
            system_prompt=SYSTEM_PROMPT,
            user_message=question,
            context=context,
            history=history,
        ):
            yield chunk
