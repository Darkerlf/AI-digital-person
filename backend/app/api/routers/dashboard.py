from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_authenticated_user
from app.core.database import get_db
from app.schemas.dashboard import DashboardOverview, FeedbackReport
from app.schemas.imports import ImportRequest
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview", response_model=DashboardOverview)
def overview(_: object = Depends(require_authenticated_user), db: Session = Depends(get_db)):
    return DashboardService(db).get_overview()


@router.get("/hot-spots")
def hot_spots(_: object = Depends(require_authenticated_user), db: Session = Depends(get_db)):
    return DashboardService(db).get_hot_spots()


@router.get("/behavior-trends")
def behavior_trends(_: object = Depends(require_authenticated_user), db: Session = Depends(get_db)):
    return DashboardService(db).get_behavior_trends()


@router.get("/feedback-report", response_model=FeedbackReport)
def feedback_report(_: object = Depends(require_authenticated_user), db: Session = Depends(get_db)):
    return DashboardService(db).get_feedback_report()


@router.post("/import-behavior-events")
def import_behavior_events(
    payload: ImportRequest,
    _: object = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    return DashboardService(db).import_behavior_events(payload.source_path)
