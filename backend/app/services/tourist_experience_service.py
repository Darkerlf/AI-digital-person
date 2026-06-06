from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.conversation_message import ConversationMessage
from app.models.conversation_session import ConversationSession
from app.models.scenic_area import ScenicArea
from app.models.scenic_spot import ScenicSpot
from app.models.service_poi import ServicePOI


DEFAULT_CENTER = {"latitude": 31.428076, "longitude": 120.098006}

SCENIC_SPOT_GCJ02_COORDINATES = {
    "灵山大照壁": {"latitude": 31.421805, "longitude": 120.104630},
    "五明桥": {"latitude": 31.422550, "longitude": 120.103950},
    "佛足坛": {"latitude": 31.423200, "longitude": 120.102950},
    "五智门": {"latitude": 31.423780, "longitude": 120.101950},
    "菩提大道": {"latitude": 31.424250, "longitude": 120.101050},
    "九龙灌浴": {"latitude": 31.424835, "longitude": 120.100154},
    "降魔浮雕": {"latitude": 31.425550, "longitude": 120.099480},
    "阿育王柱": {"latitude": 31.426220, "longitude": 120.098780},
    "百子戏弥勒": {"latitude": 31.426700, "longitude": 120.098450},
    "祥符禅寺": {"latitude": 31.428076, "longitude": 120.098006},
    "灵山大佛": {"latitude": 31.430266, "longitude": 120.096427},
    "佛教文化博览馆": {"latitude": 31.430050, "longitude": 120.096720},
    "灵山梵宫": {"latitude": 31.428867, "longitude": 120.102472},
    "五印坛城": {"latitude": 31.424856, "longitude": 120.103041},
    "曼飞龙塔": {"latitude": 31.426500, "longitude": 120.103280},
    "无尽意斋": {"latitude": 31.428350, "longitude": 120.096900},
    "拈花广场": {"latitude": 31.479550, "longitude": 120.075410},
    "梵天花海": {"latitude": 31.478200, "longitude": 120.071600},
    "香月花街": {"latitude": 31.477800, "longitude": 120.076200},
    "拈花堂": {"latitude": 31.477450, "longitude": 120.077300},
    "五灯湖": {"latitude": 31.475850, "longitude": 120.076100},
    "鹿鸣谷": {"latitude": 31.480100, "longitude": 120.071900},
}

QUICK_QUESTIONS = [
    "灵山大佛多高？",
    "门票多少钱？",
    "推荐游览路线",
    "附近有餐厅吗？",
]

SERVICE_CATEGORIES = [
    {"label": "厕所", "value": "toilet"},
    {"label": "餐饮", "value": "restaurant"},
    {"label": "停车", "value": "parking"},
    {"label": "服务中心", "value": "service_center"},
    {"label": "售票点", "value": "ticket_office"},
]

FALLBACK_SERVICE_POIS = [
    {
        "id": None,
        "name": "公共厕所",
        "category": "toilet",
        "area_text": "入口服务区",
        "description": "适合入园前后使用，靠近游客服务中心。",
        "open_hours": "随景区开放",
        "latitude": 31.421872,
        "longitude": 120.103365,
    },
    {
        "id": None,
        "name": "灵山胜境游客中心",
        "category": "service_center",
        "area_text": "景区入口",
        "description": "提供咨询、失物招领和基础游客服务。",
        "open_hours": "08:30-17:00",
        "latitude": 31.42034,
        "longitude": 120.10355,
    },
    {
        "id": None,
        "name": "灵山大佛梵宫餐饮(灵山大佛风景区店)",
        "category": "restaurant",
        "area_text": "梵宫附近",
        "description": "适合游览梵宫前后短暂休息和用餐。",
        "open_hours": "以现场开放为准",
        "latitude": 31.428762,
        "longitude": 120.102357,
    },
    {
        "id": None,
        "name": "灵山胜境停车场-入口",
        "category": "parking",
        "area_text": "景区入口外侧",
        "description": "自驾游客建议优先停放于入口停车区域。",
        "open_hours": "随景区开放",
        "latitude": 31.42349,
        "longitude": 120.104927,
    },
]


