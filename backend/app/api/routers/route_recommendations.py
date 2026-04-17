from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_authenticated_user
from app.core.database import get_db
from app.schemas.route_template import RouteRecommendationRequest, RouteRecommendationResponse
from app.services.route_recommendation_service import RouteRecommendationService

router = APIRouter(prefix="/route-recommendations", tags=["route-recommendations"])


@router.post("/generate", response_model=RouteRecommendationResponse)
def generate_recommendation(
    payload: RouteRecommendationRequest,
    _: object = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    return RouteRecommendationService(db).generate(payload)
