import json

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.conversation_message import ConversationMessage
from app.models.feedback_record import FeedbackRecord
from app.models.service_poi import ServicePOI
from app.schemas.chat import ChatRequest, ChatResponse, FeedbackRequest, FeedbackResponse
from app.schemas.route_template import RouteRecommendationRequest, RouteRecommendationResponse
from app.schemas.tourist import (
    MapGuideResponse,
    RecentRecordResponse,
    ScenicSpotNarration,
    ServicePOIListResponse,
    ServicePOIRead,
    TouristHomeResponse,
    WalkGuideRequest,
    WalkGuideResponse,
)
from app.services.chat_service import ChatService
from app.services.route_rag_recommendation_service import RouteRAGRecommendationService
from app.services.scenic_spot_service import ScenicSpotService
from app.services.tourist_experience_service import TouristExperienceService
from app.services.walk_guide_service import WalkGuideService

router = APIRouter(prefix="/tourist", tags=["tourist"])


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    service = ChatService(db)
    return await service.handle_message(
        message=payload.message,
        session_id=payload.session_id,
        scenic_area_id=payload.scenic_area_id,
        visitor_id=payload.visitor_id,
    )


@router.post("/chat/stream")
async def chat_stream(payload: ChatRequest, db: Session = Depends(get_db)):
    service = ChatService(db)

    async def event_generator():
        async for chunk in service.handle_message_stream(
            message=payload.message,
            session_id=payload.session_id,
            scenic_area_id=payload.scenic_area_id,
            visitor_id=payload.visitor_id,
        ):
            yield f"data: {json.dumps({'text': chunk}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/home", response_model=TouristHomeResponse)
def tourist_home(scenic_area_id: int | None = None, db: Session = Depends(get_db)):
    return TouristExperienceService(db).get_home(scenic_area_id)


@router.get("/map-guide", response_model=MapGuideResponse)
def tourist_map_guide(
    scenic_area_id: int | None = None,
    location_available: bool = True,
    db: Session = Depends(get_db),
):
    return TouristExperienceService(db).get_map_guide(scenic_area_id, location_available)


@router.get("/recent-records", response_model=RecentRecordResponse)
def tourist_recent_records(
    visitor_id: str | None = None,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    return TouristExperienceService(db).get_recent_records(visitor_id=visitor_id, limit=limit)


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(payload: FeedbackRequest, db: Session = Depends(get_db)):
    message = None
    if payload.message_id is not None:
        message = db.get(ConversationMessage, payload.message_id)
        if message is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation message not found")
        if payload.session_id is not None and message.session_id != payload.session_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Feedback session does not match message")

    record = FeedbackRecord(
        scenic_area_id=payload.scenic_area_id,
        source_type="chat",
        source_id=payload.message_id,
        sentiment=payload.sentiment,
        score=payload.score,
        content=payload.content,
    )
    db.add(record)
    if message is not None:
        message.feedback_status = {
            "positive": "liked",
            "neutral": "commented",
            "negative": "disliked",
        }[payload.sentiment]
    db.commit()
    db.refresh(record)
    return FeedbackResponse(id=record.id)


@router.get("/scenic-spots")
def tourist_list_scenic_spots(db: Session = Depends(get_db)):
    """Public endpoint for tourists to view scenic spots (no auth required)"""
    return {"items": ScenicSpotService(db).list_all()}


@router.get("/scenic-spots/{spot_id}")
def tourist_get_scenic_spot(spot_id: int, db: Session = Depends(get_db)):
    """Public endpoint for tourists to view a single scenic spot"""
    return ScenicSpotService(db).get_read(spot_id)


@router.get("/scenic-spots/{spot_id}/narration", response_model=ScenicSpotNarration)
def tourist_get_scenic_spot_narration(
    spot_id: int,
    mode: str = Query("brief", pattern="^(brief|deep|family)$"),
    db: Session = Depends(get_db),
):
    spot = ScenicSpotService(db).get_read(spot_id)
    title = spot["name"]
    intro = spot.get("detail_intro") or spot.get("highlights") or "暂无详细讲解资料。"
    highlights = spot.get("highlights") or ""
    cultural = spot.get("cultural_value") or ""

    if mode == "family":
        narration = (
            f"Children can think of {title} as a friendly story stop. "
            f"{intro} {highlights} We can look for shapes, colors, and simple meanings while visiting."
        )
    elif mode == "deep":
        narration = f"{title}深度讲解：{intro} {cultural} {highlights}"
    else:
        narration = f"{title}简短讲解：{intro}"

    return {
        "spot_id": spot_id,
        "title": title,
        "mode": mode,
        "narration": narration.strip(),
        "source": "scenic_spot",
    }


@router.post("/routes/recommend", response_model=RouteRecommendationResponse)
async def tourist_recommend_route(payload: RouteRecommendationRequest, db: Session = Depends(get_db)):
    return await RouteRAGRecommendationService(db).generate(payload)


@router.post("/routes/walk-guide", response_model=WalkGuideResponse)
def tourist_walk_guide(payload: WalkGuideRequest, db: Session = Depends(get_db)):
    return WalkGuideService(db).build(payload)


FALLBACK_SERVICE_POIS = [
    {
        "name": "公共厕所",
        "category": "toilet",
        "area_text": "入口服务区",
        "description": "适合入园前后使用，靠近游客服务中心。",
        "open_hours": "随景区开放",
        "latitude": 31.421872,
        "longitude": 120.103365,
    },
    {
        "name": "灵山胜境游客中心",
        "category": "service_center",
        "area_text": "景区入口",
        "description": "提供咨询、失物招领和基础游客服务。",
        "open_hours": "08:30-17:00",
        "latitude": 31.42034,
        "longitude": 120.10355,
    },
    {
        "name": "灵山大佛梵宫餐饮(灵山大佛风景区店)",
        "category": "restaurant",
        "area_text": "梵宫附近",
        "description": "适合游览梵宫前后短暂休息和用餐。",
        "open_hours": "以现场开放为准",
        "latitude": 31.428762,
        "longitude": 120.102357,
    },
    {
        "name": "灵山胜境停车场-入口",
        "category": "parking",
        "area_text": "景区入口外侧",
        "description": "自驾游客建议优先停放于入口停车区域。",
        "open_hours": "随景区开放",
        "latitude": 31.42349,
        "longitude": 120.104927,
    },
]


@router.get("/service-pois", response_model=ServicePOIListResponse)
def tourist_list_service_pois(
    category: str | None = None,
    scenic_area_id: int | None = None,
    db: Session = Depends(get_db),
):
    base_query = db.query(ServicePOI).filter(ServicePOI.status == "active")
    if scenic_area_id:
        base_query = base_query.filter(ServicePOI.scenic_area_id == scenic_area_id)

    query = base_query
    if category:
        query = query.filter(ServicePOI.category == category)
    rows = query.order_by(ServicePOI.category.asc(), ServicePOI.id.asc()).all()

    if rows:
        items = [
            ServicePOIRead(
                id=row.id,
                name=row.name,
                category=row.category,
                area_text=row.area_text,
                description=row.description,
                open_hours=row.open_hours,
                latitude=row.latitude,
                longitude=row.longitude,
            )
            for row in rows
        ]
    elif base_query.first() is None:
        fallback = FALLBACK_SERVICE_POIS
        if category:
            fallback = [item for item in fallback if item["category"] == category]
        items = [ServicePOIRead(**item) for item in fallback]
    else:
        items = []

    return {"items": items}
