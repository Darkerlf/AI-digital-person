from fastapi import APIRouter, Depends, Query, status
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
def list_correction_tasks(
    status: str | None = Query(default=None),
    correction_type: str | None = Query(default=None),
    scenic_area_id: int | None = Query(default=None),
    current_user=Depends(require_content_roles),
    db: Session = Depends(get_db),
):
    return {
        "items": KnowledgeCorrectionService(db).list_tasks(
            status=status,
            correction_type=correction_type,
            scenic_area_id=scenic_area_id,
        )
    }


@router.get("/{task_id}", response_model=KnowledgeCorrectionTaskRead)
def get_correction_task(
    task_id: int,
    current_user=Depends(require_content_roles),
    db: Session = Depends(get_db),
):
    return KnowledgeCorrectionService(db).get_task(task_id)
