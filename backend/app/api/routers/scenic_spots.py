from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.deps import require_content_roles
from app.core.database import get_db
from app.schemas.scenic_spot import ScenicSpotCreate, ScenicSpotRead, ScenicSpotUpdate
from app.services.scenic_spot_service import ScenicSpotService

router = APIRouter(prefix="/scenic-spots", tags=["scenic-spots"])


@router.post("", response_model=ScenicSpotRead, status_code=status.HTTP_201_CREATED)
def create_spot(
    payload: ScenicSpotCreate,
    _: object = Depends(require_content_roles),
    db: Session = Depends(get_db),
):
    return ScenicSpotService(db).create(payload)


@router.get("")
def list_spots(_: object = Depends(require_content_roles), db: Session = Depends(get_db)):
    return {"items": ScenicSpotService(db).list_all()}


@router.get("/{spot_id}", response_model=ScenicSpotRead)
def get_spot(spot_id: int, _: object = Depends(require_content_roles), db: Session = Depends(get_db)):
    return ScenicSpotService(db).get_read(spot_id)


@router.put("/{spot_id}", response_model=ScenicSpotRead)
def update_spot(
    spot_id: int,
    payload: ScenicSpotUpdate,
    _: object = Depends(require_content_roles),
    db: Session = Depends(get_db),
):
    return ScenicSpotService(db).update(spot_id, payload)


@router.delete("/{spot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_spot(spot_id: int, _: object = Depends(require_content_roles), db: Session = Depends(get_db)):
    ScenicSpotService(db).delete(spot_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
