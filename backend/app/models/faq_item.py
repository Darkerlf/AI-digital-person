from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class FAQItem(TimestampMixin, Base):
    __tablename__ = "faq_item"

    id: Mapped[int] = mapped_column(primary_key=True)
    scenic_area_id: Mapped[int] = mapped_column(ForeignKey("scenic_area.id"), index=True)
    question: Mapped[str] = mapped_column(String(500))
    answer: Mapped[str] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="active")
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)
