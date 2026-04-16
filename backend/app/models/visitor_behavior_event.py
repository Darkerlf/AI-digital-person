from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class VisitorBehaviorEvent(TimestampMixin, Base):
    __tablename__ = "visitor_behavior_event"

    id: Mapped[int] = mapped_column(primary_key=True)
    scenic_area_id: Mapped[int | None] = mapped_column(ForeignKey("scenic_area.id"), nullable=True, index=True)
    event_time: Mapped[str] = mapped_column(String(32), index=True)
    visitor_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    session_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    event_type: Mapped[str] = mapped_column(String(100), index=True)
    event_value: Mapped[str | None] = mapped_column(String(255), nullable=True)
    spot_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    route_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    raw_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
