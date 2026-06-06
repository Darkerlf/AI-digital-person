from pydantic import BaseModel


class ScenicSpotNarration(BaseModel):
    spot_id: int
    title: str
    mode: str
    narration: str
    source: str


class ServicePOIRead(BaseModel):
    id: int | None = None
    name: str
    category: str
    area_text: str | None = None
    description: str | None = None
    open_hours: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class ServicePOIListResponse(BaseModel):
    items: list[ServicePOIRead]


class HomeQuickRoute(BaseModel):
    title: str
    duration_minutes: int
    interest_tags: list[str]
    audience_tags: list[str]


class ServiceCategory(BaseModel):
    label: str
    value: str


class TouristHomeResponse(BaseModel):
    scenic_area_id: int | None = None
    scenic_name: str
    welcome_message: str
    quick_questions: list[str]
    hot_spots: list[dict]
    service_categories: list[ServiceCategory]
    today_route: HomeQuickRoute


class MapCenter(BaseModel):
    latitude: float
    longitude: float


class MapPoint(BaseModel):
    latitude: float
    longitude: float


class MapGuideSpot(BaseModel):
    id: int
    name: str
    latitude: float | None = None
    longitude: float | None = None
    coordinate_source: str = "missing"
    coordinate_verified: bool = False
    sort_order: int
    narration_url: str
    detail_intro: str | None = None


class MapGuideResponse(BaseModel):
    center: MapCenter
    fallback_mode: str
    spots: list[MapGuideSpot]
    service_pois: list[ServicePOIRead]


class WalkGuideRouteSpot(BaseModel):
    scenic_spot_id: int | None = None
    name: str
    stay_minutes: int | None = None
    highlight: str | None = None


class WalkGuideRequest(BaseModel):
    scenic_area_id: int | None = None
    spots: list[WalkGuideRouteSpot]
    start_location: MapPoint | None = None
    service_needs: list[str] = []


class WalkGuideStop(BaseModel):
    scenic_spot_id: int | None = None
    name: str
    latitude: float
    longitude: float


class WalkGuideLeg(BaseModel):
    from_name: str
    to_name: str
    distance_meters: int
    duration_minutes: int
    polyline: list[MapPoint]
    provider: str
    fallback_used: bool = False


class WalkGuideResponse(BaseModel):
    total_distance_meters: int
    total_duration_minutes: int
    polyline: list[MapPoint]
    legs: list[WalkGuideLeg]
    stops: list[WalkGuideStop]
    service_pois: list[ServicePOIRead]
    fallback_used: bool
    warnings: list[str] = []


class RecentMessage(BaseModel):
    id: int
    question_text: str
    answer_text: str | None = None
    latency_ms: int | None = None
    created_at: str


class RecentRecord(BaseModel):
    id: int
    visitor_id: str | None = None
    channel: str
    status: str
    created_at: str
    messages: list[RecentMessage]


class RecentRecordResponse(BaseModel):
    items: list[RecentRecord]
