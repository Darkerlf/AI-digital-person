from pydantic import BaseModel


class ChatRequest(BaseModel):
    session_id: int | None = None
    message: str
    scenic_area_id: int | None = None


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
