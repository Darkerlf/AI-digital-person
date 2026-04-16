from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ScenicSpotTag(Base):
    __tablename__ = "scenic_spot_tag"

    id: Mapped[int] = mapped_column(primary_key=True)
    scenic_spot_id: Mapped[int] = mapped_column(ForeignKey("scenic_spot.id"), index=True)
    tag_name: Mapped[str] = mapped_column(String(50), index=True)

    scenic_spot = relationship("ScenicSpot", back_populates="tags")
