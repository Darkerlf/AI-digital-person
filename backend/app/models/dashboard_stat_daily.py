from sqlalchemy import ForeignKey, Float, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class DashboardStatDaily(Base):
    __tablename__ = "dashboard_stat_daily"

    id: Mapped[int] = mapped_column(primary_key=True)
    stat_date: Mapped[str] = mapped_column(String(16), index=True)
    scenic_area_id: Mapped[int | None] = mapped_column(ForeignKey("scenic_area.id"), nullable=True, index=True)
    total_visitors: Mapped[int] = mapped_column(default=0)
    total_events: Mapped[int] = mapped_column(default=0)
    hot_spot_top_json: Mapped[list | dict | None] = mapped_column(JSON, nullable=True)
    hot_question_top_json: Mapped[list | dict | None] = mapped_column(JSON, nullable=True)
    route_usage_json: Mapped[list | dict | None] = mapped_column(JSON, nullable=True)
    satisfaction_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[str] = mapped_column(String(32))
