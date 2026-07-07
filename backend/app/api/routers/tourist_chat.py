import json

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_visitor
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

FAMILY_SPOT_NARRATION_PROFILES = {
    "灵山大佛": {
        "opening": "来到灵山大佛，先别急着背知识，家长可以陪小朋友一起抬头感受它的高度。",
        "observation": "可以找一找佛像的手势、莲花座和脚下台阶，看看这些细节怎样让大佛显得安定又庄严。",
        "closing": "讲到这里，可以把它理解成一份安静的祝福：愿大家心里稳稳的，也愿今天的旅程顺顺利利。",
    },
    "佛足坛": {
        "opening": "在佛足坛，可以先把脚步放慢，把这里看成一处关于行走和愿望的地方。",
        "observation": "家长可以带孩子找一找足印、花纹和台面上的线条，想象每一步都在提醒人认真向前走。",
        "closing": "离开前，可以和孩子聊聊今天想认真走好的一小步，让景点故事和自己的生活连起来。",
    },
    "九龙灌浴": {
        "opening": "到了九龙灌浴，最适合把讲解变成一场小小的现场观察。",
        "observation": "可以和孩子一起等音乐响起，观察水流、莲花和小太子像是怎样配合表演的。",
        "closing": "表演结束后，不妨让孩子说说刚才最惊喜的一幕，把热闹的表演变成自己的旅行记忆。",
    },
    "百子戏弥勒": {
        "opening": "百子戏弥勒的气氛很轻松，可以用找表情的方式带孩子进入故事。",
        "observation": "让小朋友找一找不同孩子的表情和动作，看看哪一个最像自己，哪一个最有趣。",
        "closing": "这一站不用讲得太严肃，记住快乐、包容和笑眯眯的善意，就已经很棒了。",
    },
    "灵山梵宫": {
        "opening": "走进灵山梵宫，可以把它当成一座会发光的艺术大厅来参观。",
        "observation": "家长可以带孩子观察屋顶、墙面和灯光里的花纹，像做一次安静的艺术寻宝。",
        "closing": "最后请孩子说出自己最喜欢的一处颜色或图案，这比记住一长串术语更有意义。",
    },
    "五印坛城": {
        "opening": "五印坛城和前面的汉传佛教景观不太一样，适合带孩子发现建筑风格的变化。",
        "observation": "可以一起找一找鲜明的颜色、纹样和屋顶造型，感受藏式建筑给人的第一印象。",
        "closing": "如果孩子觉得新奇，就告诉他：旅行的乐趣之一，就是看见和自己熟悉世界不同的美。",
    },
    "五明桥": {
        "opening": "走到五明桥，可以把脚步放慢一点，把它当作进入景区故事的过渡。",
        "observation": "家长可以让孩子数一数桥上的线条和装饰，边走边观察水面和远处景观。",
        "closing": "过桥时可以提醒孩子，桥不只是用来通行，也常常象征从日常走进一段新的体验。",
    },
}

FALLBACK_FAMILY_OPENINGS = [
    "来到这一站，可以先让小朋友用眼睛当小相机，找出最先吸引自己的地方。",
    "这一处景点适合慢慢看，家长可以先问小朋友：你觉得它像什么？",
    "在这里，不妨把讲解变成一次小小的发现任务，让小朋友先观察再听故事。",
]

FALLBACK_FAMILY_OBSERVATIONS = [
    "可以一起找一找颜色、形状、纹样和空间变化，看看哪个细节最容易被记住。",
    "可以让小朋友选一个最喜欢的角度，再说说它为什么特别。",
    "可以边走边看，把看到的细节和听到的故事连成一段自己的旅行印象。",
]

FALLBACK_FAMILY_CLOSINGS = [
    "最后请小朋友用一句话总结这一站，哪怕只是一个颜色、一个形状，也是一份真实的观察。",
    "如果小朋友还想继续问，就把问题留给下一站，让好奇心一路跟着走。",
    "这一站不用记很多术语，能带着兴趣看懂一点点，就已经是很好的亲子导览。",
]


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, visitor=Depends(get_current_visitor), db: Session = Depends(get_db)):
    service = ChatService(db)
    return await service.handle_message(
        message=payload.message,
        session_id=payload.session_id,
        scenic_area_id=payload.scenic_area_id,
        visitor_id=str(visitor.id),
    )


@router.post("/chat/stream")
async def chat_stream(payload: ChatRequest, visitor=Depends(get_current_visitor), db: Session = Depends(get_db)):
    service = ChatService(db)
    visitor_id = str(visitor.id)

    async def event_generator():
        async for chunk in service.handle_message_stream(
            message=payload.message,
            session_id=payload.session_id,
            scenic_area_id=payload.scenic_area_id,
            visitor_id=visitor_id,
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
    limit: int = Query(10, ge=1, le=50),
    visitor=Depends(get_current_visitor),
    db: Session = Depends(get_db),
):
    return TouristExperienceService(db).get_recent_records(visitor_id=str(visitor.id), limit=limit)


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    payload: FeedbackRequest,
    visitor=Depends(get_current_visitor),
    db: Session = Depends(get_db),
):
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
        detail_parts = [part.strip() for part in (intro, highlights) if part and part.strip()]
        detail = " ".join(detail_parts)
        family_profile = _family_narration_profile(title)
        narration = (
            f"{title}亲子讲解："
            f"{family_profile['opening']}"
            f"{detail}"
            f"{family_profile['observation']}"
            f"{family_profile['closing']}"
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


def _family_narration_profile(title: str) -> dict[str, str]:
    for keyword, profile in FAMILY_SPOT_NARRATION_PROFILES.items():
        if keyword in title:
            return profile
    index = sum(ord(char) for char in title) % len(FALLBACK_FAMILY_OPENINGS)
    return {
        "opening": FALLBACK_FAMILY_OPENINGS[index],
        "observation": FALLBACK_FAMILY_OBSERVATIONS[index],
        "closing": FALLBACK_FAMILY_CLOSINGS[index],
    }


@router.post("/routes/recommend", response_model=RouteRecommendationResponse)
async def tourist_recommend_route(
    payload: RouteRecommendationRequest,
    visitor=Depends(get_current_visitor),
    db: Session = Depends(get_db),
):
    return await RouteRAGRecommendationService(db).generate(payload)


@router.post("/routes/walk-guide", response_model=WalkGuideResponse)
def tourist_walk_guide(
    payload: WalkGuideRequest,
    visitor=Depends(get_current_visitor),
    db: Session = Depends(get_db),
):
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
