from pydantic import BaseModel


class ScenicSpotCreate(BaseModel):
    scenic_area_id: int
    spot_code: str
    name: str
    alias: str | None = None
    location_text: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    coordinate_source: str | None = None
    coordinate_confidence: int | None = None
    coordinate_verified: bool = False
    tencent_poi_id: str | None = None
    coordinate_address: str | None = None
    coordinate_raw_json: str | None = None
    cover_image_url: str | None = None
    guide_text: str | None = None
    target_audience: str | None = None
    parameters_text: str | None = None
    core_function: str | None = None
    cultural_value: str | None = None
    detail_intro: str | None = None
    highlights: str | None = None
    performance_info: str | None = None
    remarks: str | None = None
    suggested_duration_minutes: int | None = None
    open_status: str = "open"
    tags: list[str] = []


class ScenicSpotUpdate(BaseModel):
    scenic_area_id: int | None = None
    spot_code: str | None = None
    name: str | None = None
    alias: str | None = None
    location_text: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    coordinate_source: str | None = None
    coordinate_confidence: int | None = None
    coordinate_verified: bool | None = None
    tencent_poi_id: str | None = None
    coordinate_address: str | None = None
    coordinate_raw_json: str | None = None
    cover_image_url: str | None = None
    guide_text: str | None = None
    target_audience: str | None = None
    parameters_text: str | None = None
    core_function: str | None = None
    cultural_value: str | None = None
    detail_intro: str | None = None
    highlights: str | None = None
    performance_info: str | None = None
    remarks: str | None = None
    suggested_duration_minutes: int | None = None
    open_status: str | None = None
    tags: list[str] | None = None


class ScenicSpotRead(ScenicSpotCreate):
    id: int


class ScenicSpotCoordinateCandidate(BaseModel):
    provider: str
    title: str
    address: str | None = None
    category: str | None = None
    latitude: float
    longitude: float
    confidence: int
    distance_meters: int | None = None
    tencent_poi_id: str | None = None
    raw: dict | None = None


class ScenicSpotCoordinateCandidateResponse(BaseModel):
    spot_id: int
    search_keyword: str
    center: dict
    candidates: list[ScenicSpotCoordinateCandidate]


class ScenicSpotCoordinateBatchItem(ScenicSpotCoordinateCandidateResponse):
    spot_name: str


class ScenicSpotCoordinateBatchResponse(BaseModel):
    items: list[ScenicSpotCoordinateBatchItem]


class ScenicSpotCoordinateConfirm(BaseModel):
    latitude: float
    longitude: float
    coordinate_source: str = "tencent_place"
    coordinate_confidence: int | None = None
    tencent_poi_id: str | None = None
    coordinate_address: str | None = None
    coordinate_raw_json: dict | None = None
