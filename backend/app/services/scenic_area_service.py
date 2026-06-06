from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.scenic_area_repo import ScenicAreaRepository
from app.schemas.scenic_area import ScenicAreaCreate, ScenicAreaUpdate
from app.services.operation_log_service import record_operation_log


class ScenicAreaService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ScenicAreaRepository(db)

    def create(self, payload: ScenicAreaCreate, current_user=None):
        area = self.repo.create(**payload.model_dump())
        record_operation_log(
            self.db,
            module="scenic",
            action="create",
            target_type="scenic_area",
            target_id=area.id,
            detail={"code": area.code, "name": area.name},
            current_user=current_user,
        )
        return area

    def list_all(self):
        return self.repo.list_all()

    def get(self, area_id: int):
        area = self.repo.get(area_id)
        if area is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenic area not found")
        return area

    def update(self, area_id: int, payload: ScenicAreaUpdate, current_user=None):
        area = self.get(area_id)
        values = payload.model_dump(exclude_unset=True)
        for key, value in values.items():
            setattr(area, key, value)
        self.db.commit()
        self.db.refresh(area)
        record_operation_log(
            self.db,
            module="scenic",
            action="update",
            target_type="scenic_area",
            target_id=area.id,
            detail={"changed_fields": sorted(values.keys())},
            current_user=current_user,
        )
        return area

    def delete(self, area_id: int, current_user=None) -> None:
        area = self.get(area_id)
        detail = {"code": area.code, "name": area.name}
        self.db.delete(area)
        self.db.commit()
        record_operation_log(
            self.db,
            module="scenic",
            action="delete",
            target_type="scenic_area",
            target_id=area_id,
            detail=detail,
            current_user=current_user,
        )
