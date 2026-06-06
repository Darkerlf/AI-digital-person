from fastapi.testclient import TestClient

from app.main import app
from app.models.conversation_message import ConversationMessage
from app.models.conversation_session import ConversationSession
from app.models.feedback_record import FeedbackRecord


def test_feedback_report_includes_latest_answer_feedback_details(test_db_session, auth_headers) -> None:
    session = ConversationSession(session_key="tourist_feedback", channel="miniprogram", status="active")
    test_db_session.add(session)
    test_db_session.flush()
    message = ConversationMessage(
        session_id=session.id,
        question_text="How much is the ticket?",
        answer_text="The ticket price depends on the current scenic-area notice.",
        feedback_status="disliked",
    )
    test_db_session.add(message)
    test_db_session.flush()
    test_db_session.add(
        FeedbackRecord(
            source_type="chat",
            source_id=message.id,
            sentiment="negative",
            score=2,
            content="The answer needs a more precise ticket price.",
        )
    )
    test_db_session.commit()

    response = TestClient(app).get("/api/dashboard/feedback-report", headers=auth_headers)

    assert response.status_code == 200
    latest = response.json()["latest_feedback"][0]
    assert latest["message_id"] == message.id
    assert latest["question_text"] == "How much is the ticket?"
    assert latest["answer_text"].startswith("The ticket price")
    assert latest["content"] == "The answer needs a more precise ticket price."

