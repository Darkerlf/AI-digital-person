import json

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.route_template_repo import RouteTemplateRepository
from app.schemas.route_template import RouteTemplateCreate, RouteTemplateUpdate


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

    def create(self, payload: RouteTemplateCreate) -> dict:
        template = self.repo.create(**payload.model_dump())
        return self._to_read_dict(template)

    def update(self, template_id: int, payload: RouteTemplateUpdate) -> dict:
        template = self.get(template_id)
        updated = self.repo.update(template, **payload.model_dump(exclude_unset=True))
        return self._to_read_dict(updated)

    def delete(self, template_id: int) -> None:
        self.repo.delete(self.get(template_id))
