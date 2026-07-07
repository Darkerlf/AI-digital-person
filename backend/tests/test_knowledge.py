from fastapi.testclient import TestClient

from app.main import app
from app.models.knowledge_chunk import KnowledgeChunk


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


def test_list_chunks_does_not_serialize_embedding_vectors(test_db_session, auth_headers) -> None:
    client = TestClient(app)
    area_response = client.post(
        "/api/scenic-areas",
        headers=auth_headers,
        json={"code": "EMBED", "name": "Embedding Area", "status": "active"},
    )
    create_response = client.post(
        "/api/knowledge/documents/upload",
        headers=auth_headers,
        json={
            "scenic_area_id": area_response.json()["id"],
            "title": "Embedding Guide",
            "doc_type": "markdown",
            "source_name": "embedding.md",
            "content_text": "embedding vector chunk content " * 40,
        },
    )
    document_id = create_response.json()["id"]
    chunk = test_db_session.query(KnowledgeChunk).filter_by(document_id=document_id).first()
    chunk.embedding_vector = b"\x9b\x00\xff"
    test_db_session.commit()

    response = client.get(f"/api/knowledge/documents/{document_id}/chunks", headers=auth_headers)

    assert response.status_code == 200
    item = response.json()["items"][0]
    assert "embedding_vector" not in item
    assert "embedding vector chunk content" in item["chunk_text"]


def test_update_document_content_rebuilds_chunks_and_increments_version(test_db_session, auth_headers) -> None:
    client = TestClient(app)
    area_response = client.post(
        "/api/scenic-areas",
        headers=auth_headers,
        json={"code": "DOC-UP", "name": "Doc Update Area", "status": "active"},
    )
    create_response = client.post(
        "/api/knowledge/documents/upload",
        headers=auth_headers,
        json={
            "scenic_area_id": area_response.json()["id"],
            "title": "Original Guide",
            "doc_type": "txt",
            "source_name": "original.txt",
            "content_text": "original chunk content " * 40,
        },
    )
    document_id = create_response.json()["id"]
    original_chunks = client.get(f"/api/knowledge/documents/{document_id}/chunks", headers=auth_headers).json()["items"]

    response = client.put(
        f"/api/knowledge/documents/{document_id}",
        headers=auth_headers,
        json={
            "title": "Updated Guide",
            "content_text": "updated rebuilt chunk content " * 40,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Guide"
    assert data["version"] == 2
    chunks = client.get(f"/api/knowledge/documents/{document_id}/chunks", headers=auth_headers).json()["items"]
    assert chunks
    assert chunks[0]["chunk_text"] != original_chunks[0]["chunk_text"]
    assert "updated rebuilt chunk content" in chunks[0]["chunk_text"]


def test_update_document_status_without_content_does_not_increment_version(test_db_session, auth_headers) -> None:
    client = TestClient(app)
    area_response = client.post(
        "/api/scenic-areas",
        headers=auth_headers,
        json={"code": "DOC-STATUS", "name": "Doc Status Area", "status": "active"},
    )
    create_response = client.post(
        "/api/knowledge/documents/upload",
        headers=auth_headers,
        json={
            "scenic_area_id": area_response.json()["id"],
            "title": "Status Guide",
            "doc_type": "txt",
            "source_name": "status.txt",
            "content_text": "status chunk content " * 40,
        },
    )
    document_id = create_response.json()["id"]

    response = client.put(
        f"/api/knowledge/documents/{document_id}",
        headers=auth_headers,
        json={"status": "inactive"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "inactive"
    assert response.json()["version"] == 1


def test_delete_document_removes_document_and_chunks(test_db_session, auth_headers) -> None:
    client = TestClient(app)
    area_response = client.post(
        "/api/scenic-areas",
        headers=auth_headers,
        json={"code": "DOC-DEL", "name": "Doc Delete Area", "status": "active"},
    )
    create_response = client.post(
        "/api/knowledge/documents/upload",
        headers=auth_headers,
        json={
            "scenic_area_id": area_response.json()["id"],
            "title": "Delete Guide",
            "doc_type": "txt",
            "source_name": "delete.txt",
            "content_text": "delete chunk content " * 40,
        },
    )
    document_id = create_response.json()["id"]

    response = client.delete(f"/api/knowledge/documents/{document_id}", headers=auth_headers)

    assert response.status_code == 204
    assert client.get(f"/api/knowledge/documents/{document_id}", headers=auth_headers).status_code == 404
    assert test_db_session.query(KnowledgeChunk).filter_by(document_id=document_id).count() == 0
