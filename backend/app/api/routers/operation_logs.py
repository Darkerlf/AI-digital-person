from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_authenticated_user
from app.core.database import get_db
from app.repositories.settings_repo import SettingsRepository

router = APIRouter(prefix="/operation-logs", tags=["operation-logs"])


@router.get("")
def list_operation_logs(_: object = Depends(require_authenticated_user), db: Session = Depends(get_db)):
    return {"items": SettingsRepository(db).list_operation_logs()}
