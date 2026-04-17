from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.importers.behavior_excel_importer import BehaviorExcelImporter
from app.models.visitor_behavior_event import VisitorBehaviorEvent
from app.repositories.dashboard_repo import DashboardRepository
from app.repositories.import_repo import ImportRepository
from app.tasks.dashboard_aggregator import aggregate_daily_stats
from app.utils.file_storage import save_upload


class DashboardService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = DashboardRepository(db)
        self.import_repo = ImportRepository(db)

    def get_overview(self) -> dict[str, object]:
        return {
            "total_events": self.repo.count_events(),
            "total_spots": self.repo.count_spots(),
            "total_documents": self.repo.count_documents(),
            "recent_import_jobs": self.repo.recent_jobs(),
        }

    def get_hot_spots(self) -> dict[str, object]:
        stats = aggregate_daily_stats(self.db, "2026-04-07")
        return {"items": stats["hot_spot_top"]}

    def get_behavior_trends(self) -> dict[str, object]:
        rows = self.db.query(VisitorBehaviorEvent).all()
        trends: dict[str, int] = {}
        for row in rows:
            day = row.event_time[:10]
            trends[day] = trends.get(day, 0) + 1
        return {"items": [{"date": key, "count": value} for key, value in sorted(trends.items())]}

    def get_feedback_report(self) -> dict[str, object]:
        rows = self.repo.list_feedback_records()
        if not rows:
            return {
                "total_feedback": 0,
                "average_score": None,
                "sentiment_distribution": {"positive": 0, "neutral": 0, "negative": 0},
                "suggestion_summary": "暂无游客反馈数据，建议先打通游客端反馈采集。",
            }

        sentiment_distribution = {"positive": 0, "neutral": 0, "negative": 0}
        scores = [row.score for row in rows if row.score is not None]
        for row in rows:
            if row.sentiment in sentiment_distribution:
                sentiment_distribution[row.sentiment] += 1

        average_score = round(sum(scores) / len(scores), 1) if scores else None
        negative_rows = [
            row for row in rows if row.sentiment == "negative" or (row.score is not None and row.score < 3.0)
        ]
        if negative_rows:
            focus = negative_rows[0].content or "负面反馈"
            suggestion_summary = f"近期游客反馈集中在：{focus}，建议优先优化相关讲解或路线体验。"
        elif average_score is not None and average_score >= 4.0:
            suggestion_summary = "整体满意度较高，建议继续放大优质讲解内容并保持数字人回答稳定性。"
        else:
            suggestion_summary = "满意度处于中性区间，建议补充景点故事内容并优化路线推荐准确性。"

        return {
            "total_feedback": len(rows),
            "average_score": average_score,
            "sentiment_distribution": sentiment_distribution,
            "suggestion_summary": suggestion_summary,
        }

    def import_behavior_events(self, source_path: str):
        path = Path(source_path)
        if not path.exists():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Source file not found")

        stored_path = save_upload(path)
        job = self.import_repo.create_job(
            job_type="behavior_event",
            source_file_name=path.name,
            source_file_path=str(stored_path),
            status="processing",
            total_count=0,
            success_count=0,
            failed_count=0,
            error_message=None,
            started_at=None,
            finished_at=None,
            created_by=None,
        )
        rows = BehaviorExcelImporter().parse(path)
        touched_dates: set[str] = set()
        for row in rows:
            event_time = str(row.get("event_time") or row.get("时间") or row.get("date") or row.get("日期") or "")
            touched_dates.add(event_time[:10])
            event = VisitorBehaviorEvent(
                scenic_area_id=None,
                event_time=event_time,
                visitor_id=str(row.get("visitor_id") or row.get("用户ID") or ""),
                session_id=str(row.get("session_id") or row.get("会话ID") or ""),
                event_type=str(row.get("event_type") or row.get("行为类型") or "unknown"),
                event_value=str(row.get("event_value") or row.get("行为值") or ""),
                spot_name=str(row.get("spot_name") or row.get("景点名称") or ""),
                route_name=str(row.get("route_name") or row.get("路线名称") or ""),
                raw_json=row,
            )
            self.db.add(event)
        self.db.flush()
        for stat_date in touched_dates:
            if stat_date:
                self.repo.upsert_daily_stat(stat_date, aggregate_daily_stats(self.db, stat_date))
        job.total_count = len(rows)
        job.success_count = len(rows)
        job.status = "success"
        self.db.commit()
        self.db.refresh(job)
        return job
