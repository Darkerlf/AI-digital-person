from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.route_template_repo import RouteTemplateRepository
from app.schemas.route_template import RouteRecommendationRequest


class RouteRecommendationService:
    def __init__(self, db: Session) -> None:
        self.repo = RouteTemplateRepository(db)

    def generate(self, payload: RouteRecommendationRequest) -> dict:
        candidates = self.repo.list_active_by_area(payload.scenic_area_id)
        if not candidates:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active route template found")

        scored_candidates = [self._score_candidate(template, payload) for template in candidates]
        scored_candidates.sort(
            key=lambda item: (
                0 if item["exact_match"] else 1,
                item["duration_distance"],
                -item["interest_overlap"],
                -item["audience_overlap"],
                -item["priority"],
                item["template"].id,
            )
        )

        winner = scored_candidates[0]
        template = winner["template"]
        return {
            "matched_template": {
                "id": template.id,
                "name": template.name,
                "template_type": template.template_type,
                "scenic_area_id": template.scenic_area_id,
                "priority": template.priority,
            },
            "fallback_used": not winner["exact_match"],
            "match_reason": self._build_match_reason(winner),
            "summary": template.summary,
            "spots": [
                {
                    "scenic_spot_id": item.scenic_spot_id,
                    "name": item.scenic_spot.name,
                    "stay_minutes": item.stay_minutes,
                    "highlight": item.highlight,
                }
                for item in sorted(template.spots, key=lambda value: value.sort_order)
            ],
        }

    def _score_candidate(self, template, payload: RouteRecommendationRequest) -> dict:
        interest_overlap = len(set(payload.interest_tags).intersection(self._load_tags(template.interest_tags_json)))
        audience_overlap = len(set(payload.audience_tags).intersection(self._load_tags(template.audience_tags_json)))
        duration_in_range = template.duration_min_minutes <= payload.duration_minutes <= template.duration_max_minutes
        duration_distance = 0 if duration_in_range else min(
            abs(payload.duration_minutes - template.duration_min_minutes),
            abs(payload.duration_minutes - template.duration_max_minutes),
        )
        exact_match = duration_in_range and (not payload.interest_tags or interest_overlap > 0)
        return {
            "template": template,
            "exact_match": exact_match,
            "duration_in_range": duration_in_range,
            "duration_distance": duration_distance,
            "interest_overlap": interest_overlap,
            "audience_overlap": audience_overlap,
            "priority": template.priority,
        }

    def _build_match_reason(self, result: dict) -> str:
        if result["exact_match"]:
            return "命中时长与兴趣标签条件，返回最佳路线模板。"
        if not result["duration_in_range"]:
            return "未命中精确条件，已放宽时长范围并返回最接近的路线模板。"
        if result["interest_overlap"] == 0:
            return "未命中精确条件，已返回文化主题最接近的路线模板。"
        return "未命中精确条件，已返回综合得分最高的路线模板。"

    @staticmethod
    def _load_tags(raw_tags: str) -> list[str]:
        import json

        return json.loads(raw_tags or "[]")
