from datetime import datetime

from pydantic import BaseModel


class ConversationSessionListItem(BaseModel):
    id: int
    session_key: str
    channel: str
    visitor_id: str | None
    status: str
    created_at: datetime
    message_count: int
    unresolved_count: int


class ConversationMessageRead(BaseModel):
    id: int
    question_text: str
    recognized_text: str | None
    answer_text: str | None
    matched_document_title: str | None
    latency_ms: int | None
    feedback_status: str | None
    is_missed: bool
    resolution_status: str
    resolution_note: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationSessionDetail(BaseModel):
    id: int
    session_key: str
    channel: str
    visitor_id: str | None
    status: str
    created_at: datetime
    messages: list[ConversationMessageRead]


class UnresolvedConversationItem(BaseModel):
    id: int
    session_id: int
    session_key: str
    question_text: str
    recognized_text: str | None
    feedback_status: str | None
    created_at: datetime
    resolution_status: str


class ResolveConversationMessageRequest(BaseModel):
    resolution_note: str
