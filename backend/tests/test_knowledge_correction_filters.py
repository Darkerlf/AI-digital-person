from fastapi.testclient import TestClient

from app.main import app
from app.models.conversation_message import ConversationMessage
from app.models.conversation_session import ConversationSession
from app.models.scenic_area import ScenicArea


def test_list_correction_tasks_filters_by_status_and_type(test_db_session, auth_headers) -> None:
    area = ScenicArea(code="KCF", name="Correction Filter Area", description="Filter seed", status="active")
    test_db_session.add(area)
    test_db_session.commit()
    test_db_session.refresh(area)

    session = ConversationSession(
        scenic_area_id=area.id,
        session_key="correction-filter-session",
        channel="miniprogram",
        visitor_id="visitor-filter",
        status="completed",
    )
    test_db_session.add(session)
    test_db_session.commit()
    test_db_session.refresh(session)

    faq_message = ConversationMessage(
        session_id=session.id,
        question_text="FAQ missing question",
        recognized_text="FAQ missing question",
        answer_text="No answer",
        feedback_status="disliked",
        is_missed=True,
        resolution_status="pending",
    )
    document_message = ConversationMessage(
        session_id=session.id,
        question_text="Document missing question",
        recognized_text="Document missing question",
        answer_text="No document",
        feedback_status="disliked",
        is_missed=True,
        resolution_status="pending",
    )
    test_db_session.add_all([faq_message, document_message])
    test_db_session.commit()
    test_db_session.refresh(faq_message)
    test_db_session.refresh(document_message)

    client = TestClient(app)
    faq_response = client.post(
        "/api/knowledge/correction-tasks",
        headers=auth_headers,
        json={"source_message_id": faq_message.id, "correction_type": "faq"},
    )
    document_response = client.post(
        "/api/knowledge/correction-tasks",
        headers=auth_headers,
        json={"source_message_id": document_message.id, "correction_type": "document"},
    )
    assert faq_response.status_code == 201
    assert document_response.status_code == 201

    filtered_response = client.get(
        "/api/knowledge/correction-tasks",
        headers=auth_headers,
        params={"status": "open", "correction_type": "document"},
    )

    assert filtered_response.status_code == 200
    items = filtered_response.json()["items"]
    assert [item["id"] for item in items] == [document_response.json()["id"]]
