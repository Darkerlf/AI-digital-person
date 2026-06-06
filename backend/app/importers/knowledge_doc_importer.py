from pathlib import Path

from app.importers.behavior_excel_importer import BehaviorExcelImporter
from app.importers.parsers.docx_parser import read_docx_blocks
from app.importers.parsers.text_parser import read_text


class KnowledgeDocImporter:
    def parse(self, path: Path) -> dict[str, str]:
        suffix = path.suffix.lower()
        if suffix == ".docx":
            content_text = read_docx_blocks(path)
            doc_type = "docx"
        elif suffix == ".xlsx":
            content_text = BehaviorExcelImporter().build_knowledge_summary(path)
            doc_type = "xlsx"
        else:
            content_text = read_text(path)
            doc_type = suffix.lstrip(".") or "txt"
        return {
            "title": path.stem,
            "doc_type": doc_type,
            "source_name": path.name,
            "content_text": content_text,
        }
