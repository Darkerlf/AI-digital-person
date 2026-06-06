from sqlalchemy import Boolean, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class RouteRecommendationRecord(TimestampMixin, Base):
    __tablename__ = "route_recommendation_record"

    id: Mapped[int] = mapped_column(primary_key=True)
    scenic_area_id: Mapped[int | None] = mapped_column(ForeignKey("scenic_area.id"), nullable=True, index=True)
    visitor_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    session_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    source: Mapped[str] = mapped_column(String(50), default="route_template")
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    matched_template_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    matched_template_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    fallback_used: Mapped[bool] = mapped_column(Boolean, default=False)
    request_json: Mapped[dict] = mapped_column(JSON)
    response_json: Mapped[dict] = mapped_column(JSON)
