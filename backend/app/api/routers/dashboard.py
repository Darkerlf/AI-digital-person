from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_ops_roles
from app.core.database import get_db
from app.schemas.dashboard import DashboardOverview, FeedbackReport
from app.schemas.imports import ImportRequest
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview", response_model=DashboardOverview)
def overview(_: object = Depends(require_ops_roles), db: Session = Depends(get_db)):
    return DashboardService(db).get_overview()


@router.get("/hot-spots")
def hot_spots(
    stat_date: str | None = Query(default=None),
    _: object = Depends(require_ops_roles),
    db: Session = Depends(get_db),
):
    return DashboardService(db).get_hot_spots(stat_date=stat_date)


@router.get("/behavior-trends")
def behavior_trends(
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
    _: object = Depends(require_ops_roles),
    db: Session = Depends(get_db),
):
    return DashboardService(db).get_behavior_trends(start_date=start_date, end_date=end_date)


@router.get("/feedback-report", response_model=FeedbackReport)
def feedback_report(
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
    scenic_area_id: int | None = Query(default=None),
    source_type: str | None = Query(default=None),
    _: object = Depends(require_ops_roles),
    db: Session = Depends(get_db),
):
    return DashboardService(db).get_feedback_report(
        start_date=start_date,
        end_date=end_date,
        scenic_area_id=scenic_area_id,
        source_type=source_type,
    )


@router.post("/import-behavior-events")
def import_behavior_events(
    payload: ImportRequest,
    _: object = Depends(require_ops_roles),
    db: Session = Depends(get_db),
):
    return DashboardService(db).import_behavior_events(payload.source_path)
