from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import require_content_roles
from app.core.database import get_db
from app.schemas.knowledge import KnowledgeDocumentCreate, KnowledgeDocumentRead
from app.services.knowledge_service import KnowledgeService

router = APIRouter(prefix="/knowledge/documents", tags=["knowledge-documents"])


@router.post("/upload", response_model=KnowledgeDocumentRead, status_code=status.HTTP_201_CREATED)
def create_document(
    payload: KnowledgeDocumentCreate,
    _: object = Depends(require_content_roles),
    db: Session = Depends(get_db),
):
    return KnowledgeService(db).create_document(payload)


@router.get("", response_model=list[KnowledgeDocumentRead])
def list_documents(_: object = Depends(require_content_roles), db: Session = Depends(get_db)):
    return KnowledgeService(db).list_documents()


@router.get("/{document_id}", response_model=KnowledgeDocumentRead)
def get_document(document_id: int, _: object = Depends(require_content_roles), db: Session = Depends(get_db)):
    return KnowledgeService(db).get_document(document_id)


@router.get("/{document_id}/chunks")
def list_chunks(document_id: int, _: object = Depends(require_content_roles), db: Session = Depends(get_db)):
    return {"items": KnowledgeService(db).list_chunks(document_id)}
