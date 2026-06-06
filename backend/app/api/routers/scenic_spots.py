from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.deps import require_content_roles
from app.core.database import get_db
from app.schemas.scenic_spot import (
    ScenicSpotCoordinateBatchResponse,
    ScenicSpotCoordinateCandidateResponse,
    ScenicSpotCoordinateConfirm,
    ScenicSpotCreate,
    ScenicSpotRead,
    ScenicSpotUpdate,
)
from app.services.scenic_spot_coordinate_service import ScenicSpotCoordinateService
from app.services.scenic_spot_service import ScenicSpotService

router = APIRouter(prefix="/scenic-spots", tags=["scenic-spots"])


@router.post("", response_model=ScenicSpotRead, status_code=status.HTTP_201_CREATED)
def create_spot(
    payload: ScenicSpotCreate,
    current_user=Depends(require_content_roles),
    db: Session = Depends(get_db),
):
    return ScenicSpotService(db).create(payload, current_user=current_user)


@router.get("")
def list_spots(
    keyword: str | None = None,
    open_status: str | None = None,
    _: object = Depends(require_content_roles),
    db: Session = Depends(get_db),
):
    return {"items": ScenicSpotService(db).list_all(keyword=keyword, open_status=open_status)}


@router.get("/coordinate-candidates/batch", response_model=ScenicSpotCoordinateBatchResponse)
def list_batch_coordinate_candidates(
    only_unverified: bool = True,
    limit: int = 50,
    _: object = Depends(require_content_roles),
    db: Session = Depends(get_db),
):
    return ScenicSpotCoordinateService(db).list_batch_candidates(only_unverified=only_unverified, limit=limit)


@router.get("/{spot_id}", response_model=ScenicSpotRead)
def get_spot(spot_id: int, _: object = Depends(require_content_roles), db: Session = Depends(get_db)):
    return ScenicSpotService(db).get_read(spot_id)


@router.get("/{spot_id}/coordinate-candidates", response_model=ScenicSpotCoordinateCandidateResponse)
def list_coordinate_candidates(
    spot_id: int,
    _: object = Depends(require_content_roles),
    db: Session = Depends(get_db),
):
    return ScenicSpotCoordinateService(db).list_candidates(spot_id)


@router.post("/{spot_id}/coordinate-candidates/confirm", response_model=ScenicSpotRead)
def confirm_coordinate_candidate(
    spot_id: int,
    payload: ScenicSpotCoordinateConfirm,
    current_user=Depends(require_content_roles),
    db: Session = Depends(get_db),
):
    return ScenicSpotCoordinateService(db).confirm_candidate(spot_id, payload, current_user=current_user)


@router.put("/{spot_id}", response_model=ScenicSpotRead)
def update_spot(
    spot_id: int,
    payload: ScenicSpotUpdate,
    current_user=Depends(require_content_roles),
    db: Session = Depends(get_db),
):
    return ScenicSpotService(db).update(spot_id, payload, current_user=current_user)


@router.delete("/{spot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_spot(spot_id: int, current_user=Depends(require_content_roles), db: Session = Depends(get_db)):
    ScenicSpotService(db).delete(spot_id, current_user=current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