class TouristExperienceService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_home(self, scenic_area_id: int | None = None) -> dict:
        area = self._get_area(scenic_area_id)
        hot_spots = self._list_spots(area.id if area else scenic_area_id, limit=5)
        return {
            "scenic_area_id": area.id if area else scenic_area_id,
            "scenic_name": area.name if area else "灵山胜境",
            "welcome_message": "你好，我是灵山胜境 AI 导游，可以帮你讲解景点、推荐路线和查询服务设施。",
            "quick_questions": QUICK_QUESTIONS,
            "hot_spots": [self._spot_summary(spot) for spot in hot_spots],
            "service_categories": SERVICE_CATEGORIES,
            "today_route": {
                "title": "亲子家庭路线（4小时轻松游）",
                "duration_minutes": 240,
                "interest_tags": ["亲子", "文化"],
                "audience_tags": ["家庭"],
            },
        }

    def get_map_guide(self, scenic_area_id: int | None = None, location_available: bool = True) -> dict:
        spots = self._list_spots(scenic_area_id)
        service_pois = self._list_service_pois(scenic_area_id)
        center = (self._first_available_center(spots) if location_available else None) or DEFAULT_CENTER
        return {
            "center": center,
            "fallback_mode": "map" if location_available else "list",
            "spots": [
                self._map_guide_spot(spot, index + 1)
                for index, spot in enumerate(spots)
            ],
            "service_pois": [self._service_poi_summary(row) for row in service_pois],
        }

    def get_recent_records(self, visitor_id: str | None = None, limit: int = 10) -> dict:
        statement = select(ConversationSession).order_by(ConversationSession.created_at.desc()).limit(limit)
        if visitor_id:
            statement = statement.where(ConversationSession.visitor_id == visitor_id)
        sessions = self.db.execute(statement).scalars().all()
        return {
            "items": [
                {
                    "id": session.id,
                    "visitor_id": session.visitor_id,
                    "channel": session.channel,
                    "status": session.status,
                    "created_at": session.created_at.isoformat(),
                    "messages": [
                        {
                            "id": message.id,
                            "question_text": message.question_text,
                            "answer_text": message.answer_text,
                            "latency_ms": message.latency_ms,
                            "created_at": message.created_at.isoformat(),
                        }
                        for message in self._list_messages(session.id)
                    ],
                }
                for session in sessions
            ]
        }

    def _get_area(self, scenic_area_id: int | None) -> ScenicArea | None:
        if scenic_area_id:
            area = self.db.get(ScenicArea, scenic_area_id)
            if area:
                return area
        return self.db.execute(select(ScenicArea).order_by(ScenicArea.id.asc()).limit(1)).scalar_one_or_none()

    def _list_spots(self, scenic_area_id: int | None, limit: int | None = None) -> list[ScenicSpot]:
        statement = (
            select(ScenicSpot)
            .where(ScenicSpot.open_status == "open")
            .order_by(ScenicSpot.id.asc())
        )
        if scenic_area_id:
            statement = statement.where(ScenicSpot.scenic_area_id == scenic_area_id)
        if limit:
            statement = statement.limit(limit)
        return list(self.db.execute(statement).scalars().all())

    def _list_service_pois(self, scenic_area_id: int | None) -> list[ServicePOI]:
        base_statement = select(ServicePOI).where(ServicePOI.status == "active")
        if scenic_area_id:
            base_statement = base_statement.where(ServicePOI.scenic_area_id == scenic_area_id)
        statement = base_statement.order_by(ServicePOI.category.asc(), ServicePOI.id.asc())
        rows = list(self.db.execute(statement).scalars().all())
        if rows:
            return rows
        has_configured_rows = self.db.execute(base_statement.limit(1)).scalar_one_or_none() is not None
        if has_configured_rows:
            return []
        return [ServicePOI(**item) for item in FALLBACK_SERVICE_POIS]

    def _list_messages(self, session_id: int) -> list[ConversationMessage]:
        return list(
            self.db.execute(
                select(ConversationMessage)
                .where(ConversationMessage.session_id == session_id)
                .order_by(ConversationMessage.created_at.asc(), ConversationMessage.id.asc())
            ).scalars().all()
        )

    @staticmethod
    def _spot_summary(spot: ScenicSpot) -> dict:
        return {
            "id": spot.id,
            "name": spot.name,
            "detail_intro": spot.detail_intro,
            "highlights": spot.highlights,
            "latitude": spot.latitude,
            "longitude": spot.longitude,
        }

    def _map_guide_spot(self, spot: ScenicSpot, sort_order: int) -> dict:
        latitude = spot.latitude
        longitude = spot.longitude
        coordinate_source = "database" if latitude is not None and longitude is not None else "missing"
        coordinate_verified = bool(spot.coordinate_verified)
        if latitude is not None and longitude is not None and spot.coordinate_source:
            coordinate_source = spot.coordinate_source
        if latitude is None or longitude is None:
            preset = SCENIC_SPOT_GCJ02_COORDINATES.get(spot.name)
            if preset:
                latitude = preset["latitude"]
                longitude = preset["longitude"]
                coordinate_source = "preset_gcj02"
                coordinate_verified = False
        return {
            "id": spot.id,
            "name": spot.name,
            "latitude": latitude,
            "longitude": longitude,
            "coordinate_source": coordinate_source,
            "coordinate_verified": coordinate_verified,
            "sort_order": sort_order,
            "narration_url": f"/api/tourist/scenic-spots/{spot.id}/narration",
            "detail_intro": spot.detail_intro,
        }

    @staticmethod
    def _service_poi_summary(row: ServicePOI) -> dict:
        return {
            "id": row.id,
            "name": row.name,
            "category": row.category,
            "area_text": row.area_text,
            "description": row.description,
            "open_hours": row.open_hours,
            "latitude": row.latitude,
            "longitude": row.longitude,
        }

    @staticmethod
    def _first_available_center(spots: list[ScenicSpot]) -> dict | None:
        for spot in spots:
            if spot.latitude is not None and spot.longitude is not None:
                return {"latitude": spot.latitude, "longitude": spot.longitude}
            preset = SCENIC_SPOT_GCJ02_COORDINATES.get(spot.name)
            if preset:
                return preset
        return None
