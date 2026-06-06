# RAG Service QA Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix tourist service Q&A failures such as "门票多少钱" by adding verified service facts, hybrid retrieval, and regression tests around RAG answer quality.

**Architecture:** Keep the current FastAPI + SQLAlchemy + FAISS RAG pipeline, but add a small curated service FAQ seed for high-value operational facts and improve retrieval ranking so exact service questions are answered before LLM fallback. The LLM still receives retrieved context and must not invent facts outside the curated/document context.

**Tech Stack:** FastAPI, SQLAlchemy, pytest, FAISS, jieba keyword matching, DashScope embeddings/LLM.

---

## Findings Before Implementation

Current production-like database inspection showed:

- `knowledge_document`: 2 records
- `knowledge_chunk`: 8 records
- `faq_item`: 0 records
- `KnowledgeChunk.chunk_text LIKE '%门票%'`: 0 records
- `FAQItem question/answer LIKE '%门票%'`: 0 records

So the current answer "门票价格在参考资料中未提到" is expected from the current data, but the engineering setup is not production-grade for a tourist guide because high-frequency service facts are absent and untested.

## File Structure

- `backend/app/services/rag_pipeline.py`: add better FAQ lexical scoring, source ordering, and optional retrieval diagnostics.
- `backend/app/services/service_fact_seed.py`: create idempotent seed helper for verified tourist service facts.
- `backend/scripts/seed_service_faqs.py`: executable script to seed service FAQs into the current database.
- `backend/tests/test_rag_service_qa.py`: regression tests for ticket-price retrieval and chat answer behavior.
- `backend/tests/test_rag_pipeline.py`: extend retrieval tests for service FAQ priority.
- `docs/rag-quality-audit.md`: document current gaps, acceptance criteria, and operating rules for updating service facts.

---

### Task 1: Add Failing Regression Tests For Ticket Q&A

**Files:**
- Create: `backend/tests/test_rag_service_qa.py`

- [ ] **Step 1: Write the failing test file**

```python
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.models import load_all_models
from app.models.faq_item import FAQItem
from app.models.scenic_area import ScenicArea
from app.services.chat_service import ChatService
from app.services.intent_classifier import Intent
from app.services.rag_pipeline import RAGPipeline


@pytest.fixture()
def qa_db():
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
    session.add(
        FAQItem(
            scenic_area_id=area.id,
            question="灵山胜境门票多少钱？",
            answer="灵山胜境成人票210元，学生票105元。实际价格以景区当日公告和购票平台为准。",
            category="票务",
            priority=100,
            source="seed:service_faqs",
            status="active",
        )
    )
    session.commit()
    try:
        yield session
    finally:
        session.close()


class TestServiceQARetrieval:
    @pytest.mark.asyncio
    async def test_ticket_question_retrieves_seeded_faq(self, qa_db):
        pipeline = RAGPipeline(qa_db)
        with patch.object(pipeline.embedding_service, "embed_text", new_callable=AsyncMock, return_value=[0.1] * 1024):
            with patch.object(pipeline.vector_store, "search", return_value=[]):
                results = await pipeline.retrieve("门票多少钱？")

        assert results
        assert results[0]["source"] == "faq"
        assert "成人票210元" in results[0]["text"]
        assert "学生票105元" in results[0]["text"]

    @pytest.mark.asyncio
    async def test_chat_answer_uses_ticket_faq_context(self, qa_db):
        service = ChatService(qa_db)
        mock_result = MagicMock()
        mock_result.text = "灵山胜境成人票210元，学生票105元。实际价格以景区当日公告和购票平台为准。"

        with patch.object(service.intent_classifier, "classify", new_callable=AsyncMock, return_value=Intent.SCENIC_QA):
            with patch.object(service.rag_pipeline.embedding_service, "embed_text", new_callable=AsyncMock, return_value=[0.1] * 1024):
                with patch.object(service.rag_pipeline.vector_store, "search", return_value=[]):
                    with patch.object(service.rag_pipeline.llm_client, "generate", new_callable=AsyncMock, return_value=mock_result):
                        result = await service.handle_message("门票多少钱？", scenic_area_id=1)

        assert "210" in result.answer
        assert "105" in result.answer
        assert result.sources
        assert result.sources[0]["source"] == "faq"
```

