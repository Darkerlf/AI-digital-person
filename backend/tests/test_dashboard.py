from app.models.visitor_behavior_event import VisitorBehaviorEvent
from app.tasks.dashboard_aggregator import aggregate_daily_stats


def test_aggregate_daily_stats_counts_events_and_hot_spots(test_db_session) -> None:
    test_db_session.add_all(
        [
            VisitorBehaviorEvent(
                scenic_area_id=None,
                event_time="2026-04-07T10:00:00",
                visitor_id="v1",
                session_id="s1",
                event_type="view",
                event_value="1",
                spot_name="灵山大照壁",
                route_name=None,
                raw_json=None,
            ),
            VisitorBehaviorEvent(
                scenic_area_id=None,
                event_time="2026-04-07T11:00:00",
                visitor_id="v2",
                session_id="s2",
                event_type="view",
                event_value="1",
                spot_name="灵山大照壁",
                route_name=None,
                raw_json=None,
            ),
        ]
    )
    test_db_session.commit()

    result = aggregate_daily_stats(test_db_session, "2026-04-07")

    assert result["total_events"] == 2
    assert result["hot_spot_top"][0][0] == "灵山大照壁"
