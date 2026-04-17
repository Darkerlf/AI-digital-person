from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models.conversation_message import ConversationMessage
from app.models.conversation_session import ConversationSession


class ConversationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_sessions(self) -> list[dict[str, object]]:
        message_count = func.count(ConversationMessage.id)
        unresolved_count = func.sum(case((ConversationMessage.resolution_status == "pending", 1), else_=0))
        rows = (
            self.db.query(
                ConversationSession.id,
                ConversationSession.session_key,
                ConversationSession.channel,
                ConversationSession.visitor_id,
                ConversationSession.status,
                ConversationSession.created_at,
                message_count.label("message_count"),
                unresolved_count.label("unresolved_count"),
            )
            .outerjoin(ConversationMessage, ConversationMessage.session_id == ConversationSession.id)
            .group_by(ConversationSession.id)
            .order_by(ConversationSession.id.desc())
            .all()
        )
        return [
            {
                "id": row.id,
                "session_key": row.session_key,
                "channel": row.channel,
                "visitor_id": row.visitor_id,
                "status": row.status,
                "created_at": row.created_at,
                "message_count": int(row.message_count or 0),
                "unresolved_count": int(row.unresolved_count or 0),
            }
            for row in rows
        ]

    def get_session(self, session_id: int) -> ConversationSession | None:
        return self.db.get(ConversationSession, session_id)

    def list_messages(self, session_id: int) -> list[ConversationMessage]:
        return (
            self.db.execute(
                select(ConversationMessage)
                .where(ConversationMessage.session_id == session_id)
                .order_by(ConversationMessage.id.asc())
            )
            .scalars()
            .all()
        )

    def list_unresolved_messages(self) -> list[dict[str, object]]:
        rows = (
            self.db.query(ConversationMessage, ConversationSession.session_key)
            .join(ConversationSession, ConversationSession.id == ConversationMessage.session_id)
            .filter(ConversationMessage.resolution_status == "pending")
            .order_by(ConversationMessage.id.desc())
            .all()
        )
        return [
            {
                "id": message.id,
                "session_id": message.session_id,
                "session_key": session_key,
                "question_text": message.question_text,
                "recognized_text": message.recognized_text,
                "feedback_status": message.feedback_status,
                "created_at": message.created_at,
                "resolution_status": message.resolution_status,
            }
            for message, session_key in rows
        ]

    def get_message(self, message_id: int) -> ConversationMessage | None:
        return self.db.get(ConversationMessage, message_id)
