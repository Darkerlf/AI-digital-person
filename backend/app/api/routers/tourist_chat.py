import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/tourist", tags=["tourist"])


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    service = ChatService(db)
    return await service.handle_message(
        message=payload.message,
        session_id=payload.session_id,
        scenic_area_id=payload.scenic_area_id,
    )


@router.post("/chat/stream")
async def chat_stream(payload: ChatRequest, db: Session = Depends(get_db)):
    service = ChatService(db)

    async def event_generator():
        async for chunk in service.handle_message_stream(
            message=payload.message,
            session_id=payload.session_id,
            scenic_area_id=payload.scenic_area_id,
        ):
            yield f"data: {json.dumps({'text': chunk}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
