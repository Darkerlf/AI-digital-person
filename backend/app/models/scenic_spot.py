from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
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
    latitude: Mapped[float | None] = mapped_column(Float(precision=53), nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float(precision=53), nullable=True)
    coordinate_source: Mapped[str | None] = mapped_column(String(50), nullable=True)
    coordinate_confidence: Mapped[int | None] = mapped_column(Integer, nullable=True)
    coordinate_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    tencent_poi_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    coordinate_address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    coordinate_raw_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    cover_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    guide_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_audience: Mapped[str | None] = mapped_column(String(255), nullable=True)
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
    route_template_spots = relationship("RouteTemplateSpot", back_populates="scenic_spot")