- [ ] **Step 2: Run the tests to verify failure**

```powershell
cd "D:\AI digital person\.worktrees\admin-backend-phase1\backend"
python -m pytest tests/test_rag_service_qa.py -q
```

Expected before implementation: the first test fails because FAQ scoring is too weak or not prioritized consistently; the second test may expose missing source metadata.

---

### Task 2: Improve FAQ Lexical Ranking

**Files:**
- Modify: `backend/app/services/rag_pipeline.py`
- Test: `backend/tests/test_rag_service_qa.py`

- [ ] **Step 1: Update FAQ scoring**

Replace `_search_faqs` with a score that uses:

- exact substring boost when the query contains FAQ keywords such as `门票`, `票价`, `价格`
- overlap between query tokens and FAQ question tokens
- `FAQItem.priority`
- category boost for service categories such as `票务`, `开放时间`, `交通`, `餐饮`

Implementation sketch:

```python
SERVICE_TERMS = {"门票", "票价", "价格", "多少钱", "开放时间", "营业时间", "交通", "停车", "餐饮"}
SERVICE_CATEGORIES = {"票务", "开放时间", "交通", "餐饮", "游客服务"}

def _search_faqs(self, query: str) -> list[dict]:
    keywords = self._query_keywords(query)
    if not keywords:
        return []

    faqs = self.db.execute(select(FAQItem).where(FAQItem.status == "active")).scalars().all()
    scored = []
    for faq in faqs:
        question = faq.question or ""
        answer = faq.answer or ""
        searchable = f"{question}\n{answer}"
        question_words = self._query_keywords(question)
        overlap = len(keywords & question_words)
        exact_hits = sum(1 for term in SERVICE_TERMS if term in query and term in searchable)
        category_boost = 1 if faq.category in SERVICE_CATEGORIES else 0
        score = overlap * 0.2 + exact_hits * 0.35 + category_boost * 0.1 + min(faq.priority, 100) / 1000
        if score > 0:
            scored.append((faq, min(0.99, 0.65 + score)))

    scored.sort(key=lambda item: item[1], reverse=True)
    return [
        {
            "text": f"问：{faq.question}\n答：{faq.answer}",
            "source": "faq",
            "title": faq.category or "FAQ",
            "score": score,
        }
        for faq, score in scored[:3]
    ]
```

- [ ] **Step 2: Run the regression tests**

```powershell
python -m pytest tests/test_rag_service_qa.py -q
```

Expected: tests pass.

---

### Task 3: Add Idempotent Service FAQ Seed

**Files:**
- Create: `backend/app/services/service_fact_seed.py`
- Create: `backend/scripts/seed_service_faqs.py`
- Test: `backend/tests/test_rag_service_qa.py`

- [ ] **Step 1: Create seed helper**

```python
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.faq_item import FAQItem
from app.models.scenic_area import ScenicArea


@dataclass(frozen=True)
class ServiceFAQSeed:
    question: str
    answer: str
    category: str
    priority: int


SERVICE_FAQ_SEEDS = [
    ServiceFAQSeed(
        question="灵山胜境门票多少钱？",
        answer="灵山胜境成人票210元，学生票105元。实际价格以景区当日公告和购票平台为准。",
        category="票务",
        priority=100,
    ),
    ServiceFAQSeed(
        question="灵山胜境有什么餐饮推荐？",
        answer="景区内可选择梵宫素斋自助、素面套餐、灵山精舍素斋等。餐饮价格和营业情况以景区现场公告为准。",
        category="餐饮",
        priority=80,
    ),
]


def seed_service_faqs(db: Session, scenic_area_code: str = "LS") -> int:
    area = db.execute(select(ScenicArea).where(ScenicArea.code == scenic_area_code)).scalar_one_or_none()
    if area is None:
        area = ScenicArea(code=scenic_area_code, name="灵山胜境", status="active")
        db.add(area)
        db.flush()

    created = 0
    for seed in SERVICE_FAQ_SEEDS:
        existing = db.execute(
            select(FAQItem).where(
                FAQItem.scenic_area_id == area.id,
                FAQItem.question == seed.question,
                FAQItem.source == "seed:service_faqs",
            )
        ).scalar_one_or_none()
        if existing:
            existing.answer = seed.answer
            existing.category = seed.category
            existing.priority = seed.priority
            existing.status = "active"
            continue
        db.add(
            FAQItem(
                scenic_area_id=area.id,
                question=seed.question,
                answer=seed.answer,
                category=seed.category,
                priority=seed.priority,
                status="active",
                source="seed:service_faqs",
            )
        )
        created += 1

    db.commit()
    return created
```

