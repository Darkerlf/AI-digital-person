from pathlib import Path

from app.importers.parsers.excel_parser import read_excel_rows


class BehaviorExcelImporter:
    def parse(self, path: Path) -> list[dict[str, object]]:
        return read_excel_rows(path)
