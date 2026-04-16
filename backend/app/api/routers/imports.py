from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import require_authenticated_user
from app.core.database import get_db
from app.schemas.imports import ImportRequest
from app.services.dashboard_service import DashboardService
from app.services.import_service import ImportService

router = APIRouter(prefix="/imports", tags=["imports"])


@router.post("/scenic-spots", status_code=status.HTTP_201_CREATED)
def import_scenic_spots(
    payload: ImportRequest,
    _: object = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    return ImportService(db).run_scenic_import(payload.source_path)


@router.post("/knowledge-docs", status_code=status.HTTP_201_CREATED)
def import_knowledge_documents(
    payload: ImportRequest,
    scenic_area_id: int,
    _: object = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    return ImportService(db).run_knowledge_import(payload.source_path, scenic_area_id)


@router.post("/behavior-events", status_code=status.HTTP_201_CREATED)
def import_behavior_events(
    payload: ImportRequest,
    _: object = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    return DashboardService(db).import_behavior_events(payload.source_path)


@router.get("/jobs")
def list_jobs(_: object = Depends(require_authenticated_user), db: Session = Depends(get_db)):
    return {"items": ImportService(db).list_jobs()}


@router.get("/jobs/{job_id}")
def get_job(job_id: int, _: object = Depends(require_authenticated_user), db: Session = Depends(get_db)):
    return ImportService(db).get_job(job_id)


@router.get("/jobs/{job_id}/items")
def list_job_items(job_id: int, _: object = Depends(require_authenticated_user), db: Session = Depends(get_db)):
    return {"items": ImportService(db).list_job_items(job_id)}
