from fastapi.testclient import TestClient

from app.main import app
from app.models.conversation_message import ConversationMessage
from app.models.conversation_session import ConversationSession
from app.models.scenic_area import ScenicArea


def create_unresolved_message_seed(test_db_session) -> tuple[int, int, int]:
    scenic_area = ScenicArea(code="LS", name="灵山胜境", description="示范景区", status="active")
    test_db_session.add(scenic_area)
    test_db_session.commit()
    test_db_session.refresh(scenic_area)

    conversation = ConversationSession(
        scenic_area_id=scenic_area.id,
        session_key="session-001",
        channel="miniprogram",
        visitor_id="visitor-001",
        status="completed",
    )
    test_db_session.add(conversation)
    test_db_session.commit()
    test_db_session.refresh(conversation)

    message = ConversationMessage(
        session_id=conversation.id,
        question_text="景区半日游路线怎么安排？",
        recognized_text="景区半日游路线怎么安排",
        answer_text="暂时没有找到合适路线。",
        matched_document_title=None,
        latency_ms=2100,
        feedback_status="disliked",
        is_missed=True,
        resolution_status="pending",
        resolution_note=None,
    )
    test_db_session.add(message)
    test_db_session.commit()
    test_db_session.refresh(message)
    return scenic_area.id, conversation.id, message.id


def create_open_correction_task(
    client: TestClient,
    headers: dict[str, str],
    message_id: int,
    correction_type: str,
) -> int:
    response = client.post(
        "/api/knowledge/correction-tasks",
        headers=headers,
        json={
            "source_message_id": message_id,
            "correction_type": correction_type,
            "resolution_note": "待补知识。",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_create_faq_correction_task_from_unresolved_message(test_db_session, content_auth_headers) -> None:
    _, _, message_id = create_unresolved_message_seed(test_db_session)
    client = TestClient(app)

    response = client.post(
        "/api/knowledge/correction-tasks",
        headers=content_auth_headers,
        json={
            "source_message_id": message_id,
            "correction_type": "faq",
            "resolution_note": "需要补 FAQ。",
        },
    )

    assert response.status_code == 201
    assert response.json()["status"] == "open"
    assert response.json()["question_text"] == "景区半日游路线怎么安排？"
    assert response.json()["correction_type"] == "faq"


def test_reject_duplicate_open_correction_task_for_same_message(test_db_session, content_auth_headers) -> None:
    _, _, message_id = create_unresolved_message_seed(test_db_session)
    client = TestClient(app)
    payload = {
        "source_message_id": message_id,
        "correction_type": "faq",
        "resolution_note": "第一次创建",
    }

    first_response = client.post("/api/knowledge/correction-tasks", headers=content_auth_headers, json=payload)
    second_response = client.post("/api/knowledge/correction-tasks", headers=content_auth_headers, json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_link_faq_and_resolve_correction_task(test_db_session, content_auth_headers) -> None:
    scenic_area_id, _, message_id = create_unresolved_message_seed(test_db_session)
    client = TestClient(app)
    task_id = create_open_correction_task(client, content_auth_headers, message_id, "faq")

    faq_response = client.post(
        "/api/knowledge/faqs",
        headers=content_auth_headers,
        params={"correction_task_id": task_id},
        json={
            "scenic_area_id": scenic_area_id,
            "question": "景区半日游路线怎么安排？",
            "answer": "建议先游览核心景点，再安排文化体验。",
            "category": "路线",
            "priority": 10,
            "status": "active",
            "source": "correction-task",
        },
    )

    assert faq_response.status_code == 201

    detail_response = client.get(f"/api/knowledge/correction-tasks/{task_id}", headers=content_auth_headers)
    assert detail_response.status_code == 200
    assert detail_response.json()["linked_faq_id"] == faq_response.json()["id"]
    assert detail_response.json()["status"] == "resolved"


def test_link_document_and_resolve_updates_message_state(test_db_session, content_auth_headers) -> None:
    scenic_area_id, _, message_id = create_unresolved_message_seed(test_db_session)
    client = TestClient(app)
    task_id = create_open_correction_task(client, content_auth_headers, message_id, "document")

    document_response = client.post(
        "/api/knowledge/documents/upload",
        headers=content_auth_headers,
        params={"correction_task_id": task_id},
        json={
            "scenic_area_id": scenic_area_id,
            "title": "景区半日游路线说明",
            "doc_type": "markdown",
            "source_name": "manual-entry",
            "content_text": "推荐路线：先核心景点，后体验项目。",
        },
    )

    assert document_response.status_code == 201

    detail_response = client.get(f"/api/knowledge/correction-tasks/{task_id}", headers=content_auth_headers)
    assert detail_response.status_code == 200
    assert detail_response.json()["linked_document_id"] == document_response.json()["id"]
    assert detail_response.json()["status"] == "resolved"

    unresolved_response = client.get("/api/sessions/unresolved", headers=content_auth_headers)
    assert unresolved_response.status_code == 200
    assert all(item["id"] != message_id for item in unresolved_response.json()["items"])
