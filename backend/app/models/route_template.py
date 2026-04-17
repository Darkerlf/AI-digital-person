from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class RouteTemplate(TimestampMixin, Base):
    __tablename__ = "route_template"

    id: Mapped[int] = mapped_column(primary_key=True)
    scenic_area_id: Mapped[int] = mapped_column(ForeignKey("scenic_area.id"), index=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    template_type: Mapped[str] = mapped_column(String(20), default="fixed")
    interest_tags_json: Mapped[str] = mapped_column(Text, default="[]")
    audience_tags_json: Mapped[str] = mapped_column(Text, default="[]")
    duration_min_minutes: Mapped[int] = mapped_column(Integer)
    duration_max_minutes: Mapped[int] = mapped_column(Integer)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active")
    priority: Mapped[int] = mapped_column(Integer, default=0)
    rule_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    scenic_area = relationship("ScenicArea", back_populates="route_templates")
    spots = relationship(
        "RouteTemplateSpot",
        back_populates="template",
        cascade="all, delete-orphan",
        order_by="RouteTemplateSpot.sort_order.asc()",
    )
