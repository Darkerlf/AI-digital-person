from pathlib import Path

from docx import Document


def read_docx_tables(path: Path) -> list[list[str]]:
    document = Document(str(path))
    rows: list[list[str]] = []
    for table in document.tables:
        for row in table.rows:
            rows.append([cell.text.strip() for cell in row.cells])
    return rows


def read_docx_paragraphs(path: Path) -> str:
    document = Document(str(path))
    return "\n".join(paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip())
