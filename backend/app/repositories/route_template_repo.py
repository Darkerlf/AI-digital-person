import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.route_template import RouteTemplate
from app.models.route_template_spot import RouteTemplateSpot


class RouteTemplateRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_all(self) -> list[RouteTemplate]:
        return self.db.execute(select(RouteTemplate).order_by(RouteTemplate.id.asc())).scalars().all()

    def get(self, template_id: int) -> RouteTemplate | None:
        return self.db.get(RouteTemplate, template_id)

    def list_active_by_area(self, scenic_area_id: int | None) -> list[RouteTemplate]:
        statement = select(RouteTemplate).where(RouteTemplate.status == "active")
        if scenic_area_id is not None:
            statement = statement.where(RouteTemplate.scenic_area_id == scenic_area_id)
        return self.db.execute(statement.order_by(RouteTemplate.priority.desc(), RouteTemplate.id.asc())).scalars().all()

    def create(self, **kwargs) -> RouteTemplate:
        spots = kwargs.pop("spots", [])
        interest_tags = kwargs.pop("interest_tags", [])
        audience_tags = kwargs.pop("audience_tags", [])

        template = RouteTemplate(
            **kwargs,
            interest_tags_json=json.dumps(interest_tags, ensure_ascii=False),
            audience_tags_json=json.dumps(audience_tags, ensure_ascii=False),
        )
        self.db.add(template)
        self.db.flush()
        self._replace_spots(template, spots)
        self.db.commit()
        return self.get(template.id)  # type: ignore[return-value]

    def update(self, template: RouteTemplate, **kwargs) -> RouteTemplate:
        spots = kwargs.pop("spots", None)
        interest_tags = kwargs.pop("interest_tags", None)
        audience_tags = kwargs.pop("audience_tags", None)

        for key, value in kwargs.items():
            setattr(template, key, value)

        if interest_tags is not None:
            template.interest_tags_json = json.dumps(interest_tags, ensure_ascii=False)
        if audience_tags is not None:
            template.audience_tags_json = json.dumps(audience_tags, ensure_ascii=False)
        if spots is not None:
            self._replace_spots(template, spots)

        self.db.commit()
        return self.get(template.id)  # type: ignore[return-value]

    def delete(self, template: RouteTemplate) -> None:
        self.db.delete(template)
        self.db.commit()

    def _replace_spots(self, template: RouteTemplate, spots: list[dict]) -> None:
        for existing in list(template.spots):
            self.db.delete(existing)
        self.db.flush()
        for spot in spots:
            self.db.add(
                RouteTemplateSpot(
                    template_id=template.id,
                    scenic_spot_id=spot["scenic_spot_id"],
                    sort_order=spot["sort_order"],
                    stay_minutes=spot.get("stay_minutes"),
                    highlight=spot.get("highlight"),
                )
            )
