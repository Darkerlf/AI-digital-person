from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ImportJobItem(Base):
    __tablename__ = "import_job_item"

    id: Mapped[int] = mapped_column(primary_key=True)
    import_job_id: Mapped[int] = mapped_column(ForeignKey("import_job.id"), index=True)
    item_type: Mapped[str] = mapped_column(String(50))
    raw_payload_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    target_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    target_id: Mapped[int | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
