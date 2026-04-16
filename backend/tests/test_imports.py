from pathlib import Path

from app.importers.scenic_docx_importer import ScenicDocxImporter


def test_scenic_docx_importer_extracts_table_rows() -> None:
    importer = ScenicDocxImporter()
    rows = importer.parse(Path("tests/fixtures/scenic_spots.docx"))

    assert rows[0]["spot_code"] == "LS-001"
    assert rows[0]["name"] == "灵山大照壁"
