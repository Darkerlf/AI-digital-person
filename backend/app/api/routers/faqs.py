from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.deps import require_content_roles
from app.core.database import get_db
from app.schemas.knowledge import FAQCreate, FAQRead, FAQUpdate
from app.services.knowledge_service import KnowledgeService

router = APIRouter(prefix="/knowledge/faqs", tags=["faqs"])


@router.get("")
def list_faqs(_: object = Depends(require_content_roles), db: Session = Depends(get_db)):
    return {"items": KnowledgeService(db).list_faqs()}


@router.post("", response_model=FAQRead, status_code=status.HTTP_201_CREATED)
def create_faq(
    payload: FAQCreate,
    correction_task_id: int | None = None,
    current_user=Depends(require_content_roles),
    db: Session = Depends(get_db),
):
    return KnowledgeService(db).create_faq(payload, correction_task_id=correction_task_id, current_user=current_user)


@router.put("/{faq_id}", response_model=FAQRead)
def update_faq(
    faq_id: int,
    payload: FAQUpdate,
    current_user=Depends(require_content_roles),
    db: Session = Depends(get_db),
):
    return KnowledgeService(db).update_faq(faq_id, payload, current_user=current_user)


@router.delete("/{faq_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_faq(faq_id: int, current_user=Depends(require_content_roles), db: Session = Depends(get_db)):
    KnowledgeService(db).delete_faq(faq_id, current_user=current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
