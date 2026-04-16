from fastapi.testclient import TestClient

from app.main import app


def test_create_document_and_generate_chunks(test_db_session, auth_headers) -> None:
    client = TestClient(app)

    area_response = client.post(
        "/api/scenic-areas",
        headers=auth_headers,
        json={"code": "NH", "name": "拈花湾", "description": "小镇", "status": "active"},
    )

    response = client.post(
        "/api/knowledge/documents/upload",
        headers=auth_headers,
        json={
            "scenic_area_id": area_response.json()["id"],
            "title": "灵山导览词",
            "doc_type": "txt",
            "source_name": "guide.txt",
            "content_text": "第一段内容。" * 80,
        },
    )

    assert response.status_code == 201

    chunks = client.get(f"/api/knowledge/documents/{response.json()['id']}/chunks", headers=auth_headers)
    assert chunks.status_code == 200
    assert len(chunks.json()["items"]) >= 1
