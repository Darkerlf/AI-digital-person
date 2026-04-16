from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class AIProviderConfig(TimestampMixin, Base):
    __tablename__ = "ai_provider_config"

    id: Mapped[int] = mapped_column(primary_key=True)
    provider_name: Mapped[str] = mapped_column(String(100), index=True)
    model_type: Mapped[str] = mapped_column(String(50), index=True)
    endpoint: Mapped[str | None] = mapped_column(String(500), nullable=True)
    api_key_masked: Mapped[str | None] = mapped_column(String(255), nullable=True)
    extra_config_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="inactive")
