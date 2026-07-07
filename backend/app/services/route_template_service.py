import json

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.scenic_area import ScenicArea
from app.models.scenic_spot import ScenicSpot
from app.repositories.route_template_repo import RouteTemplateRepository
from app.schemas.route_template import RouteTemplateCreate, RouteTemplateUpdate
from app.services.operation_log_service import record_operation_log


class RouteTemplateService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = RouteTemplateRepository(db)

    def _to_read_dict(self, template) -> dict:
        return {
            "id": template.id,
            "scenic_area_id": template.scenic_area_id,
            "name": template.name,
            "template_type": template.template_type,
            "interest_tags": json.loads(template.interest_tags_json or "[]"),
            "audience_tags": json.loads(template.audience_tags_json or "[]"),
            "duration_min_minutes": template.duration_min_minutes,
            "duration_max_minutes": template.duration_max_minutes,
            "summary": template.summary,
            "status": template.status,
            "priority": template.priority,
            "rule_notes": template.rule_notes,
            "spots": [
                {
                    "id": item.id,
                    "scenic_spot_id": item.scenic_spot_id,
                    "name": item.scenic_spot.name,
                    "sort_order": item.sort_order,
                    "stay_minutes": item.stay_minutes,
                    "highlight": item.highlight,
                }
                for item in sorted(template.spots, key=lambda value: value.sort_order)
            ],
        }

    def list_all(self) -> list[dict]:
        return [self._to_read_dict(item) for item in self.repo.list_all()]

    def get(self, template_id: int):
        template = self.repo.get(template_id)
        if template is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route template not found")
        return template

    def get_read(self, template_id: int) -> dict:
        return self._to_read_dict(self.get(template_id))

    def _validate_scenic_area(self, scenic_area_id: int) -> None:
        if self.db.get(ScenicArea, scenic_area_id) is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Scenic area not found")

    def _validate_spots_belong_to_area(self, scenic_area_id: int, spots) -> None:
        spot_ids = [spot.scenic_spot_id for spot in spots]
        if len(spot_ids) != len(set(spot_ids)):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route template spots must be unique")

        for spot_id in spot_ids:
            scenic_spot = self.db.get(ScenicSpot, spot_id)
            if scenic_spot is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Scenic spot not found")
            if scenic_spot.scenic_area_id != scenic_area_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Route template spots must belong to the selected scenic area",
                )

    def create(self, payload: RouteTemplateCreate, current_user=None) -> dict:
        self._validate_scenic_area(payload.scenic_area_id)
        self._validate_spots_belong_to_area(payload.scenic_area_id, payload.spots)
        template = self.repo.create(**payload.model_dump())
        record_operation_log(
            self.db,
            module="route",
            action="create",
            target_type="route_template",
            target_id=template.id,
            detail={"name": template.name, "template_type": template.template_type},
            current_user=current_user,
        )
        return self._to_read_dict(template)

    def update(self, template_id: int, payload: RouteTemplateUpdate, current_user=None) -> dict:
        template = self.get(template_id)
        values = payload.model_dump(exclude_unset=True)
        scenic_area_id = values.get("scenic_area_id", template.scenic_area_id)
        duration_min = values.get("duration_min_minutes", template.duration_min_minutes)
        duration_max = values.get("duration_max_minutes", template.duration_max_minutes)

        if duration_min > duration_max:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="duration_min_minutes must be less than or equal to duration_max_minutes",
            )
        self._validate_scenic_area(scenic_area_id)
        if "spots" in values:
            self._validate_spots_belong_to_area(scenic_area_id, payload.spots or [])
        elif "scenic_area_id" in values:
            self._validate_spots_belong_to_area(scenic_area_id, template.spots)

        updated = self.repo.update(template, **values)
        record_operation_log(
            self.db,
            module="route",
            action="update",
            target_type="route_template",
            target_id=updated.id,
            detail={"changed_fields": sorted(values.keys())},
            current_user=current_user,
        )
        return self._to_read_dict(updated)

    def delete(self, template_id: int, current_user=None) -> None:
        template = self.get(template_id)
        detail = {"name": template.name, "template_type": template.template_type}
        self.repo.delete(template)
        record_operation_log(
            self.db,
            module="route",
            action="delete",
            target_type="route_template",
            target_id=template_id,
            detail=detail,
            current_user=current_user,
        )
