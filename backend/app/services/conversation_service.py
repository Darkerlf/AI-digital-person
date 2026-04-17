from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.conversation_repo import ConversationRepository
from app.schemas.conversation import ResolveConversationMessageRequest


class ConversationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ConversationRepository(db)

    def list_sessions(self) -> list[dict[str, object]]:
        return self.repo.list_sessions()

    def get_session_detail(self, session_id: int) -> dict[str, object]:
        session = self.repo.get_session(session_id)
        if session is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        return {
            "id": session.id,
            "session_key": session.session_key,
            "channel": session.channel,
            "visitor_id": session.visitor_id,
            "status": session.status,
            "created_at": session.created_at,
            "messages": self.repo.list_messages(session_id),
        }

    def list_unresolved_messages(self) -> list[dict[str, object]]:
        return self.repo.list_unresolved_messages()

    def resolve_message(self, message_id: int, payload: ResolveConversationMessageRequest):
        message = self.repo.get_message(message_id)
        if message is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation message not found")
        message.resolution_status = "resolved"
        message.resolution_note = payload.resolution_note
        self.db.commit()
        self.db.refresh(message)
        return message
