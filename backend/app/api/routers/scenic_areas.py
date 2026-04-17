from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.deps import require_content_roles
from app.core.database import get_db
from app.schemas.scenic_area import ScenicAreaCreate, ScenicAreaRead, ScenicAreaUpdate
from app.services.scenic_area_service import ScenicAreaService

router = APIRouter(prefix="/scenic-areas", tags=["scenic-areas"])


@router.post("", response_model=ScenicAreaRead, status_code=status.HTTP_201_CREATED)
def create_area(
    payload: ScenicAreaCreate,
    _: object = Depends(require_content_roles),
    db: Session = Depends(get_db),
):
    return ScenicAreaService(db).create(payload)


@router.get("", response_model=list[ScenicAreaRead])
def list_areas(_: object = Depends(require_content_roles), db: Session = Depends(get_db)):
    return ScenicAreaService(db).list_all()


@router.get("/{area_id}", response_model=ScenicAreaRead)
def get_area(area_id: int, _: object = Depends(require_content_roles), db: Session = Depends(get_db)):
    return ScenicAreaService(db).get(area_id)


@router.put("/{area_id}", response_model=ScenicAreaRead)
def update_area(
    area_id: int,
    payload: ScenicAreaUpdate,
    _: object = Depends(require_content_roles),
    db: Session = Depends(get_db),
):
    return ScenicAreaService(db).update(area_id, payload)


@router.delete("/{area_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_area(area_id: int, _: object = Depends(require_content_roles), db: Session = Depends(get_db)):
    ScenicAreaService(db).delete(area_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
