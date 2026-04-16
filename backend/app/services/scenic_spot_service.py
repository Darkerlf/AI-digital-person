from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.scenic_spot_tag import ScenicSpotTag
from app.repositories.scenic_spot_repo import ScenicSpotRepository
from app.schemas.scenic_spot import ScenicSpotCreate, ScenicSpotUpdate


class ScenicSpotService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ScenicSpotRepository(db)

    def _to_read_dict(self, spot) -> dict:
        return {
            "id": spot.id,
            "scenic_area_id": spot.scenic_area_id,
            "spot_code": spot.spot_code,
            "name": spot.name,
            "alias": spot.alias,
            "location_text": spot.location_text,
            "open_status": spot.open_status,
            "tags": [tag.tag_name for tag in spot.tags],
        }

    def create(self, payload: ScenicSpotCreate):
        spot = self.repo.create(**payload.model_dump())
        return self._to_read_dict(spot)

    def list_all(self):
        return [self._to_read_dict(spot) for spot in self.repo.list_all()]

    def get(self, spot_id: int):
        spot = self.repo.get(spot_id)
        if spot is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenic spot not found")
        return spot

    def get_read(self, spot_id: int):
        return self._to_read_dict(self.get(spot_id))

    def update(self, spot_id: int, payload: ScenicSpotUpdate):
        spot = self.get(spot_id)
        values = payload.model_dump(exclude_unset=True)
        tags = values.pop("tags", None)
        for key, value in values.items():
            setattr(spot, key, value)
        if tags is not None:
            for existing in list(spot.tags):
                self.db.delete(existing)
            self.db.flush()
            for tag_name in tags:
                self.db.add(ScenicSpotTag(scenic_spot_id=spot.id, tag_name=tag_name))
        self.db.commit()
        self.db.refresh(spot)
        return self._to_read_dict(spot)

    def delete(self, spot_id: int) -> None:
        spot = self.get(spot_id)
        self.db.delete(spot)
        self.db.commit()