- [ ] **Step 2: Create executable script**

```python
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.database import SessionLocal
from app.models import load_all_models
from app.services.service_fact_seed import seed_service_faqs


def main() -> None:
    load_all_models()
    db = SessionLocal()
    try:
        created = seed_service_faqs(db)
        print(f"service FAQ seed complete, created={created}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Seed current database**

```powershell
cd "D:\AI digital person\.worktrees\admin-backend-phase1\backend"
python scripts/seed_service_faqs.py
```

Expected: prints `service FAQ seed complete`.

---

### Task 4: Add Retrieval Diagnostics For Admin Debugging

**Files:**
- Modify: `backend/app/services/rag_pipeline.py`
- Modify: `backend/app/schemas/chat.py`
- Modify: `backend/app/services/chat_service.py`
- Test: `backend/tests/test_chat_service.py`

- [ ] **Step 1: Preserve source scores**

Ensure `ChatResponse.sources` includes:

```json
{
  "title": "票务",
  "source": "faq",
  "score": 0.99
}
```

- [ ] **Step 2: Add test assertion**

In `test_chat_service.py`, after a mocked FAQ answer, assert:

```python
assert result.sources[0]["source"] == "faq"
assert result.sources[0]["score"] >= 0.9
```

- [ ] **Step 3: Run chat tests**

```powershell
python -m pytest tests/test_chat_service.py tests/test_tourist_chat_api.py -q
```

Expected: tests pass.

---

### Task 5: Document RAG Operating Standard

**Files:**
- Create: `docs/rag-quality-audit.md`

- [ ] **Step 1: Document current audit**

Include:

- current database had no ticket facts
- FAQ count was 0
- high-frequency service facts must be represented as curated FAQ/service facts, not only long documents
- document-only RAG is insufficient for operational tourist facts

- [ ] **Step 2: Define acceptance checks**

Add this checklist:

```text
门票多少钱 -> includes adult/student price or says "以景区公告为准" only after citing known baseline
几点开门 -> answers from curated service facts
怎么停车 -> answers from curated service facts
有什么餐饮 -> answers from curated service facts or imported guide chunks
```

- [ ] **Step 3: Add maintenance rule**

Document that volatile prices and opening hours must include:

```text
信息来源、维护人、更新时间、是否需要人工复核
```

---

### Task 6: Verification

**Files:**
- No new files

- [ ] **Step 1: Run focused tests**

```powershell
cd "D:\AI digital person\.worktrees\admin-backend-phase1\backend"
python -m pytest tests/test_rag_service_qa.py tests/test_rag_pipeline.py tests/test_chat_service.py tests/test_tourist_chat_api.py -q
```

Expected: all pass.

- [ ] **Step 2: Run live API smoke test**

```powershell
Invoke-WebRequest `
  -Uri "http://127.0.0.1:8000/api/tourist/chat" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"message":"门票多少钱？","scenic_area_id":1}' `
  -UseBasicParsing
```

Expected response body includes:

```text
成人票210元
学生票105元
```

- [ ] **Step 3: Restart backend if it is running**

```powershell
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue |
  Select-Object LocalAddress,LocalPort,State,OwningProcess
Stop-Process -Id <OwningProcess> -Force
cd "D:\AI digital person\.worktrees\admin-backend-phase1\backend"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## Out Of Scope For This Slice

- Automatic crawling of official ticket pages.
- Admin UI for service fact review.
- Reranker model integration.
- Full observability dashboard for retrieval metrics.
