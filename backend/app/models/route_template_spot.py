from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class RouteTemplateSpot(TimestampMixin, Base):
    __tablename__ = "route_template_spot"

    id: Mapped[int] = mapped_column(primary_key=True)
    template_id: Mapped[int] = mapped_column(ForeignKey("route_template.id"), index=True)
    scenic_spot_id: Mapped[int] = mapped_column(ForeignKey("scenic_spot.id"), index=True)
    sort_order: Mapped[int] = mapped_column(Integer)
    stay_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    highlight: Mapped[str | None] = mapped_column(Text, nullable=True)

    template = relationship("RouteTemplate", back_populates="spots")
    scenic_spot = relationship("ScenicSpot", back_populates="route_template_spots")
