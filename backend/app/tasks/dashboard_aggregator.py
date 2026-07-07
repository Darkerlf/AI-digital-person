from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.models.visitor_behavior_event import VisitorBehaviorEvent


def _top_counts(db: Session, stat_date: str, column, *, filters=(), limit: int = 5) -> list[tuple[str, int]]:
    count_label = func.count(VisitorBehaviorEvent.id).label("event_count")
    statement = (
        select(column, count_label)
        .where(VisitorBehaviorEvent.event_time.like(f"{stat_date}%"), column.is_not(None), column != "")
        .where(*filters)
        .group_by(column)
        .order_by(desc(count_label), column.asc())
        .limit(limit)
    )
    return [(str(name), int(count)) for name, count in db.execute(statement).all()]


def aggregate_daily_stats(db: Session, stat_date: str) -> dict[str, object]:
    day_filter = VisitorBehaviorEvent.event_time.like(f"{stat_date}%")
    total_events = db.scalar(select(func.count(VisitorBehaviorEvent.id)).where(day_filter)) or 0
    total_visitors = (
        db.scalar(select(func.count(func.distinct(VisitorBehaviorEvent.visitor_id))).where(day_filter))
        or 0
    )
    hot_spots = _top_counts(db, stat_date, VisitorBehaviorEvent.spot_name)
    hot_questions = _top_counts(
        db,
        stat_date,
        VisitorBehaviorEvent.event_value,
        filters=(VisitorBehaviorEvent.event_type.in_({"question", "qa_question"}),),
    )
    missed_questions = _top_counts(
        db,
        stat_date,
        VisitorBehaviorEvent.event_value,
        filters=(VisitorBehaviorEvent.event_type.in_({"miss", "missed_question", "unanswered_question"}),),
    )
    route_usage = _top_counts(db, stat_date, VisitorBehaviorEvent.route_name)
    hour_column = func.substr(VisitorBehaviorEvent.event_time, 12, 2)
    hour_count = func.count(VisitorBehaviorEvent.id).label("event_count")
    active_hours = [
        (str(hour), int(count))
        for hour, count in db.execute(
            select(hour_column, hour_count)
            .where(day_filter, func.length(VisitorBehaviorEvent.event_time) >= 13)
            .group_by(hour_column)
            .order_by(desc(hour_count), hour_column.asc())
            .limit(24)
        ).all()
    ]
    score_rows = db.execute(
        select(VisitorBehaviorEvent.event_value).where(
            day_filter,
            VisitorBehaviorEvent.event_type.in_({"feedback_score", "satisfaction_score"}),
            VisitorBehaviorEvent.event_value.is_not(None),
            VisitorBehaviorEvent.event_value != "",
        )
    ).all()
    scores = []
    for (value,) in score_rows:
        try:
            scores.append(float(value))
        except (TypeError, ValueError):
            continue
    return {
        "total_events": int(total_events),
        "total_visitors": int(total_visitors),
        "hot_spot_top": hot_spots,
        "hot_question_top": hot_questions,
        "missed_question_top": missed_questions,
        "route_usage": route_usage,
        "active_hour_top": active_hours,
        "satisfaction_score": round(sum(scores) / len(scores), 1) if scores else None,
    }
