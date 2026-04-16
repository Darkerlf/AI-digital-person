from pathlib import Path

from openpyxl import load_workbook


def read_excel_rows(path: Path) -> list[dict[str, object]]:
    workbook = load_workbook(path)
    sheet = workbook.active
    rows = list(sheet.iter_rows(values_only=True))
    header = [str(item).strip() for item in rows[0]]
    return [dict(zip(header, row, strict=False)) for row in rows[1:]]
