from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import require_authenticated_user
from app.core.database import get_db
from app.schemas.digital_human import DigitalHumanCreate, DigitalHumanUpdate
from app.services.digital_human_service import DigitalHumanService

router = APIRouter(prefix="/digital-humans", tags=["digital-humans"])


@router.get("")
def list_digital_humans(_: object = Depends(require_authenticated_user), db: Session = Depends(get_db)):
    return {"items": DigitalHumanService(db).list_all()}


@router.post("", status_code=status.HTTP_201_CREATED)
def create_digital_human(
    payload: DigitalHumanCreate,
    _: object = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    return DigitalHumanService(db).create(payload)


@router.put("/{config_id}")
def update_digital_human(
    config_id: int,
    payload: DigitalHumanUpdate,
    _: object = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    return DigitalHumanService(db).update(config_id, payload)
