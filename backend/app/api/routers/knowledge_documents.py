from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import require_content_roles
from app.core.database import get_db
from app.schemas.knowledge import (
    KnowledgeChunkRead,
    KnowledgeDocumentCreate,
    KnowledgeDocumentRead,
    KnowledgeDocumentUpdate,
)
from app.services.knowledge_service import KnowledgeService

router = APIRouter(prefix="/knowledge/documents", tags=["knowledge-documents"])


@router.post("/upload", response_model=KnowledgeDocumentRead, status_code=status.HTTP_201_CREATED)
def create_document(
    payload: KnowledgeDocumentCreate,
    correction_task_id: int | None = None,
    current_user=Depends(require_content_roles),
    db: Session = Depends(get_db),
):
    return KnowledgeService(db).create_document(
        payload,
        correction_task_id=correction_task_id,
        current_user=current_user,
    )


@router.get("", response_model=list[KnowledgeDocumentRead])
def list_documents(_: object = Depends(require_content_roles), db: Session = Depends(get_db)):
    return KnowledgeService(db).list_documents()


@router.get("/{document_id}", response_model=KnowledgeDocumentRead)
def get_document(document_id: int, _: object = Depends(require_content_roles), db: Session = Depends(get_db)):
    return KnowledgeService(db).get_document(document_id)


@router.put("/{document_id}", response_model=KnowledgeDocumentRead)
def update_document(
    document_id: int,
    payload: KnowledgeDocumentUpdate,
    current_user=Depends(require_content_roles),
    db: Session = Depends(get_db),
):
    return KnowledgeService(db).update_document(document_id, payload, current_user=current_user)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    current_user=Depends(require_content_roles),
    db: Session = Depends(get_db),
):
    KnowledgeService(db).delete_document(document_id, current_user=current_user)


@router.get("/{document_id}/chunks")
def list_chunks(document_id: int, _: object = Depends(require_content_roles), db: Session = Depends(get_db)):
    return {
        "items": [
            KnowledgeChunkRead.model_validate(chunk).model_dump()
            for chunk in KnowledgeService(db).list_chunks(document_id)
        ]
    }
