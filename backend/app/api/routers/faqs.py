from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.deps import require_content_roles
from app.core.database import get_db
from app.schemas.knowledge import FAQCreate, FAQUpdate
from app.services.knowledge_service import KnowledgeService

router = APIRouter(prefix="/knowledge/faqs", tags=["faqs"])


@router.get("")
def list_faqs(_: object = Depends(require_content_roles), db: Session = Depends(get_db)):
    return {"items": KnowledgeService(db).list_faqs()}


@router.post("", status_code=status.HTTP_201_CREATED)
def create_faq(payload: FAQCreate, _: object = Depends(require_content_roles), db: Session = Depends(get_db)):
    return KnowledgeService(db).create_faq(payload)


@router.put("/{faq_id}")
def update_faq(
    faq_id: int,
    payload: FAQUpdate,
    _: object = Depends(require_content_roles),
    db: Session = Depends(get_db),
):
    return KnowledgeService(db).update_faq(faq_id, payload)


@router.delete("/{faq_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_faq(faq_id: int, _: object = Depends(require_content_roles), db: Session = Depends(get_db)):
    KnowledgeService(db).delete_faq(faq_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
