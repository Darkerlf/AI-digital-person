from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.faq_item import FAQItem
from app.models.knowledge_chunk import KnowledgeChunk
from app.models.knowledge_document import KnowledgeDocument


class KnowledgeRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_document(self, **kwargs) -> KnowledgeDocument:
        document = KnowledgeDocument(**kwargs)
        self.db.add(document)
        self.db.flush()
        return document

    def add_chunk(self, **kwargs) -> KnowledgeChunk:
        chunk = KnowledgeChunk(**kwargs)
        self.db.add(chunk)
        return chunk

    def list_chunks(self, document_id: int) -> list[KnowledgeChunk]:
        return self.db.execute(
            select(KnowledgeChunk)
            .where(KnowledgeChunk.document_id == document_id)
            .order_by(KnowledgeChunk.chunk_index.asc())
        ).scalars().all()

    def list_documents(self) -> list[KnowledgeDocument]:
        return self.db.execute(select(KnowledgeDocument).order_by(KnowledgeDocument.id.asc())).scalars().all()

    def get_document(self, document_id: int) -> KnowledgeDocument | None:
        return self.db.get(KnowledgeDocument, document_id)

    def list_faqs(self) -> list[FAQItem]:
        return self.db.execute(select(FAQItem).order_by(FAQItem.id.asc())).scalars().all()

    def create_faq(self, **kwargs) -> FAQItem:
        faq = FAQItem(**kwargs)
        self.db.add(faq)
        self.db.commit()
        self.db.refresh(faq)
        return faq

    def get_faq(self, faq_id: int) -> FAQItem | None:
        return self.db.get(FAQItem, faq_id)
