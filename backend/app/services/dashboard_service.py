from datetime import date, datetime
from pathlib import Path
import re

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.importers.behavior_excel_importer import BehaviorExcelImporter
from app.models.conversation_message import ConversationMessage
from app.models.route_recommendation_record import RouteRecommendationRecord
from app.models.visitor_behavior_event import VisitorBehaviorEvent
from app.repositories.dashboard_repo import DashboardRepository
from app.repositories.import_repo import ImportRepository
from app.tasks.dashboard_aggregator import aggregate_daily_stats
from app.utils.file_storage import store_upload


TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_\u4e00-\u9fff]+")
STOP_WORDS = {
    "and",
    "the",
    "too",
    "is",
    "are",
    "not",
    "very",
    "with",
    "this",
    "that",
    "should",
    "be",
}


def _json_safe(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


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

    def _latest_event_date(self) -> str | None:
        rows = self.db.query(VisitorBehaviorEvent).all()
        dates = [row.event_time[:10] for row in rows if row.event_time]
        return max(dates) if dates else None

    def get_hot_spots(self, stat_date: str | None = None) -> dict[str, object]:
        selected_date = stat_date or self._latest_event_date()
        if selected_date is None:
            return {"stat_date": None, "items": []}
        stats = aggregate_daily_stats(self.db, selected_date)
        return {"stat_date": selected_date, "items": stats["hot_spot_top"]}

    def get_behavior_trends(self, start_date: str | None = None, end_date: str | None = None) -> dict[str, object]:
        rows = self.db.query(VisitorBehaviorEvent).all()
        trends: dict[str, int] = {}
        for row in rows:
            day = row.event_time[:10]
            if start_date and day < start_date:
                continue
            if end_date and day > end_date:
                continue
            trends[day] = trends.get(day, 0) + 1
        return {"items": [{"date": key, "count": value} for key, value in sorted(trends.items())]}

    def _filter_feedback_rows(
        self,
        *,
        start_date: str | None = None,
        end_date: str | None = None,
        scenic_area_id: int | None = None,
        source_type: str | None = None,
    ):
        rows = self.repo.list_feedback_records()
        filtered = []
        for row in rows:
            day = row.created_at.date().isoformat() if row.created_at else None
            if start_date and (day is None or day < start_date):
                continue
            if end_date and (day is None or day > end_date):
                continue
            if scenic_area_id is not None and row.scenic_area_id != scenic_area_id:
                continue
            if source_type and row.source_type != source_type:
                continue
            filtered.append(row)
        return filtered

    def _extract_feedback_tokens(self, rows) -> list[dict[str, object]]:
        counts: dict[str, int] = {}
        for row in rows:
            for token in TOKEN_PATTERN.findall((row.content or "").lower()):
                if len(token) < 2 or token in STOP_WORDS:
                    continue
                counts[token] = counts.get(token, 0) + 1
        return [
            {"name": key, "count": value}
            for key, value in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:10]
        ]

    def _negative_rows(self, rows):
        return [row for row in rows if row.sentiment == "negative" or (row.score is not None and row.score < 3.0)]

    def _build_feedback_trend(self, rows) -> list[dict[str, object]]:
        buckets: dict[str, dict[str, object]] = {}
        for row in rows:
            day = row.created_at.date().isoformat()
            bucket = buckets.setdefault(day, {"scores": [], "negative_count": 0, "total_feedback": 0})
            bucket["total_feedback"] = int(bucket["total_feedback"]) + 1
            if row.score is not None:
                bucket["scores"].append(float(row.score))  # type: ignore[index, union-attr]
            if row in self._negative_rows([row]):
                bucket["negative_count"] = int(bucket["negative_count"]) + 1

        trend = []
        for day, bucket in sorted(buckets.items()):
            scores = bucket["scores"]
            trend.append(
                {
                    "date": day,
                    "total_feedback": int(bucket["total_feedback"]),
                    "average_score": round(sum(scores) / len(scores), 1) if scores else None,
                    "negative_count": int(bucket["negative_count"]),
                }
            )
        return trend

    def _build_negative_reasons(self, rows) -> list[dict[str, object]]:
        counts: dict[str, int] = {}
        occurrence_counts: dict[str, int] = {}
        for row in self._negative_rows(rows):
            tokens = set()
            for token in TOKEN_PATTERN.findall((row.content or "").lower()):
                if len(token) < 2 or token in STOP_WORDS:
                    continue
                tokens.add(token)
                occurrence_counts[token] = occurrence_counts.get(token, 0) + 1
            for token in tokens:
                counts[token] = counts.get(token, 0) + 1
        return [
            {"reason": key, "count": value}
            for key, value in sorted(
                counts.items(),
                key=lambda item: (-item[1], -occurrence_counts.get(item[0], 0), item[0]),
            )[:10]
        ]

    def _build_route_feedback_analysis(self, rows) -> list[dict[str, object]]:
        buckets: dict[str, dict[str, object]] = {}
        for row in rows:
            if row.source_type != "route" or row.source_id is None:
                continue
            record = self.db.get(RouteRecommendationRecord, row.source_id)
            route_name = record.matched_template_name if record and record.matched_template_name else f"route-{row.source_id}"
            bucket = buckets.setdefault(route_name, {"scores": [], "total_feedback": 0, "negative_count": 0})
            bucket["total_feedback"] = int(bucket["total_feedback"]) + 1
            if row.score is not None:
                bucket["scores"].append(float(row.score))  # type: ignore[index, union-attr]
            if row in self._negative_rows([row]):
                bucket["negative_count"] = int(bucket["negative_count"]) + 1

        items = []
        for route_name, bucket in buckets.items():
            scores = bucket["scores"]
            items.append(
                {
                    "route_name": route_name,
                    "total_feedback": int(bucket["total_feedback"]),
                    "average_score": round(sum(scores) / len(scores), 1) if scores else None,
                    "negative_count": int(bucket["negative_count"]),
                }
            )
        return sorted(items, key=lambda item: (-int(item["negative_count"]), item["route_name"]))

    def get_feedback_report(
        self,
        *,
        start_date: str | None = None,
        end_date: str | None = None,
        scenic_area_id: int | None = None,
        source_type: str | None = None,
    ) -> dict[str, object]:
        rows = self._filter_feedback_rows(
            start_date=start_date,
            end_date=end_date,
            scenic_area_id=scenic_area_id,
            source_type=source_type,
        )
        negative_rows = self._negative_rows(rows)
        if not rows:
            return {
                "total_feedback": 0,
                "average_score": None,
                "sentiment_distribution": {"positive": 0, "neutral": 0, "negative": 0},
                "latest_feedback": [],
                "suggestion_summary": "No feedback data yet.",
                "feedback_trend": [],
                "focus_top_n": [],
                "complaint_top_n": [],
                "negative_reason_top_n": [],
                "route_feedback_analysis": [],
            }

        sentiment_distribution = {"positive": 0, "neutral": 0, "negative": 0}
        scores = [row.score for row in rows if row.score is not None]
        for row in rows:
            if row.sentiment in sentiment_distribution:
                sentiment_distribution[row.sentiment] += 1

        average_score = round(sum(scores) / len(scores), 1) if scores else None
        if negative_rows:
            focus = negative_rows[0].content or "negative feedback"
            suggestion_summary = f"Recent negative feedback focuses on: {focus}."
        elif average_score is not None and average_score >= 4.0:
            suggestion_summary = "Overall satisfaction is high. Keep current guide quality stable."
        else:
            suggestion_summary = "Satisfaction is moderate. Continue improving guide content and route accuracy."

        latest_feedback = []
        for row in rows[:20]:
            message = None
            if row.source_type == "chat" and row.source_id is not None:
                message = self.db.get(ConversationMessage, row.source_id)
            latest_feedback.append(
                {
                    "id": row.id,
                    "message_id": row.source_id if row.source_type == "chat" else None,
                    "session_id": message.session_id if message else None,
                    "sentiment": row.sentiment,
                    "score": row.score,
                    "content": row.content,
                    "question_text": message.question_text if message else None,
                    "answer_text": message.answer_text if message else None,
                    "created_at": row.created_at,
                }
            )

        return {
            "total_feedback": len(rows),
            "average_score": average_score,
            "sentiment_distribution": sentiment_distribution,
            "suggestion_summary": suggestion_summary,
            "latest_feedback": latest_feedback,
            "feedback_trend": self._build_feedback_trend(rows),
            "focus_top_n": self._extract_feedback_tokens(rows),
            "complaint_top_n": self._extract_feedback_tokens(negative_rows),
            "negative_reason_top_n": self._build_negative_reasons(rows),
            "route_feedback_analysis": self._build_route_feedback_analysis(rows),
        }

    def import_behavior_events(self, source_path: str, source_file_name: str | None = None):
        path = Path(source_path)
        if not path.exists():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Source file not found")

        stored_path = store_upload(path, prefix="imports/behavior_event")
        job = self.import_repo.create_job(
            job_type="behavior_event",
            source_file_name=source_file_name or path.name,
            source_file_path=stored_path,
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
            event_time = str(row.get("event_time") or "")
            touched_dates.add(event_time[:10])
            event = VisitorBehaviorEvent(
                scenic_area_id=None,
                event_time=event_time,
                visitor_id=str(row.get("visitor_id") or ""),
                session_id=str(row.get("session_id") or ""),
                event_type=str(row.get("event_type") or "unknown"),
                event_value=str(row.get("event_value") or ""),
                spot_name=str(row.get("spot_name") or ""),
                route_name=str(row.get("route_name") or ""),
                raw_json=_json_safe(row),
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
