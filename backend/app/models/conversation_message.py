from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class ConversationMessage(TimestampMixin, Base):
    __tablename__ = "conversation_message"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("conversation_session.id"), index=True)
    question_text: Mapped[str] = mapped_column(Text)
    recognized_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    answer_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    matched_document_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    feedback_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_missed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    resolution_status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    resolution_note: Mapped[str | None] = mapped_column(Text, nullable=True)
