import json
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.models.conversation_message import ConversationMessage
from app.services.intent_classifier import Intent


def test_chat_stream_feedback_binds_to_generated_message(test_db_session) -> None:
    client = TestClient(app)

    with patch("app.services.chat_service.IntentClassifier.classify", new_callable=AsyncMock, return_value=Intent.SCENIC_QA):
        with patch("app.services.chat_service.RAGPipeline") as MockRAG:
            instance = MockRAG.return_value

            async def fake_stream(*args, **kwargs):
                yield "Welcome"
                yield " to Lingshan"

            instance.answer_stream = fake_stream

            with client.stream("POST", "/api/tourist/chat/stream", json={"message": "Introduce Lingshan"}) as response:
                assert response.status_code == 200
                response.read()
                frames = [
                    json.loads(line.removeprefix("data: "))
                    for line in response.text.splitlines()
                    if line.startswith("data: {")
                ]

    meta_frame = next(frame for frame in frames if frame["text"].startswith("\n__meta__:"))
    meta = json.loads(meta_frame["text"].removeprefix("\n__meta__:"))
    assert meta["message_id"] > 0

    feedback_response = client.post(
        "/api/tourist/feedback",
        json={
            "session_id": meta["session_id"],
            "message_id": meta["message_id"],
            "sentiment": "negative",
        },
    )

    assert feedback_response.status_code == 200
    message = test_db_session.get(ConversationMessage, meta["message_id"])
    assert message.feedback_status == "disliked"

