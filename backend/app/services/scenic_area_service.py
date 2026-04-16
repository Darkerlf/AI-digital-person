from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.scenic_area_repo import ScenicAreaRepository
from app.schemas.scenic_area import ScenicAreaCreate, ScenicAreaUpdate


class ScenicAreaService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ScenicAreaRepository(db)

    def create(self, payload: ScenicAreaCreate):
        return self.repo.create(**payload.model_dump())

    def list_all(self):
        return self.repo.list_all()

    def get(self, area_id: int):
        area = self.repo.get(area_id)
        if area is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenic area not found")
        return area

    def update(self, area_id: int, payload: ScenicAreaUpdate):
        area = self.get(area_id)
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(area, key, value)
        self.db.commit()
        self.db.refresh(area)
        return area

    def delete(self, area_id: int) -> None:
        area = self.get(area_id)
        self.db.delete(area)
        self.db.commit()
