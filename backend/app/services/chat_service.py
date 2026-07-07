import json
import re
import time
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.conversation_message import ConversationMessage
from app.models.conversation_session import ConversationSession
from app.models.faq_item import FAQItem
from app.repositories.conversation_turn_repo import ConversationTurnRepository
from app.repositories.settings_repo import SettingsRepository
from app.schemas.chat import ChatResponse
from app.services.intent_classifier import Intent, IntentClassifier
from app.services.rag_pipeline import RAGPipeline, SYSTEM_PROMPT
from app.services.route_rag_recommendation_service import RouteRAGRecommendationService


IDENTITY_QUESTION_PATTERNS = (
    "你是谁",
    "你叫什么",
    "你叫什么名字",
    "你的名字",
    "介绍一下你自己",
    "自我介绍",
)


class ChatService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.intent_classifier = IntentClassifier()
        self.rag_pipeline = RAGPipeline(db)
        self.turn_repo = ConversationTurnRepository(db)

    def _get_or_create_session(
        self, session_id: int | None, scenic_area_id: int | None, visitor_id: str | None
    ) -> ConversationSession:
        if session_id:
            session = self.db.get(ConversationSession, session_id)
            if session:
                return session
        session_key = f"tourist_{uuid.uuid4().hex[:16]}"
        valid_area_id = None
        if scenic_area_id:
            from app.models.scenic_area import ScenicArea

            if self.db.get(ScenicArea, scenic_area_id):
                valid_area_id = scenic_area_id
        session = ConversationSession(
            scenic_area_id=valid_area_id,
            session_key=session_key,
            channel="miniprogram",
            visitor_id=visitor_id,
            status="active",
        )
        self.db.add(session)
        self.db.flush()
        return session

    def _build_history(self, session_id: int) -> list[dict[str, str]]:
        turns = self.turn_repo.get_recent_turns(session_id, limit=10)
        turns.reverse()
        history = []
        for turn in turns:
            role = "user" if turn.role == "user" else "assistant"
            history.append({"role": role, "content": turn.content})
        return history

    def _normalize_question(self, value: str) -> str:
        return re.sub(r"[\s，。！？、,.!?;；:：]+", "", value or "").lower()

    def _is_identity_question(self, message: str) -> bool:
        normalized = self._normalize_question(message)
        return any(pattern in normalized for pattern in IDENTITY_QUESTION_PATTERNS)

    def _get_digital_human_name(self, scenic_area_id: int | None) -> str:
        active_config = SettingsRepository(self.db).get_active_digital_human(scenic_area_id)
        name = (active_config.name if active_config else "") or "灵灵"
        return name.strip() or "灵灵"

    def _build_identity_answer(self, scenic_area_id: int | None) -> str:
        name = self._get_digital_human_name(scenic_area_id)
        return (
            f"你好，我是{name}，灵山胜境的 AI 导游。"
            "我可以为你介绍景点故事、推荐游览路线，也能帮你查询门票、服务点和游览注意事项。"
        )

    def _find_exact_faq_answer(self, message: str, scenic_area_id: int | None) -> str | None:
        normalized = self._normalize_question(message)
        if not normalized:
            return None

        query = select(FAQItem).where(FAQItem.status == "active")
        if scenic_area_id:
            query = query.where(FAQItem.scenic_area_id == scenic_area_id)
        faqs = self.db.execute(query.order_by(FAQItem.priority.desc(), FAQItem.id.asc())).scalars().all()
        for faq in faqs:
            if self._normalize_question(faq.question) == normalized:
                return faq.answer
        return None

    def _matched_document_title(self, sources: list[dict]) -> str | None:
        titles = []
        for source in sources:
            title = str(source.get("title") or "").strip()
            if title and title not in titles:
                titles.append(title)
        return "、".join(titles[:3]) if titles else None

    def _message_resolution_fields(self, intent: Intent, sources: list[dict]) -> dict[str, object]:
        is_missed = intent == Intent.SCENIC_QA and not sources
        return {
            "matched_document_title": self._matched_document_title(sources),
            "is_missed": is_missed,
            "resolution_status": "pending" if is_missed else "resolved",
        }

    async def handle_message(
        self,
        message: str,
        session_id: int | None = None,
        scenic_area_id: int | None = None,
        visitor_id: str | None = None,
    ) -> ChatResponse:
        start_time = time.time()
        session = self._get_or_create_session(session_id, scenic_area_id, visitor_id)
        intent = await self.intent_classifier.classify(message)

        self.turn_repo.add_turn(
            session_id=session.id,
            role="user",
            content=message,
            intent=intent.value,
        )

        history = self._build_history(session.id)

        if self._is_identity_question(message):
            answer = self._build_identity_answer(scenic_area_id or session.scenic_area_id)
            intent = Intent.CHITCHAT
            sources = []
        elif intent == Intent.ROUTE_RECOMMEND:
            route_service = RouteRAGRecommendationService(self.db)
            try:
                answer = await route_service.generate_answer(
                    message,
                    scenic_area_id=scenic_area_id or session.scenic_area_id,
                    history=history,
                )
            except Exception:
                answer = "抱歉，暂时无法为您推荐路线。您可以告诉我游览时长、同行人群和偏好，我再为您规划。"
            sources = []
        elif intent == Intent.CHITCHAT:
            answer = await self.rag_pipeline.answer(message, history=history)
            sources = []
        else:
            direct_answer = self._find_exact_faq_answer(message, scenic_area_id or session.scenic_area_id)
            if direct_answer:
                answer = direct_answer
                sources = [{"title": "FAQ", "source": "faq_exact"}]
            else:
                chunks = await self.rag_pipeline.retrieve(message)
                context = self.rag_pipeline.build_context(chunks) if chunks else None
                result = await self.rag_pipeline.llm_client.generate(
                    system_prompt=SYSTEM_PROMPT,
                    user_message=message,
                    context=context,
                    history=history,
                )
                answer = result.text
                sources = [{"title": c["title"], "source": c["source"]} for c in chunks]

        self.turn_repo.add_turn(
            session_id=session.id,
            role="assistant",
            content=answer,
            intent=intent.value,
        )

        latency_ms = int((time.time() - start_time) * 1000)
        msg = ConversationMessage(
            session_id=session.id,
            question_text=message,
            recognized_text=message,
            answer_text=answer,
            latency_ms=latency_ms,
            **self._message_resolution_fields(intent, sources),
        )
        self.db.add(msg)
        self.db.commit()

        return ChatResponse(
            session_id=session.id,
            answer=answer,
            intent=intent.value,
            sources=sources,
        )

    async def handle_message_stream(
        self,
        message: str,
        session_id: int | None = None,
        scenic_area_id: int | None = None,
        visitor_id: str | None = None,
    ):
        session = self._get_or_create_session(session_id, scenic_area_id, visitor_id)
        intent = await self.intent_classifier.classify(message)

        self.turn_repo.add_turn(
            session_id=session.id,
            role="user",
            content=message,
            intent=intent.value,
        )

        history = self._build_history(session.id)
        full_answer = ""

        if self._is_identity_question(message):
            intent = Intent.CHITCHAT
            full_answer = self._build_identity_answer(scenic_area_id or session.scenic_area_id)
            sources = []
            yield full_answer
        elif intent == Intent.ROUTE_RECOMMEND:
            route_service = RouteRAGRecommendationService(self.db)
            try:
                answer = await route_service.generate_answer(
                    message,
                    scenic_area_id=scenic_area_id or session.scenic_area_id,
                    history=history,
                )
            except Exception:
                answer = "抱歉，暂时无法为您推荐路线。"
            yield answer
            full_answer = answer
            sources = []
        elif intent == Intent.SCENIC_QA:
            direct_answer = self._find_exact_faq_answer(message, scenic_area_id or session.scenic_area_id)
            if direct_answer:
                sources = [{"title": "FAQ", "source": "faq_exact"}]
                yield direct_answer
                full_answer = direct_answer
            else:
                chunks = await self.rag_pipeline.retrieve(message)
                context = self.rag_pipeline.build_context(chunks) if chunks else None
                sources = [{"title": c["title"], "source": c["source"]} for c in chunks]
                async for chunk in self.rag_pipeline.llm_client.generate_stream(
                    system_prompt=SYSTEM_PROMPT,
                    user_message=message,
                    context=context,
                    history=history,
                ):
                    yield chunk
                    full_answer += chunk
        else:
            sources = []
            async for chunk in self.rag_pipeline.answer_stream(message, history=history):
                yield chunk
                full_answer += chunk

        self.turn_repo.add_turn(
            session_id=session.id,
            role="assistant",
            content=full_answer,
            intent=intent.value,
        )

        msg = ConversationMessage(
            session_id=session.id,
            question_text=message,
            recognized_text=message,
            answer_text=full_answer,
            **self._message_resolution_fields(intent, sources),
        )
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)

        yield f"\n__meta__:{json.dumps({'session_id': session.id, 'message_id': msg.id, 'intent': intent.value})}"
