from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.importers.knowledge_doc_importer import KnowledgeDocImporter
from app.importers.scenic_docx_importer import ScenicDocxImporter
from app.models.import_job import ImportJob
from app.repositories.import_repo import ImportRepository
from app.repositories.scenic_area_repo import ScenicAreaRepository
from app.services.knowledge_service import KnowledgeService
from app.services.scenic_spot_service import ScenicSpotService
from app.utils.file_storage import save_upload

PENDING = "pending"
PROCESSING = "processing"
SUCCESS = "success"
PARTIAL_SUCCESS = "partial_success"
FAILED = "failed"


class ImportService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ImportRepository(db)
        self.area_repo = ScenicAreaRepository(db)

    def _create_job(self, job_type: str, source_path: Path) -> ImportJob:
        stored_path = save_upload(source_path)
        job = self.repo.create_job(
            job_type=job_type,
            source_file_name=source_path.name,
            source_file_path=str(stored_path),
            status=PENDING,
            total_count=0,
            success_count=0,
            failed_count=0,
            error_message=None,
            started_at=None,
            finished_at=None,
            created_by=None,
        )
        self.db.commit()
        self.db.refresh(job)
        return job

    def run_scenic_import(self, source_path: str):
        path = Path(source_path)
        if not path.exists():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Source file not found")
        job = self._create_job("scenic_spot", path)
        job.status = PROCESSING
        importer = ScenicDocxImporter()
        rows = importer.parse(path)
        spot_service = ScenicSpotService(self.db)
        for row in rows:
            area = next((item for item in self.area_repo.list_all() if item.name == row["scenic_area_name"]), None)
            if area is None:
                area = self.area_repo.create(code=row["scenic_area_name"], name=row["scenic_area_name"], description=None, status="active")
            spot = spot_service.create(
                type(
                    "Payload",
                    (),
                    {
                        "model_dump": lambda self, row=row, area=area: {
                            "scenic_area_id": area.id,
                            "spot_code": row["spot_code"],
                            "name": row["name"],
                            "alias": None,
                            "location_text": row["location_text"],
                            "open_status": "open",
                            "tags": [],
                        }
                    },
                )()
            )
            self.repo.create_job_item(
                import_job_id=job.id,
                item_type="scenic_spot",
                raw_payload_json=row,
                target_type="scenic_spot",
                target_id=spot["id"],
                status=SUCCESS,
                error_message=None,
            )
        job.total_count = len(rows)
        job.success_count = len(rows)
        job.failed_count = 0
        job.status = SUCCESS
        self.db.commit()
        self.db.refresh(job)
        return job

    def run_knowledge_import(self, source_path: str, scenic_area_id: int):
        path = Path(source_path)
        if not path.exists():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Source file not found")
        job = self._create_job("knowledge_document", path)
        job.status = PROCESSING
        payload = KnowledgeDocImporter().parse(path)
        document = KnowledgeService(self.db).create_document(
            type(
                "Payload",
                (),
                {
                    "scenic_area_id": scenic_area_id,
                    "title": payload["title"],
                    "doc_type": payload["doc_type"],
                    "source_name": payload["source_name"],
                    "content_text": payload["content_text"],
                },
            )()
        )
        self.repo.create_job_item(
            import_job_id=job.id,
            item_type="knowledge_document",
            raw_payload_json=payload,
            target_type="knowledge_document",
            target_id=document.id,
            status=SUCCESS,
            error_message=None,
        )
        job.total_count = 1
        job.success_count = 1
        job.failed_count = 0
        job.status = SUCCESS
        self.db.commit()
        self.db.refresh(job)
        return job

    def list_jobs(self):
        return self.repo.list_jobs()

    def get_job(self, job_id: int):
        job = self.repo.get_job(job_id)
        if job is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Import job not found")
        return job

    def list_job_items(self, job_id: int):
        self.get_job(job_id)
        return self.repo.list_job_items(job_id)
