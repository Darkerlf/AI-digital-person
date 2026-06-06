from pydantic import BaseModel, Field


class RouteTemplateSpotWrite(BaseModel):
    scenic_spot_id: int
    sort_order: int
    stay_minutes: int | None = None
    highlight: str | None = None


class RouteTemplateSpotRead(RouteTemplateSpotWrite):
    id: int
    name: str


class RouteTemplateCreate(BaseModel):
    scenic_area_id: int
    name: str
    template_type: str = "fixed"
    interest_tags: list[str] = Field(default_factory=list)
    audience_tags: list[str] = Field(default_factory=list)
    duration_min_minutes: int
    duration_max_minutes: int
    summary: str | None = None
    status: str = "active"
    priority: int = 0
    rule_notes: str | None = None
    spots: list[RouteTemplateSpotWrite] = Field(default_factory=list)


class RouteTemplateUpdate(BaseModel):
    scenic_area_id: int | None = None
    name: str | None = None
    template_type: str | None = None
    interest_tags: list[str] | None = None
    audience_tags: list[str] | None = None
    duration_min_minutes: int | None = None
    duration_max_minutes: int | None = None
    summary: str | None = None
    status: str | None = None
    priority: int | None = None
    rule_notes: str | None = None
    spots: list[RouteTemplateSpotWrite] | None = None


class RouteTemplateRead(BaseModel):
    id: int
    scenic_area_id: int
    name: str
    template_type: str
    interest_tags: list[str]
    audience_tags: list[str]
    duration_min_minutes: int
    duration_max_minutes: int
    summary: str | None = None
    status: str
    priority: int
    rule_notes: str | None = None
    spots: list[RouteTemplateSpotRead]


class RouteRecommendationRequest(BaseModel):
    scenic_area_id: int | None = None
    interest_tags: list[str] = Field(default_factory=list)
    duration_minutes: int
    audience_tags: list[str] = Field(default_factory=list)
    start_spot_name: str | None = None
    end_spot_name: str | None = None
    pace: str | None = None
    mobility_tags: list[str] = Field(default_factory=list)
    service_needs: list[str] = Field(default_factory=list)
    reroute_from_spot_name: str | None = None


class RouteRecommendationMatchedTemplate(BaseModel):
    id: int
    name: str
    template_type: str
    scenic_area_id: int
    priority: int


class RouteRecommendationSpotRead(BaseModel):
    scenic_spot_id: int | None = None
    name: str
    stay_minutes: int | None = None
    highlight: str | None = None


class RouteRecommendationSource(BaseModel):
    title: str | None = None
    source: str | None = None
    score: float | None = None


class RouteRecommendationResponse(BaseModel):
    matched_template: RouteRecommendationMatchedTemplate
    fallback_used: bool
    match_reason: str
    summary: str | None = None
    spots: list[RouteRecommendationSpotRead]
    sources: list[RouteRecommendationSource] = Field(default_factory=list)
