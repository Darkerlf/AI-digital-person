from datetime import datetime

from pydantic import BaseModel


class KnowledgeCorrectionTaskCreate(BaseModel):
    source_message_id: int
    correction_type: str
    resolution_note: str | None = None


class KnowledgeCorrectionTaskRead(BaseModel):
    id: int
    source_message_id: int
    session_id: int
    scenic_area_id: int | None
    question_text: str
    recognized_text: str | None
    feedback_status: str | None
    correction_type: str
    status: str
    resolution_note: str | None
    linked_faq_id: int | None
    linked_document_id: int | None
    created_by: int | None
    resolved_by: int | None
    created_at: datetime
    updated_at: datetime
