from pathlib import Path

from app.importers.parsers.docx_parser import read_docx_tables


class ScenicDocxImporter:
    def parse(self, path: Path) -> list[dict[str, str]]:
        rows = read_docx_tables(path)
        header = rows[0]
        result: list[dict[str, str]] = []
        for row in rows[1:]:
            record = dict(zip(header, row, strict=False))
            result.append(
                {
                    "scenic_area_name": record["景区名称"],
                    "spot_code": record["景点ID"],
                    "name": record["景点名称"],
                    "location_text": record["具体位置"],
                    "parameters_text": record["建筑/景观参数"],
                    "core_function": record["核心功能"],
                    "cultural_value": record["文化内涵"],
                    "detail_intro": record["详细介绍"],
                    "highlights": record["游玩亮点"],
                    "performance_info": record["演艺/开放信息"],
                    "remarks": record["备注"],
                }
            )
        return result
