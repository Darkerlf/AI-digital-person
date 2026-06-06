from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.scenic_spot_tag import ScenicSpotTag
from app.repositories.scenic_spot_repo import ScenicSpotRepository
from app.schemas.scenic_spot import ScenicSpotCreate, ScenicSpotUpdate
from app.services.operation_log_service import record_operation_log


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
            "latitude": spot.latitude,
            "longitude": spot.longitude,
            "coordinate_source": spot.coordinate_source,
            "coordinate_confidence": spot.coordinate_confidence,
            "coordinate_verified": spot.coordinate_verified,
            "tencent_poi_id": spot.tencent_poi_id,
            "coordinate_address": spot.coordinate_address,
            "coordinate_raw_json": spot.coordinate_raw_json,
            "cover_image_url": spot.cover_image_url,
            "guide_text": spot.guide_text,
            "target_audience": spot.target_audience,
            "parameters_text": spot.parameters_text,
            "detail_intro": spot.detail_intro,
            "highlights": spot.highlights,
            "core_function": spot.core_function,
            "cultural_value": spot.cultural_value,
            "performance_info": spot.performance_info,
            "remarks": spot.remarks,
            "suggested_duration_minutes": spot.suggested_duration_minutes,
            "open_status": spot.open_status,
            "tags": [tag.tag_name for tag in spot.tags],
        }

    def create(self, payload: ScenicSpotCreate, current_user=None):
        spot = self.repo.create(**payload.model_dump())
        record_operation_log(
            self.db,
            module="scenic",
            action="create",
            target_type="scenic_spot",
            target_id=spot.id,
            detail={"spot_code": spot.spot_code, "name": spot.name},
            current_user=current_user,
        )
        return self._to_read_dict(spot)

    def list_all(self, keyword: str | None = None, open_status: str | None = None):
        return [self._to_read_dict(spot) for spot in self.repo.list_all(keyword=keyword, open_status=open_status)]

    def get(self, spot_id: int):
        spot = self.repo.get(spot_id)
        if spot is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenic spot not found")
        return spot

    def get_read(self, spot_id: int):
        return self._to_read_dict(self.get(spot_id))

    def update(self, spot_id: int, payload: ScenicSpotUpdate, current_user=None):
        spot = self.get(spot_id)
        values = payload.model_dump(exclude_unset=True)
        changed_fields = sorted(values.keys())
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
        record_operation_log(
            self.db,
            module="scenic",
            action="update",
            target_type="scenic_spot",
            target_id=spot.id,
            detail={"changed_fields": changed_fields},
            current_user=current_user,
        )
        return self._to_read_dict(spot)

    def delete(self, spot_id: int, current_user=None) -> None:
        spot = self.get(spot_id)
        detail = {"spot_code": spot.spot_code, "name": spot.name}
        self.db.delete(spot)
        self.db.commit()
        record_operation_log(
            self.db,
            module="scenic",
            action="delete",
            target_type="scenic_spot",
            target_id=spot_id,
            detail=detail,
            current_user=current_user,
        )
