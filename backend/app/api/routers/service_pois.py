from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import require_content_roles
from app.core.database import get_db
from app.schemas.service_poi import ServicePOICreate, ServicePOIListResponse, ServicePOIRead, ServicePOIUpdate
from app.services.service_poi_service import ServicePOIService

router = APIRouter(prefix="/service-pois", tags=["service-pois"])


@router.post("", response_model=ServicePOIRead, status_code=status.HTTP_201_CREATED)
def create_service_poi(
    payload: ServicePOICreate,
    current_user=Depends(require_content_roles),
    db: Session = Depends(get_db),
):
    return ServicePOIService(db).create(payload, current_user=current_user)


@router.get("", response_model=ServicePOIListResponse)
def list_service_pois(
    category: str | None = Query(default=None),
    scenic_area_id: int | None = Query(default=None),
    _: object = Depends(require_content_roles),
    db: Session = Depends(get_db),
):
    return {"items": ServicePOIService(db).list_all(category=category, scenic_area_id=scenic_area_id)}


@router.get("/{poi_id}", response_model=ServicePOIRead)
def get_service_poi(
    poi_id: int,
    _: object = Depends(require_content_roles),
    db: Session = Depends(get_db),
):
    return ServicePOIService(db).get_read(poi_id)


@router.put("/{poi_id}", response_model=ServicePOIRead)
def update_service_poi(
    poi_id: int,
    payload: ServicePOIUpdate,
    current_user=Depends(require_content_roles),
    db: Session = Depends(get_db),
):
    return ServicePOIService(db).update(poi_id, payload, current_user=current_user)


@router.delete("/{poi_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service_poi(
    poi_id: int,
    current_user=Depends(require_content_roles),
    db: Session = Depends(get_db),
):
    ServicePOIService(db).delete(poi_id, current_user=current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
