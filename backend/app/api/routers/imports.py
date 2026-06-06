from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import require_content_roles
from app.core.database import get_db
from app.schemas.imports import ImportRequest
from app.services.dashboard_service import DashboardService
from app.services.import_service import ImportService

router = APIRouter(prefix="/imports", tags=["imports"])


async def _save_upload_to_temp(file: UploadFile) -> Path:
    suffix = Path(file.filename or "").suffix
    with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        content = await file.read()
        temp_file.write(content)
        return Path(temp_file.name)


@router.post("/scenic-spots", status_code=status.HTTP_201_CREATED)
def import_scenic_spots(
    payload: ImportRequest,
    _: object = Depends(require_content_roles),
    db: Session = Depends(get_db),
):
    return ImportService(db).run_scenic_import(payload.source_path)


@router.post("/scenic-spots/upload", status_code=status.HTTP_201_CREATED)
async def upload_scenic_spots(
    file: UploadFile = File(...),
    _: object = Depends(require_content_roles),
    db: Session = Depends(get_db),
):
    path = await _save_upload_to_temp(file)
    try:
        return ImportService(db).run_scenic_import(str(path), file.filename)
    finally:
        path.unlink(missing_ok=True)


@router.post("/knowledge-docs", status_code=status.HTTP_201_CREATED)
def import_knowledge_documents(
    payload: ImportRequest,
    scenic_area_id: int,
    _: object = Depends(require_content_roles),
    db: Session = Depends(get_db),
):
    return ImportService(db).run_knowledge_import(payload.source_path, scenic_area_id)


@router.post("/knowledge-docs/upload", status_code=status.HTTP_201_CREATED)
async def upload_knowledge_documents(
    scenic_area_id: int,
    file: UploadFile = File(...),
    _: object = Depends(require_content_roles),
    db: Session = Depends(get_db),
):
    path = await _save_upload_to_temp(file)
    try:
        return ImportService(db).run_knowledge_import(str(path), scenic_area_id, file.filename)
    finally:
        path.unlink(missing_ok=True)


@router.post("/behavior-events", status_code=status.HTTP_201_CREATED)
def import_behavior_events(
    payload: ImportRequest,
    _: object = Depends(require_content_roles),
    db: Session = Depends(get_db),
):
    return DashboardService(db).import_behavior_events(payload.source_path)


@router.post("/behavior-events/upload", status_code=status.HTTP_201_CREATED)
async def upload_behavior_events(
    file: UploadFile = File(...),
    _: object = Depends(require_content_roles),
    db: Session = Depends(get_db),
):
    path = await _save_upload_to_temp(file)
    try:
        return DashboardService(db).import_behavior_events(str(path), file.filename)
    finally:
        path.unlink(missing_ok=True)


@router.get("/jobs")
def list_jobs(_: object = Depends(require_content_roles), db: Session = Depends(get_db)):
    return {"items": ImportService(db).list_jobs()}


@router.get("/jobs/{job_id}")
def get_job(job_id: int, _: object = Depends(require_content_roles), db: Session = Depends(get_db)):
    return ImportService(db).get_job(job_id)


@router.get("/jobs/{job_id}/items")
def list_job_items(job_id: int, _: object = Depends(require_content_roles), db: Session = Depends(get_db)):
    return {"items": ImportService(db).list_job_items(job_id)}
