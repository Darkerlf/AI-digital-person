from fastapi.testclient import TestClient

from app.main import app
from app.models.conversation_message import ConversationMessage
from app.models.conversation_session import ConversationSession


def test_session_management_lists_unresolved_and_marks_fixed(test_db_session, auth_headers) -> None:
    conversation = ConversationSession(
        scenic_area_id=None,
        session_key="session-001",
        channel="miniprogram",
        visitor_id="visitor-001",
        status="completed",
    )
    test_db_session.add(conversation)
    test_db_session.commit()
    test_db_session.refresh(conversation)

    test_db_session.add_all(
        [
            ConversationMessage(
                session_id=conversation.id,
                question_text="灵山胜境有什么适合半天游的路线？",
                recognized_text="灵山胜境有什么适合半天游的路线",
                answer_text="暂时没有找到合适路线。",
                matched_document_title=None,
                latency_ms=2100,
                feedback_status="disliked",
                is_missed=True,
                resolution_status="pending",
                resolution_note=None,
            ),
            ConversationMessage(
                session_id=conversation.id,
                question_text="灵山大佛有哪些历史背景？",
                recognized_text="灵山大佛有哪些历史背景",
                answer_text="灵山大佛是灵山胜境的重要地标。",
                matched_document_title="灵山胜境：历史、文化、景点特色与个性化游览指南",
                latency_ms=1200,
                feedback_status="liked",
                is_missed=False,
                resolution_status="resolved",
                resolution_note="知识命中正常",
            ),
        ]
    )
    test_db_session.commit()

    client = TestClient(app)

    sessions_response = client.get("/api/sessions", headers=auth_headers)
    unresolved_response = client.get("/api/sessions/unresolved", headers=auth_headers)

    assert sessions_response.status_code == 200
    assert sessions_response.json()["items"][0]["session_key"] == "session-001"
    assert sessions_response.json()["items"][0]["message_count"] == 2
    assert sessions_response.json()["items"][0]["unresolved_count"] == 1

    assert unresolved_response.status_code == 200
    assert unresolved_response.json()["items"][0]["question_text"] == "灵山胜境有什么适合半天游的路线？"
    assert unresolved_response.json()["items"][0]["resolution_status"] == "pending"

    unresolved_message_id = unresolved_response.json()["items"][0]["id"]
    resolve_response = client.put(
        f"/api/sessions/messages/{unresolved_message_id}/resolve",
        headers=auth_headers,
        json={"resolution_note": "已补充半天游 FAQ 和路线模板。"},
    )

    assert resolve_response.status_code == 200
    assert resolve_response.json()["resolution_status"] == "resolved"
    assert resolve_response.json()["resolution_note"] == "已补充半天游 FAQ 和路线模板。"

    detail_response = client.get(f"/api/sessions/{conversation.id}", headers=auth_headers)

    assert detail_response.status_code == 200
    assert detail_response.json()["messages"][0]["question_text"] == "灵山胜境有什么适合半天游的路线？"
