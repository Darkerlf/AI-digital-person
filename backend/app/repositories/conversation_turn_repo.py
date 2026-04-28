from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.conversation_turn import ConversationTurn


class ConversationTurnRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add_turn(self, **kwargs) -> ConversationTurn:
        turn = ConversationTurn(**kwargs)
        self.db.add(turn)
        self.db.flush()
        return turn

    def list_turns(self, session_id: int, limit: int = 20) -> list[ConversationTurn]:
        return self.db.execute(
            select(ConversationTurn)
            .where(ConversationTurn.session_id == session_id)
            .order_by(ConversationTurn.created_at.asc())
            .limit(limit)
        ).scalars().all()

    def get_recent_turns(self, session_id: int, limit: int = 10) -> list[ConversationTurn]:
        return self.db.execute(
            select(ConversationTurn)
            .where(ConversationTurn.session_id == session_id)
            .order_by(ConversationTurn.created_at.desc())
            .limit(limit)
        ).scalars().all()
