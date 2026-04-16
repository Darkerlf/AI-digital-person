from collections import Counter

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.visitor_behavior_event import VisitorBehaviorEvent


def aggregate_daily_stats(db: Session, stat_date: str) -> dict[str, object]:
    rows = db.execute(select(VisitorBehaviorEvent)).scalars().all()
    day_rows = [row for row in rows if row.event_time.startswith(stat_date)]
    hot_spots = Counter(row.spot_name for row in day_rows if row.spot_name)
    return {
        "total_events": len(day_rows),
        "hot_spot_top": hot_spots.most_common(5),
    }
