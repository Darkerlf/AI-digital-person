from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.knowledge_repo import KnowledgeRepository
from app.services.knowledge_correction_service import KnowledgeCorrectionService
from app.schemas.knowledge import FAQCreate, FAQUpdate, KnowledgeDocumentCreate
from app.tasks.knowledge_chunker import chunk_text
from app.utils.text_cleaner import normalize_text


class KnowledgeService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = KnowledgeRepository(db)

    def create_document(self, payload: KnowledgeDocumentCreate, correction_task_id: int | None = None, current_user=None):
        content_text = normalize_text(payload.content_text)
        document = self.repo.create_document(
            scenic_area_id=payload.scenic_area_id,
            title=payload.title,
            doc_type=payload.doc_type,
            source_name=payload.source_name,
            source_path=None,
            content_text=content_text,
            status="active",
            version=1,
            imported_at=None,
            created_by=None,
        )
        for chunk in chunk_text(content_text):
            self.repo.add_chunk(document_id=document.id, status="active", **chunk)
        self.db.commit()
        self.db.refresh(document)
        if correction_task_id is not None and current_user is not None:
            KnowledgeCorrectionService(self.db).link_document_and_resolve(
                correction_task_id=correction_task_id,
                document_id=document.id,
                current_user=current_user,
            )
        return document

    def list_documents(self):
        return self.repo.list_documents()

    def get_document(self, document_id: int):
        document = self.repo.get_document(document_id)
        if document is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge document not found")
        return document

    def list_chunks(self, document_id: int):
        self.get_document(document_id)
        return self.repo.list_chunks(document_id)

    def list_faqs(self):
        return self.repo.list_faqs()

    def create_faq(self, payload: FAQCreate, correction_task_id: int | None = None, current_user=None):
        faq = self.repo.create_faq(**payload.model_dump())
        if correction_task_id is not None and current_user is not None:
            KnowledgeCorrectionService(self.db).link_faq_and_resolve(
                correction_task_id=correction_task_id,
                faq_id=faq.id,
                current_user=current_user,
            )
        return faq

    def update_faq(self, faq_id: int, payload: FAQUpdate):
        faq = self.repo.get_faq(faq_id)
        if faq is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FAQ not found")
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(faq, key, value)
        self.db.commit()
        self.db.refresh(faq)
        return faq

    def delete_faq(self, faq_id: int) -> None:
        faq = self.repo.get_faq(faq_id)
        if faq is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FAQ not found")
        self.db.delete(faq)
        self.db.commit()
