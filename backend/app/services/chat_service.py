import json
import time
import uuid

from sqlalchemy.orm import Session

from app.models.conversation_message import ConversationMessage
from app.models.conversation_session import ConversationSession
from app.repositories.conversation_turn_repo import ConversationTurnRepository
from app.schemas.chat import ChatResponse
from app.schemas.route_template import RouteRecommendationRequest
from app.services.intent_classifier import Intent, IntentClassifier
from app.services.rag_pipeline import RAGPipeline, SYSTEM_PROMPT
from app.services.route_recommendation_service import RouteRecommendationService


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
        session = ConversationSession(
            scenic_area_id=scenic_area_id,
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

        if intent == Intent.ROUTE_RECOMMEND:
            route_service = RouteRecommendationService(self.db)
            try:
                req = RouteRecommendationRequest(
                    scenic_area_id=scenic_area_id or session.scenic_area_id,
                    duration_minutes=120,
                )
                recommendation = route_service.generate(req)
                template_name = recommendation.get("matched_template", {}).get("name", "经典路线")
                answer = f"为您推荐路线：{template_name}"
            except Exception:
                answer = "抱歉，暂时无法为您推荐路线，请告诉我您的偏好，我来帮您规划。"
            sources = []
        elif intent == Intent.CHITCHAT:
            answer = await self.rag_pipeline.answer(message, history=history)
            sources = []
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
            answer_text=answer,
            latency_ms=latency_ms,
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
        """Streaming version — yields text chunks, then final metadata."""
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

        if intent == Intent.ROUTE_RECOMMEND:
            route_service = RouteRecommendationService(self.db)
            try:
                req = RouteRecommendationRequest(
                    scenic_area_id=scenic_area_id or session.scenic_area_id,
                    duration_minutes=120,
                )
                recommendation = route_service.generate(req)
                template_name = recommendation.get("matched_template", {}).get("name", "经典路线")
                answer = f"为您推荐路线：{template_name}"
            except Exception:
                answer = "抱歉，暂时无法为您推荐路线。"
            yield answer
            full_answer = answer
        else:
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
            answer_text=full_answer,
        )
        self.db.add(msg)
        self.db.commit()

        yield f"\n__meta__:{json.dumps({'session_id': session.id, 'intent': intent.value})}"
