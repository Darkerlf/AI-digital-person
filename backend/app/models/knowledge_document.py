from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class KnowledgeDocument(TimestampMixin, Base):
    __tablename__ = "knowledge_document"

    id: Mapped[int] = mapped_column(primary_key=True)
    scenic_area_id: Mapped[int] = mapped_column(ForeignKey("scenic_area.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    doc_type: Mapped[str] = mapped_column(String(32))
    source_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_name: Mapped[str] = mapped_column(String(255))
    content_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active")
    version: Mapped[int] = mapped_column(default=1)
    imported_at: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_by: Mapped[int | None] = mapped_column(nullable=True)
