import jieba
from cachetools import TTLCache
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.faq_item import FAQItem
from app.models.knowledge_chunk import KnowledgeChunk
from app.models.scenic_spot import ScenicSpot
from app.services.embedding_service import EmbeddingService
from app.services.llm_client import LLMClient
from app.services.vector_store import VectorStore

SYSTEM_PROMPT = """你是灵山胜境景区的AI数字人导游。你的职责是像一位真人导游一样，基于资料为游客做准确、自然、有温度的讲解。

回答规则：
1. 只回答与灵山胜境景区相关的问题
2. 基于提供的参考资料回答，不要编造信息
3. 如果参考资料中没有相关信息，礼貌地告知游客
4. 先直接回应游客的问题，再用一两句自然讲解把景点、故事或游览建议串起来
5. 用口语化短句，像在游客身边边走边讲；避免照抄资料、避免堆砌参数
6. 段落之间要有承接关系，可以使用“从这里往前看”“接下来您会看到”“如果时间充裕”等自然转场
7. 适合语音播报：不要使用emoji、表格、Markdown标题或生硬编号
8. 普通问答控制在120到220字；需要路线或深度讲解时再适当展开"""


class RAGPipeline:
    _shared_vector_store: VectorStore | None = None
    _shared_embedding_chunk_ids: tuple[int, ...] | None = None

    def __init__(self, db: Session) -> None:
        self.db = db
        self.llm_client = LLMClient()
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore(dimension=settings.embedding_dimension)
        self._loaded = False
        self._faq_cache: TTLCache[str, list[dict]] = TTLCache(maxsize=256, ttl=300)

    @classmethod
    def clear_shared_index_cache(cls) -> None:
        cls._shared_vector_store = None
        cls._shared_embedding_chunk_ids = None

    def _ensure_index_loaded(self) -> None:
        if self._loaded:
            return
        chunk_ids = tuple(
            self.db.execute(
                select(KnowledgeChunk.id).where(
                    KnowledgeChunk.status == "active",
                    KnowledgeChunk.embedding_vector.isnot(None),
                )
            ).scalars().all()
        )
        if (
            self.__class__._shared_vector_store is not None
            and self.__class__._shared_embedding_chunk_ids == chunk_ids
        ):
            self.vector_store = self.__class__._shared_vector_store
            self._loaded = True
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
        self.__class__._shared_vector_store = self.vector_store
        self.__class__._shared_embedding_chunk_ids = chunk_ids
        self._loaded = True

    async def retrieve(self, query: str) -> list[dict]:
        fast_results = self._fast_local_results(query)
        if self._can_skip_vector_search(query, fast_results):
            fast_results.sort(key=lambda item: item["score"], reverse=True)
            return fast_results

        self._ensure_index_loaded()
        try:
            query_vector = await self.embedding_service.embed_text(query)
            raw_results = self.vector_store.search(query_vector, top_k=settings.rag_top_k)
        except Exception:
            raw_results = []

        chunks_map: dict[int, KnowledgeChunk] = {}
        vector_chunk_ids: set[int] = set()
        if raw_results:
            chunk_ids = [r[0] for r in raw_results]
            vector_chunk_ids = set(chunk_ids)
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

        existing_keys = {(item["source"], item["text"]) for item in results}
        for item in fast_results:
            key = (item["source"], item["text"])
            if key not in existing_keys:
                results.append(item)
                existing_keys.add(key)

        results.sort(key=lambda item: item["score"], reverse=True)
        return results

    def _fast_local_results(self, query: str, exclude_ids: set[int] | None = None) -> list[dict]:
        results = []
        results.extend(self._search_faqs(query))
        results.extend(self._search_knowledge_chunks_by_keywords(query, exclude_ids=exclude_ids))
        results.extend(self._search_scenic_spots(query))
        return results

    def _can_skip_vector_search(self, query: str, results: list[dict]) -> bool:
        if not results:
            return False
        normalized = query or ""
        fast_keywords = ("门票", "票价", "多少钱", "开放时间", "几点", "厕所", "卫生间", "停车", "餐厅", "游客中心")
        if not any(keyword in normalized for keyword in fast_keywords):
            return False
        return any(item["score"] >= 0.6 for item in results)

    def _query_keywords(self, query: str) -> set[str]:
        words = set(jieba.cut(query))
        return {w for w in words if len(w.strip()) > 1}

    def _search_faqs(self, query: str) -> list[dict]:
        keywords = self._query_keywords(query)
        if not keywords:
            return []

        cache_key = "|".join(sorted(keywords))
        cached = self._faq_cache.get(cache_key)
        if cached is not None:
            return cached

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
        result = [
            {
                "text": f"问：{faq.question}\n答：{faq.answer}",
                "source": "faq",
                "title": "FAQ",
                "score": min(0.95, 0.7 + count * 0.1),
            }
            for faq, count in scored[:3]
        ]

        self._faq_cache[cache_key] = result
        return result

    def _search_knowledge_chunks_by_keywords(self, query: str, exclude_ids: set[int] | None = None) -> list[dict]:
        keywords = self._query_keywords(query)
        if not keywords:
            return []
        exclude_ids = exclude_ids or set()
        chunks = self.db.execute(
            select(KnowledgeChunk).where(KnowledgeChunk.status == "active")
        ).scalars().all()

        scored = []
        for chunk in chunks:
            if chunk.id in exclude_ids:
                continue
            overlap = len([keyword for keyword in keywords if keyword in chunk.chunk_text])
            if overlap <= 0:
                continue
            score = min(0.88, 0.55 + overlap * 0.08)
            scored.append((chunk, score))

        scored.sort(key=lambda item: item[1], reverse=True)
        return [
            {
                "text": chunk.chunk_text,
                "source": "document_keyword",
                "title": f"文档片段#{chunk.chunk_index}",
                "score": score,
            }
            for chunk, score in scored[:3]
        ]

    def _search_scenic_spots(self, query: str) -> list[dict]:
        keywords = self._query_keywords(query)
        if not keywords:
            return []

        spots = self.db.execute(
            select(ScenicSpot).where(ScenicSpot.open_status == "open")
        ).scalars().all()

        scored = []
        for spot in spots:
            text = self._format_scenic_spot_text(spot)
            haystack = f"{spot.name}\n{spot.alias or ''}\n{text}"
            overlap = len([keyword for keyword in keywords if keyword in haystack])
            name_bonus = 2 if spot.name and spot.name in query else 0
            if overlap + name_bonus <= 0:
                continue
            score = min(0.94, 0.45 + overlap * 0.08 + name_bonus * 0.12)
            scored.append((spot, text, score))

        scored.sort(key=lambda item: item[2], reverse=True)
        return [
            {
                "text": text,
                "source": "scenic_spot",
                "title": spot.name,
                "score": score,
            }
            for spot, text, score in scored[:3]
        ]

    def _format_scenic_spot_text(self, spot: ScenicSpot) -> str:
        fields = [
            ("景点名称", spot.name),
            ("别名", spot.alias),
            ("具体位置", spot.location_text),
            ("建筑/景观参数", spot.parameters_text),
            ("核心功能", spot.core_function),
            ("文化内涵", spot.cultural_value),
            ("详细介绍", spot.detail_intro),
            ("游玩亮点", spot.highlights),
            ("演艺/开放信息", spot.performance_info),
            ("备注", spot.remarks),
        ]
        return "\n".join(f"{label}：{value}" for label, value in fields if value)

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
