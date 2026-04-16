from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class ScenicSpot(TimestampMixin, Base):
    __tablename__ = "scenic_spot"

    id: Mapped[int] = mapped_column(primary_key=True)
    scenic_area_id: Mapped[int] = mapped_column(ForeignKey("scenic_area.id"), index=True)
    spot_code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    alias: Mapped[str | None] = mapped_column(String(255), nullable=True)
    location_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    parameters_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    core_function: Mapped[str | None] = mapped_column(Text, nullable=True)
    cultural_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    detail_intro: Mapped[str | None] = mapped_column(Text, nullable=True)
    highlights: Mapped[str | None] = mapped_column(Text, nullable=True)
    performance_info: Mapped[str | None] = mapped_column(Text, nullable=True)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggested_duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    open_status: Mapped[str] = mapped_column(String(20), default="open")

    scenic_area = relationship("ScenicArea", back_populates="spots")
    tags = relationship("ScenicSpotTag", back_populates="scenic_spot", cascade="all, delete-orphan")
