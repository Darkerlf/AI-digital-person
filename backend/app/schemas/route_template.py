from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints, model_validator


RequiredText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
OptionalText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
RouteTemplateType = Literal["fixed", "hybrid", "custom"]
RouteTemplateStatus = Literal["active", "inactive"]


class RouteTemplateSpotWrite(BaseModel):
    scenic_spot_id: int = Field(gt=0)
    sort_order: int = Field(gt=0)
    stay_minutes: int | None = Field(default=None, ge=0)
    highlight: OptionalText | None = None


class RouteTemplateSpotRead(RouteTemplateSpotWrite):
    id: int
    name: str


class RouteTemplateCreate(BaseModel):
    scenic_area_id: int = Field(gt=0)
    name: RequiredText
    template_type: RouteTemplateType = "fixed"
    interest_tags: list[str] = Field(default_factory=list)
    audience_tags: list[str] = Field(default_factory=list)
    duration_min_minutes: int = Field(gt=0)
    duration_max_minutes: int = Field(gt=0)
    summary: OptionalText | None = None
    status: RouteTemplateStatus = "active"
    priority: int = 0
    rule_notes: OptionalText | None = None
    spots: list[RouteTemplateSpotWrite] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_duration_range(self):
        if self.duration_min_minutes > self.duration_max_minutes:
            raise ValueError("duration_min_minutes must be less than or equal to duration_max_minutes")
        return self


class RouteTemplateUpdate(BaseModel):
    scenic_area_id: int | None = Field(default=None, gt=0)
    name: OptionalText | None = None
    template_type: RouteTemplateType | None = None
    interest_tags: list[str] | None = None
    audience_tags: list[str] | None = None
    duration_min_minutes: int | None = Field(default=None, gt=0)
    duration_max_minutes: int | None = Field(default=None, gt=0)
    summary: OptionalText | None = None
    status: RouteTemplateStatus | None = None
    priority: int | None = None
    rule_notes: OptionalText | None = None
    spots: list[RouteTemplateSpotWrite] | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def validate_duration_range(self):
        if (
            self.duration_min_minutes is not None
            and self.duration_max_minutes is not None
            and self.duration_min_minutes > self.duration_max_minutes
        ):
            raise ValueError("duration_min_minutes must be less than or equal to duration_max_minutes")
        return self


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


class RouteDurationBreakdown(BaseModel):
    total_minutes: int
    visit_minutes: int
    walking_minutes: int
    buffer_minutes: int


class RouteRecommendationResponse(BaseModel):
    matched_template: RouteRecommendationMatchedTemplate
    fallback_used: bool
    match_reason: str
    summary: str | None = None
    spots: list[RouteRecommendationSpotRead]
    sources: list[RouteRecommendationSource] = Field(default_factory=list)
    duration_breakdown: RouteDurationBreakdown | None = None
