from collections import Counter

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.visitor_behavior_event import VisitorBehaviorEvent


def aggregate_daily_stats(db: Session, stat_date: str) -> dict[str, object]:
    rows = db.execute(select(VisitorBehaviorEvent)).scalars().all()
    day_rows = [row for row in rows if row.event_time.startswith(stat_date)]
    hot_spots = Counter(row.spot_name for row in day_rows if row.spot_name)
    hot_questions = Counter(
        row.event_value
        for row in day_rows
        if row.event_type in {"question", "qa_question"} and row.event_value
    )
    missed_questions = Counter(
        row.event_value
        for row in day_rows
        if row.event_type in {"miss", "missed_question", "unanswered_question"} and row.event_value
    )
    route_usage = Counter(row.route_name for row in day_rows if row.route_name)
    active_hours = Counter(row.event_time[11:13] for row in day_rows if len(row.event_time) >= 13)
    visitor_ids = {row.visitor_id for row in day_rows if row.visitor_id}
    scores = []
    for row in day_rows:
        if row.event_type in {"feedback_score", "satisfaction_score"} and row.event_value:
            try:
                scores.append(float(row.event_value))
            except ValueError:
                continue
    return {
        "total_events": len(day_rows),
        "total_visitors": len(visitor_ids),
        "hot_spot_top": hot_spots.most_common(5),
        "hot_question_top": hot_questions.most_common(5),
        "missed_question_top": missed_questions.most_common(5),
        "route_usage": route_usage.most_common(5),
        "active_hour_top": active_hours.most_common(24),
        "satisfaction_score": round(sum(scores) / len(scores), 1) if scores else None,
    }
