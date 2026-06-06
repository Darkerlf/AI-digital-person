from app.models.visitor_behavior_event import VisitorBehaviorEvent
from app.services.dashboard_service import DashboardService
from app.tasks.dashboard_aggregator import aggregate_daily_stats


def test_aggregate_daily_stats_includes_questions_routes_hours_and_satisfaction(test_db_session) -> None:
    test_db_session.add_all(
        [
            VisitorBehaviorEvent(
                scenic_area_id=None,
                event_time="2026-05-01T09:15:00",
                visitor_id="visitor-1",
                session_id="session-1",
                event_type="view",
                event_value="1",
                spot_name="Grand Hall",
                route_name=None,
                raw_json=None,
            ),
            VisitorBehaviorEvent(
                scenic_area_id=None,
                event_time="2026-05-01T09:45:00",
                visitor_id="visitor-1",
                session_id="session-1",
                event_type="question",
                event_value="How long is the route?",
                spot_name=None,
                route_name="Classic Route",
                raw_json=None,
            ),
            VisitorBehaviorEvent(
                scenic_area_id=None,
                event_time="2026-05-01T10:05:00",
                visitor_id="visitor-2",
                session_id="session-2",
                event_type="missed_question",
                event_value="Where can I rent a stroller?",
                spot_name=None,
                route_name="Classic Route",
                raw_json=None,
            ),
            VisitorBehaviorEvent(
                scenic_area_id=None,
                event_time="2026-05-01T10:25:00",
                visitor_id="visitor-2",
                session_id="session-2",
                event_type="feedback_score",
                event_value="4",
                spot_name=None,
                route_name=None,
                raw_json=None,
            ),
        ]
    )
    test_db_session.commit()

    result = aggregate_daily_stats(test_db_session, "2026-05-01")

    assert result["total_events"] == 4
    assert result["total_visitors"] == 2
    assert result["hot_spot_top"] == [("Grand Hall", 1)]
    assert result["hot_question_top"] == [("How long is the route?", 1)]
    assert result["missed_question_top"] == [("Where can I rent a stroller?", 1)]
    assert result["route_usage"] == [("Classic Route", 2)]
    assert result["active_hour_top"] == [("09", 2), ("10", 2)]
    assert result["satisfaction_score"] == 4.0


def test_dashboard_hot_spots_defaults_to_latest_event_date(test_db_session) -> None:
    test_db_session.add_all(
        [
            VisitorBehaviorEvent(
                scenic_area_id=None,
                event_time="2026-05-01T09:00:00",
                visitor_id="old-visitor",
                session_id="old-session",
                event_type="view",
                event_value="1",
                spot_name="Old Spot",
                route_name=None,
                raw_json=None,
            ),
            VisitorBehaviorEvent(
                scenic_area_id=None,
                event_time="2026-05-03T09:00:00",
                visitor_id="new-visitor",
                session_id="new-session",
                event_type="view",
                event_value="1",
                spot_name="Latest Spot",
                route_name=None,
                raw_json=None,
            ),
        ]
    )
    test_db_session.commit()

    result = DashboardService(test_db_session).get_hot_spots()

    assert result["stat_date"] == "2026-05-03"
    assert result["items"] == [("Latest Spot", 1)]
