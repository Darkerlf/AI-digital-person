from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.scenic_area import ScenicArea


class ScenicAreaRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_all(self) -> list[ScenicArea]:
        return self.db.execute(select(ScenicArea).order_by(ScenicArea.id.asc())).scalars().all()

    def get(self, area_id: int) -> ScenicArea | None:
        return self.db.get(ScenicArea, area_id)

    def create(self, **kwargs) -> ScenicArea:
        area = ScenicArea(**kwargs)
        self.db.add(area)
        self.db.commit()
        self.db.refresh(area)
        return area
