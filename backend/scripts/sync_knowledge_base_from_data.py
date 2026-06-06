from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import settings
from app.core.database import SessionLocal
from app.importers.knowledge_doc_importer import KnowledgeDocImporter
from app.models import load_all_models
from app.models.knowledge_chunk import KnowledgeChunk
from app.models.knowledge_document import KnowledgeDocument
from app.models.scenic_area import ScenicArea
from app.models.scenic_spot import ScenicSpot
from app.models.visitor_behavior_event import VisitorBehaviorEvent
from app.schemas.knowledge import KnowledgeDocumentCreate
from app.services.dashboard_service import DashboardService
from app.services.import_service import ImportService
from app.services.knowledge_service import KnowledgeService
from app.tasks.knowledge_embedder import embed_all_chunks


def _source_files(data_dir: Path) -> list[Path]:
    return sorted(
        [path for path in data_dir.iterdir() if path.is_file() and not path.name.startswith("~$")],
        key=lambda path: path.name,
    )


def _ensure_area(db, name: str = "灵山胜境") -> ScenicArea:
    area = db.query(ScenicArea).filter(ScenicArea.name == name).first()
    if area:
        return area
    area = ScenicArea(code="LS", name=name, description="灵山胜境景区", status="active")
    db.add(area)
    db.commit()
    db.refresh(area)
    return area


def _delete_knowledge_document_by_source(db, source_name: str) -> int:
    docs = db.query(KnowledgeDocument).filter(KnowledgeDocument.source_name == source_name).all()
    if not docs:
        return 0
    ids = [doc.id for doc in docs]
    db.query(KnowledgeChunk).filter(KnowledgeChunk.document_id.in_(ids)).delete(synchronize_session=False)
    db.query(KnowledgeDocument).filter(KnowledgeDocument.id.in_(ids)).delete(synchronize_session=False)
    db.commit()
    return len(ids)


def _sync_knowledge_documents(db, data_dir: Path, scenic_area_id: int) -> list[str]:
    synced = []
    service = KnowledgeService(db)
    importer = KnowledgeDocImporter()
    for path in _source_files(data_dir):
        if path.suffix.lower() not in {".docx", ".xlsx", ".txt"}:
            continue
        _delete_knowledge_document_by_source(db, path.name)
        payload = importer.parse(path)
        service.create_document(
            KnowledgeDocumentCreate(
                scenic_area_id=scenic_area_id,
                title=payload["title"],
                doc_type=payload["doc_type"],
                source_name=payload["source_name"],
                content_text=payload["content_text"],
            )
        )
        synced.append(path.name)
    return synced


def _sync_scenic_spots(db, data_dir: Path) -> int:
    fake = db.query(ScenicSpot).filter(ScenicSpot.spot_code == "景点ID").all()
    for spot in fake:
        db.delete(spot)
    if fake:
        db.commit()

    structured = next((path for path in _source_files(data_dir) if path.name.endswith("景点结构化数据集.docx")), None)
    if structured is None:
        return 0
    job = ImportService(db).run_scenic_import(str(structured))
    return job.success_count


def _sync_behavior_events(db, data_dir: Path, import_behavior_events: bool, reload_behavior_events: bool) -> int:
    xlsx = next((path for path in _source_files(data_dir) if path.suffix.lower() == ".xlsx"), None)
    if xlsx is None:
        return 0

    existing = db.query(VisitorBehaviorEvent).count()
    if not import_behavior_events:
        return existing
    if existing and not reload_behavior_events:
        return existing
    if existing and reload_behavior_events:
        db.query(VisitorBehaviorEvent).delete(synchronize_session=False)
        db.commit()

    job = DashboardService(db).import_behavior_events(str(xlsx))
    return job.success_count


async def _embed_missing_chunks(db) -> int:
    if not settings.dashscope_api_key:
        return 0
    return await embed_all_chunks(db)


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync local scenic source documents into the current knowledge database.")
    parser.add_argument(
        "--data-dir",
        default=str(PROJECT_ROOT / "data"),
        help="Source data directory containing the three scenic documents.",
    )
    parser.add_argument(
        "--import-behavior-events",
        action="store_true",
        help="Import xlsx rows into visitor_behavior_event. This can be slow for large workbooks.",
    )
    parser.add_argument(
        "--reload-behavior-events",
        action="store_true",
        help="Delete existing visitor behavior events before importing the xlsx file.",
    )
    parser.add_argument(
        "--skip-embeddings",
        action="store_true",
        help="Skip embedding generation for newly-created knowledge chunks.",
    )
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        raise SystemExit(f"Data directory not found: {data_dir}")

    load_all_models()
    with SessionLocal() as db:
        area = _ensure_area(db)
        scenic_count = _sync_scenic_spots(db, data_dir)
        docs = _sync_knowledge_documents(db, data_dir, area.id)
        behavior_count = _sync_behavior_events(db, data_dir, args.import_behavior_events, args.reload_behavior_events)
        embedded = 0
        if not args.skip_embeddings:
            embedded = asyncio.run(_embed_missing_chunks(db))

        print("Sync complete")
        print(f"Scenic spots synced: {scenic_count}")
        print(f"Knowledge documents synced: {len(docs)}")
        for source_name in docs:
            print(f"- {source_name}")
        print(f"Behavior events available: {behavior_count}")
        print(f"New embeddings generated: {embedded}")


if __name__ == "__main__":
    main()
