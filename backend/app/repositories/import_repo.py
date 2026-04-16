from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.import_job import ImportJob
from app.models.import_job_item import ImportJobItem


class ImportRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_job(self, **kwargs) -> ImportJob:
        job = ImportJob(**kwargs)
        self.db.add(job)
        self.db.flush()
        return job

    def create_job_item(self, **kwargs) -> ImportJobItem:
        item = ImportJobItem(**kwargs)
        self.db.add(item)
        return item

    def list_jobs(self) -> list[ImportJob]:
        return self.db.execute(select(ImportJob).order_by(ImportJob.id.desc())).scalars().all()

    def get_job(self, job_id: int) -> ImportJob | None:
        return self.db.get(ImportJob, job_id)

    def list_job_items(self, job_id: int) -> list[ImportJobItem]:
        return self.db.execute(
            select(ImportJobItem).where(ImportJobItem.import_job_id == job_id).order_by(ImportJobItem.id.asc())
        ).scalars().all()
