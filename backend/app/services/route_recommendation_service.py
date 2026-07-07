from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.route_recommendation_record import RouteRecommendationRecord
from app.repositories.route_template_repo import RouteTemplateRepository
from app.schemas.route_template import RouteRecommendationRequest


class RouteRecommendationService:
    def __init__(self, db: Session) -> None:
        self.db = db
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
        result = {
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
        result["duration_breakdown"] = self._build_duration_breakdown(
            result["spots"],
            payload.duration_minutes,
            pace=payload.pace,
        )
        self._record_generation(payload, result)
        return result

    def _record_generation(self, payload: RouteRecommendationRequest, result: dict) -> None:
        matched_template = result["matched_template"]
        self.db.add(
            RouteRecommendationRecord(
                scenic_area_id=payload.scenic_area_id,
                source=matched_template["template_type"],
                duration_minutes=payload.duration_minutes,
                matched_template_id=matched_template["id"] or None,
                matched_template_name=matched_template["name"],
                fallback_used=result["fallback_used"],
                request_json=payload.model_dump(),
                response_json=result,
            )
        )
        self.db.commit()

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

    @classmethod
    def _build_duration_breakdown(
        cls,
        spots: list[dict],
        total_minutes: int,
        pace: str | None = None,
    ) -> dict[str, int]:
        walking_minutes = cls._estimate_walking_minutes(spots, pace)
        visit_minutes = sum(int(spot.get("stay_minutes") or 0) for spot in spots)
        if visit_minutes <= 0:
            visit_minutes = max(0, total_minutes - walking_minutes)
        buffer_minutes = max(0, total_minutes - visit_minutes - walking_minutes)
        return {
            "total_minutes": total_minutes,
            "visit_minutes": visit_minutes,
            "walking_minutes": walking_minutes,
            "buffer_minutes": buffer_minutes,
        }

    @staticmethod
    def _estimate_walking_minutes(spots: list[dict], pace: str | None = None) -> int:
        transitions = max(0, len(spots) - 1)
        per_leg = {
            "fast": 6,
            "standard": 8,
            "normal": 8,
            "relaxed": 10,
        }.get(pace or "standard", 8)
        return transitions * per_leg
