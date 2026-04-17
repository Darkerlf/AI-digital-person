from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_authenticated_user
from app.core.database import get_db
from app.core.security import hash_password
from app.models.operation_log import OperationLog
from app.repositories.settings_repo import SettingsRepository
from app.schemas.settings import AIProviderCreate, AIProviderUpdate, AdminUserCreate

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/ai-providers")
def list_ai_providers(_: object = Depends(require_authenticated_user), db: Session = Depends(get_db)):
    return {"items": SettingsRepository(db).list_ai_providers()}


@router.post("/ai-providers", status_code=status.HTTP_201_CREATED)
def create_ai_provider(
    payload: AIProviderCreate,
    current_user=Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    item = SettingsRepository(db).create_ai_provider(**payload.model_dump())
    db.add(
        OperationLog(
            admin_user_id=current_user.id,
            module="settings",
            action="create_ai_provider",
            target_type="ai_provider_config",
            target_id=item.id,
            detail_json={"provider_name": item.provider_name},
        )
    )
    db.commit()
    db.refresh(item)
    return item


@router.put("/ai-providers/{provider_id}")
def update_ai_provider(
    provider_id: int,
    payload: AIProviderUpdate,
    current_user=Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    item = SettingsRepository(db).get_ai_provider(provider_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AI provider not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.add(
        OperationLog(
            admin_user_id=current_user.id,
            module="settings",
            action="update_ai_provider",
            target_type="ai_provider_config",
            target_id=item.id,
            detail_json={"provider_name": item.provider_name},
        )
    )
    db.commit()
    db.refresh(item)
    return item


@router.get("/admin-users")
def list_admin_users(_: object = Depends(require_authenticated_user), db: Session = Depends(get_db)):
    return {"items": SettingsRepository(db).list_admin_users()}


@router.post("/admin-users", status_code=status.HTTP_201_CREATED)
def create_admin_user(
    payload: AdminUserCreate,
    current_user=Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    user = SettingsRepository(db).create_admin_user(
        username=payload.username,
        password_hash=hash_password(payload.password),
        role=payload.role,
        status=payload.status,
        last_login_at=None,
    )
    db.add(
        OperationLog(
            admin_user_id=current_user.id,
            module="settings",
            action="create_admin_user",
            target_type="admin_user",
            target_id=user.id,
            detail_json={"username": user.username},
        )
    )
    db.commit()
    db.refresh(user)
    return user
