from pydantic import BaseModel


class KnowledgeDocumentCreate(BaseModel):
    scenic_area_id: int
    title: str
    doc_type: str
    source_name: str
    content_text: str


class KnowledgeDocumentRead(BaseModel):
    id: int
    scenic_area_id: int
    title: str
    doc_type: str
    source_name: str
    content_text: str | None
    status: str
    version: int

    model_config = {"from_attributes": True}


class KnowledgeChunkRead(BaseModel):
    id: int
    chunk_index: int
    chunk_text: str
    token_count: int
    source_section: str | None

    model_config = {"from_attributes": True}


class FAQCreate(BaseModel):
    scenic_area_id: int
    question: str
    answer: str
    category: str | None = None
    priority: int = 0
    status: str = "active"
    source: str | None = None


class FAQUpdate(BaseModel):
    question: str | None = None
    answer: str | None = None
    category: str | None = None
    priority: int | None = None
    status: str | None = None
    source: str | None = None
