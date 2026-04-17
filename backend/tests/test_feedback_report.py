from fastapi.testclient import TestClient

from app.main import app
from app.models.feedback_record import FeedbackRecord


def test_feedback_report_summarizes_scores_and_sentiments(test_db_session, auth_headers) -> None:
    test_db_session.add_all(
        [
            FeedbackRecord(
                scenic_area_id=None,
                source_type="qa",
                source_id=1,
                sentiment="positive",
                score=4.8,
                content="讲解很清楚，数字人回答自然。",
            ),
            FeedbackRecord(
                scenic_area_id=None,
                source_type="route",
                source_id=2,
                sentiment="negative",
                score=2.1,
                content="路线推荐不够准确，绕路太多。",
            ),
            FeedbackRecord(
                scenic_area_id=None,
                source_type="qa",
                source_id=3,
                sentiment="neutral",
                score=3.0,
                content="问答还可以，但希望增加更多景点故事。",
            ),
        ]
    )
    test_db_session.commit()

    client = TestClient(app)

    response = client.get("/api/dashboard/feedback-report", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["total_feedback"] == 3
    assert response.json()["average_score"] == 3.3
    assert response.json()["sentiment_distribution"] == {
        "positive": 1,
        "neutral": 1,
        "negative": 1,
    }
    assert "路线推荐" in response.json()["suggestion_summary"]
