from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import require_content_roles
from app.core.database import get_db
from app.schemas.knowledge_correction import KnowledgeCorrectionTaskCreate, KnowledgeCorrectionTaskRead
from app.services.knowledge_correction_service import KnowledgeCorrectionService

router = APIRouter(prefix="/knowledge/correction-tasks", tags=["knowledge-correction-tasks"])


@router.post("", response_model=KnowledgeCorrectionTaskRead, status_code=status.HTTP_201_CREATED)
def create_correction_task(
    payload: KnowledgeCorrectionTaskCreate,
    current_user=Depends(require_content_roles),
    db: Session = Depends(get_db),
):
    return KnowledgeCorrectionService(db).create_task(payload, current_user)


@router.get("")
def list_correction_tasks(current_user=Depends(require_content_roles), db: Session = Depends(get_db)):
    return {"items": KnowledgeCorrectionService(db).list_tasks()}


@router.get("/{task_id}", response_model=KnowledgeCorrectionTaskRead)
def get_correction_task(
    task_id: int,
    current_user=Depends(require_content_roles),
    db: Session = Depends(get_db),
):
    return KnowledgeCorrectionService(db).get_task(task_id)
