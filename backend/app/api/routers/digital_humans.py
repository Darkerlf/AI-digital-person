from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import require_authenticated_user
from app.core.database import get_db
from app.models.operation_log import OperationLog
from app.schemas.digital_human import DigitalHumanCreate, DigitalHumanUpdate
from app.services.digital_human_service import DigitalHumanService

router = APIRouter(prefix="/digital-humans", tags=["digital-humans"])


@router.get("")
def list_digital_humans(_: object = Depends(require_authenticated_user), db: Session = Depends(get_db)):
    return {"items": DigitalHumanService(db).list_all()}


@router.post("", status_code=status.HTTP_201_CREATED)
def create_digital_human(
    payload: DigitalHumanCreate,
    current_user=Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    item = DigitalHumanService(db).create(payload)
    db.add(
        OperationLog(
            admin_user_id=current_user.id,
            module="digital_humans",
            action="create_digital_human",
            target_type="digital_human_config",
            target_id=item.id,
            detail_json={"name": item.name},
        )
    )
    db.commit()
    db.refresh(item)
    return item


@router.put("/{config_id}")
def update_digital_human(
    config_id: int,
    payload: DigitalHumanUpdate,
    current_user=Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    item = DigitalHumanService(db).update(config_id, payload)
    db.add(
        OperationLog(
            admin_user_id=current_user.id,
            module="digital_humans",
            action="update_digital_human",
            target_type="digital_human_config",
            target_id=item.id,
            detail_json={"name": item.name},
        )
    )
    db.commit()
    db.refresh(item)
    return item
