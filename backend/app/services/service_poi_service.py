from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.service_poi_repo import ServicePOIRepository
from app.schemas.service_poi import ServicePOICreate, ServicePOIUpdate
from app.services.operation_log_service import record_operation_log


class ServicePOIService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ServicePOIRepository(db)

    @staticmethod
    def _to_read_dict(poi) -> dict:
        return {
            "id": poi.id,
            "scenic_area_id": poi.scenic_area_id,
            "name": poi.name,
            "category": poi.category,
            "area_text": poi.area_text,
            "description": poi.description,
            "open_hours": poi.open_hours,
            "latitude": poi.latitude,
            "longitude": poi.longitude,
            "status": poi.status,
        }

    def list_all(self, category: str | None = None, scenic_area_id: int | None = None) -> list[dict]:
        return [self._to_read_dict(poi) for poi in self.repo.list_all(category, scenic_area_id)]

    def create(self, payload: ServicePOICreate, current_user=None) -> dict:
        poi = self.repo.create(**payload.model_dump())
        record_operation_log(
            self.db,
            module="service",
            action="create",
            target_type="service_poi",
            target_id=poi.id,
            detail={"name": poi.name, "category": poi.category},
            current_user=current_user,
        )
        return self._to_read_dict(poi)

    def get(self, poi_id: int):
        poi = self.repo.get(poi_id)
        if poi is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service POI not found")
        return poi

    def get_read(self, poi_id: int) -> dict:
        return self._to_read_dict(self.get(poi_id))

    def update(self, poi_id: int, payload: ServicePOIUpdate, current_user=None) -> dict:
        poi = self.get(poi_id)
        values = payload.model_dump(exclude_unset=True)
        for key, value in values.items():
            setattr(poi, key, value)
        self.db.commit()
        self.db.refresh(poi)
        record_operation_log(
            self.db,
            module="service",
            action="update",
            target_type="service_poi",
            target_id=poi.id,
            detail={"changed_fields": sorted(values.keys())},
            current_user=current_user,
        )
        return self._to_read_dict(poi)

    def delete(self, poi_id: int, current_user=None) -> None:
        poi = self.get(poi_id)
        detail = {"name": poi.name, "category": poi.category}
        self.db.delete(poi)
        self.db.commit()
        record_operation_log(
            self.db,
            module="service",
            action="delete",
            target_type="service_poi",
            target_id=poi_id,
            detail=detail,
            current_user=current_user,
        )
