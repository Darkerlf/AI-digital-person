from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.service_poi import ServicePOI


class ServicePOIRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_all(self, category: str | None = None, scenic_area_id: int | None = None) -> list[ServicePOI]:
        statement = select(ServicePOI).order_by(ServicePOI.category.asc(), ServicePOI.id.asc())
        if category:
            statement = statement.where(ServicePOI.category == category)
        if scenic_area_id:
            statement = statement.where(ServicePOI.scenic_area_id == scenic_area_id)
        return self.db.execute(statement).scalars().all()

    def get(self, poi_id: int) -> ServicePOI | None:
        return self.db.get(ServicePOI, poi_id)

    def create(self, **kwargs) -> ServicePOI:
        poi = ServicePOI(**kwargs)
        self.db.add(poi)
        self.db.commit()
        self.db.refresh(poi)
        return poi
