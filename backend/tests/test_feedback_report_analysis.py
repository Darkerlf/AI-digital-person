from datetime import datetime

from fastapi.testclient import TestClient

from app.main import app
from app.models.feedback_record import FeedbackRecord
from app.models.route_recommendation_record import RouteRecommendationRecord
from app.models.scenic_area import ScenicArea


def test_feedback_report_filters_and_returns_trend_topn_reasons_and_route_analysis(
    test_db_session,
    auth_headers,
) -> None:
    area = ScenicArea(code="AREA-FEEDBACK", name="Feedback Area", status="active")
    test_db_session.add(area)
    test_db_session.flush()
    route_record = RouteRecommendationRecord(
        scenic_area_id=area.id,
        visitor_id="visitor-1",
        session_id="session-1",
        source="route_template",
        matched_template_name="Classic Route",
        fallback_used=False,
        request_json={},
        response_json={},
    )
    test_db_session.add(route_record)
    test_db_session.flush()
    test_db_session.add_all(
        [
            FeedbackRecord(
                scenic_area_id=area.id,
                source_type="route",
                source_id=route_record.id,
                sentiment="negative",
                score=2,
                content="route detour too long and route recommendation inaccurate",
                created_at=datetime(2026, 6, 1, 9, 0, 0),
            ),
            FeedbackRecord(
                scenic_area_id=area.id,
                source_type="chat",
                source_id=99,
                sentiment="positive",
                score=5,
                content="answer is clear",
                created_at=datetime(2026, 6, 1, 10, 0, 0),
            ),
            FeedbackRecord(
                scenic_area_id=None,
                source_type="route",
                source_id=None,
                sentiment="negative",
                score=1,
                content="outside area should be filtered",
                created_at=datetime(2026, 6, 2, 10, 0, 0),
            ),
        ]
    )
    test_db_session.commit()

    client = TestClient(app)
    response = client.get(
        (
            "/api/dashboard/feedback-report"
            f"?scenic_area_id={area.id}&source_type=route"
            "&start_date=2026-06-01&end_date=2026-06-01"
        ),
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total_feedback"] == 1
    assert data["feedback_trend"] == [
        {"date": "2026-06-01", "total_feedback": 1, "average_score": 2.0, "negative_count": 1}
    ]
    assert data["focus_top_n"][0] == {"name": "route", "count": 2}
    assert data["complaint_top_n"][0] == {"name": "route", "count": 2}
    assert data["negative_reason_top_n"][0] == {"reason": "route", "count": 1}
    assert data["route_feedback_analysis"] == [
        {
            "route_name": "Classic Route",
            "total_feedback": 1,
            "average_score": 2.0,
            "negative_count": 1,
        }
    ]
