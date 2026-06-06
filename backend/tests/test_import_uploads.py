from fastapi.testclient import TestClient

from app.main import app
from app.models.knowledge_document import KnowledgeDocument
from app.models.scenic_area import ScenicArea


def test_upload_knowledge_document_import_creates_job_with_original_filename(
    test_db_session,
    content_auth_headers,
) -> None:
    area = ScenicArea(code="AREA-UPLOAD", name="Upload Area", status="active")
    test_db_session.add(area)
    test_db_session.commit()

    client = TestClient(app)
    response = client.post(
        f"/api/imports/knowledge-docs/upload?scenic_area_id={area.id}",
        headers=content_auth_headers,
        files={"file": ("browser-guide.txt", b"Browser uploaded guide content", "text/plain")},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["source_file_name"] == "browser-guide.txt"
    assert data["total_count"] == 1

    document = test_db_session.query(KnowledgeDocument).filter_by(source_name="browser-guide.txt").one()
    assert document.title == "browser-guide"
    assert document.content_text == "Browser uploaded guide content"
