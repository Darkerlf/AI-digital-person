from pathlib import Path

from app.importers.parsers.docx_parser import read_docx_tables


HEADER_MAP = {
    "景区名称": "scenic_area_name",
    "景点ID": "spot_code",
    "景点名称": "name",
    "具体位置": "location_text",
    "建筑/景观参数": "parameters_text",
    "核心功能": "core_function",
    "文化内涵": "cultural_value",
    "详细介绍": "detail_intro",
    "游玩亮点": "highlights",
    "演艺/开放信息": "performance_info",
    "备注": "remarks",
}

REQUIRED_HEADERS = {"景区名称", "景点ID", "景点名称"}


class ScenicDocxImporter:
    def parse(self, path: Path) -> list[dict[str, str]]:
        rows = read_docx_tables(path)
        header: list[str] | None = None
        result: list[dict[str, str]] = []

        for row in rows:
            stripped = [cell.strip() for cell in row]
            if REQUIRED_HEADERS.issubset(set(stripped)):
                header = stripped
                continue
            if header is None or not any(stripped):
                continue

            record = dict(zip(header, stripped, strict=False))
            spot_code = record.get("景点ID", "").strip()
            name = record.get("景点名称", "").strip()
            if not spot_code or not name or spot_code == "景点ID":
                continue

            result.append(
                {
                    target: record.get(source, "")
                    for source, target in HEADER_MAP.items()
                }
            )
        return result
