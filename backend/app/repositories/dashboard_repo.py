from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.dashboard_stat_daily import DashboardStatDaily
from app.models.feedback_record import FeedbackRecord
from app.models.import_job import ImportJob
from app.models.knowledge_document import KnowledgeDocument
from app.models.scenic_spot import ScenicSpot
from app.models.visitor_behavior_event import VisitorBehaviorEvent


class DashboardRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def count_events(self) -> int:
        return self.db.scalar(select(func.count(VisitorBehaviorEvent.id))) or 0

    def count_spots(self) -> int:
        return self.db.scalar(select(func.count(ScenicSpot.id))) or 0

    def count_documents(self) -> int:
        return self.db.scalar(select(func.count(KnowledgeDocument.id))) or 0

    def recent_jobs(self) -> list[ImportJob]:
        return self.db.execute(select(ImportJob).order_by(ImportJob.id.desc()).limit(5)).scalars().all()

    def list_feedback_records(self) -> list[FeedbackRecord]:
        return self.db.execute(select(FeedbackRecord).order_by(FeedbackRecord.id.desc())).scalars().all()

    def upsert_daily_stat(self, stat_date: str, payload: dict[str, object]) -> DashboardStatDaily:
        stat = self.db.execute(
            select(DashboardStatDaily).where(DashboardStatDaily.stat_date == stat_date)
        ).scalar_one_or_none()
        if stat is None:
            stat = DashboardStatDaily(stat_date=stat_date, scenic_area_id=None)
            self.db.add(stat)
        stat.total_events = int(payload.get("total_events", 0))
        stat.total_visitors = int(payload.get("total_visitors", 0))
        stat.hot_spot_top_json = payload.get("hot_spot_top")
        stat.hot_question_top_json = payload.get("hot_question_top")
        stat.route_usage_json = payload.get("route_usage")
        stat.satisfaction_score = payload.get("satisfaction_score")  # type: ignore[assignment]
        self.db.commit()
        self.db.refresh(stat)
        return stat
