from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class KnowledgeCorrectionTask(TimestampMixin, Base):
    __tablename__ = "knowledge_correction_task"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_message_id: Mapped[int] = mapped_column(ForeignKey("conversation_message.id"), index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("conversation_session.id"), index=True)
    scenic_area_id: Mapped[int | None] = mapped_column(ForeignKey("scenic_area.id"), nullable=True, index=True)
    question_text: Mapped[str] = mapped_column(Text)
    recognized_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    feedback_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    correction_type: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="open")
    resolution_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    linked_faq_id: Mapped[int | None] = mapped_column(ForeignKey("faq_item.id"), nullable=True)
    linked_document_id: Mapped[int | None] = mapped_column(ForeignKey("knowledge_document.id"), nullable=True)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("admin_user.id"), nullable=True)
    resolved_by: Mapped[int | None] = mapped_column(ForeignKey("admin_user.id"), nullable=True)
