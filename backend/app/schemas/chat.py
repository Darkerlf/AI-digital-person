from typing import Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: int | None = None
    message: str
    scenic_area_id: int | None = None
    visitor_id: str | None = None


class ChatResponse(BaseModel):
    session_id: int
    answer: str
    intent: str
    sources: list[dict]


class TouristSessionCreate(BaseModel):
    scenic_area_id: int | None = None
    channel: str = "miniprogram"
    visitor_id: str | None = None


class TouristSessionOut(BaseModel):
    id: int
    session_key: str
    channel: str
    status: str

    model_config = {"from_attributes": True}


class ConversationTurnOut(BaseModel):
    id: int
    role: str
    content: str
    intent: str | None = None
    created_at: str

    model_config = {"from_attributes": True}


class FeedbackRequest(BaseModel):
    session_id: int | None = None
    message_id: int | None = None
    sentiment: Literal["positive", "neutral", "negative"]
    score: float | None = Field(default=None, ge=1, le=5)
    content: str | None = None
    scenic_area_id: int | None = None


class FeedbackResponse(BaseModel):
    id: int
    status: str = "ok"
