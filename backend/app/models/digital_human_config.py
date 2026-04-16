from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class DigitalHumanConfig(TimestampMixin, Base):
    __tablename__ = "digital_human_config"

    id: Mapped[int] = mapped_column(primary_key=True)
    scenic_area_id: Mapped[int | None] = mapped_column(ForeignKey("scenic_area.id"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    voice_style: Mapped[str | None] = mapped_column(String(100), nullable=True)
    welcome_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    default_mode: Mapped[str | None] = mapped_column(String(50), nullable=True)
    config_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active")
