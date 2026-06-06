from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.knowledge_repo import KnowledgeRepository
from app.services.knowledge_correction_service import KnowledgeCorrectionService
from app.services.operation_log_service import record_operation_log
from app.schemas.knowledge import FAQCreate, FAQUpdate, KnowledgeDocumentCreate, KnowledgeDocumentUpdate
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

    def update_document(self, document_id: int, payload: KnowledgeDocumentUpdate, current_user=None):
        document = self.get_document(document_id)
        values = payload.model_dump(exclude_unset=True)
        content_was_updated = "content_text" in values
        content_text = values.pop("content_text", None)

        for key, value in values.items():
            setattr(document, key, value)
        if content_was_updated:
            normalized_content = normalize_text(content_text or "")
            document.content_text = normalized_content
            document.version += 1
            self.repo.delete_chunks(document.id)
            for chunk in chunk_text(normalized_content):
                self.repo.add_chunk(document_id=document.id, status=document.status, **chunk)

        self.db.commit()
        self.db.refresh(document)
        record_operation_log(
            self.db,
            module="knowledge",
            action="update",
            target_type="knowledge_document",
            target_id=document.id,
            detail={"changed_fields": sorted([*values.keys(), *(["content_text"] if content_was_updated else [])])},
            current_user=current_user,
        )
        return document

    def delete_document(self, document_id: int, current_user=None) -> None:
        document = self.get_document(document_id)
        detail = {"title": document.title, "source_name": document.source_name}
        self.repo.delete_chunks(document.id)
        self.db.delete(document)
        self.db.commit()
        record_operation_log(
            self.db,
            module="knowledge",
            action="delete",
            target_type="knowledge_document",
            target_id=document_id,
            detail=detail,
            current_user=current_user,
        )

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
        record_operation_log(
            self.db,
            module="knowledge",
            action="create",
            target_type="faq",
            target_id=faq.id,
            detail={"question": faq.question, "category": faq.category},
            current_user=current_user,
        )
        return faq

    def update_faq(self, faq_id: int, payload: FAQUpdate, current_user=None):
        faq = self.repo.get_faq(faq_id)
        if faq is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FAQ not found")
        values = payload.model_dump(exclude_unset=True)
        for key, value in values.items():
            setattr(faq, key, value)
        self.db.commit()
        self.db.refresh(faq)
        record_operation_log(
            self.db,
            module="knowledge",
            action="update",
            target_type="faq",
            target_id=faq.id,
            detail={"changed_fields": sorted(values.keys())},
            current_user=current_user,
        )
        return faq

    def delete_faq(self, faq_id: int, current_user=None) -> None:
        faq = self.repo.get_faq(faq_id)
        if faq is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FAQ not found")
        detail = {"question": faq.question, "category": faq.category}
        self.db.delete(faq)
        self.db.commit()
        record_operation_log(
            self.db,
            module="knowledge",
            action="delete",
            target_type="faq",
            target_id=faq_id,
            detail=detail,
            current_user=current_user,
        )
