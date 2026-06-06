from pathlib import Path
from statistics import mean

from app.importers.parsers.excel_parser import read_excel_rows


NUMERIC_FIELDS = [
    "stay_duration",
    "ticket_cost",
    "food_cost",
    "shopping_cost",
    "transport_cost",
    "entertainment_cost",
    "total_cost",
    "group_size",
    "satisfaction",
]


def _as_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _as_float(value: object) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


class BehaviorExcelImporter:
    def parse(self, path: Path) -> list[dict[str, object]]:
        return [self._normalize_row(row) for row in read_excel_rows(path)]

    def _normalize_row(self, row: dict[str, object]) -> dict[str, object]:
        event_time = _as_text(row.get("event_time") or row.get("时间") or row.get("date") or row.get("日期") or row.get("visit_date"))
        visitor_id = _as_text(row.get("visitor_id") or row.get("用户ID") or row.get("tourist_id"))
        session_id = _as_text(row.get("session_id") or row.get("会话ID") or row.get("tourist_id"))
        spot_name = _as_text(row.get("spot_name") or row.get("景点名称") or row.get("attraction_name"))
        route_name = _as_text(row.get("route_name") or row.get("路线名称"))
        stay_duration = row.get("stay_duration")
        event_type = _as_text(row.get("event_type") or row.get("行为类型")) or "visit"
        event_value = _as_text(row.get("event_value") or row.get("行为值") or stay_duration)

        normalized = dict(row)
        normalized.update(
            {
                "event_time": event_time,
                "visitor_id": visitor_id,
                "session_id": session_id,
                "event_type": event_type,
                "event_value": event_value,
                "spot_name": spot_name,
                "route_name": route_name,
            }
        )
        return normalized

    def build_knowledge_summary(self, path: Path) -> str:
        rows = self.parse(path)
        by_spot: dict[str, list[dict[str, object]]] = {}
        for row in rows:
            spot_name = _as_text(row.get("spot_name") or row.get("attraction_name"))
            if spot_name:
                by_spot.setdefault(spot_name, []).append(row)

        lines = [
            f"数据来源：{path.name}",
            f"游客行为数据总记录数：{len(rows)}",
            "字段说明：ticket_cost 为门票消费，total_cost 为总消费，stay_duration 为停留时长，satisfaction 为满意度。",
        ]
        for spot_name, spot_rows in sorted(by_spot.items(), key=lambda item: len(item[1]), reverse=True):
            metrics = self._summarize_spot_metrics(spot_rows)
            if not metrics:
                continue
            lines.append(f"景点：{spot_name}")
            lines.extend(f"- {metric}" for metric in metrics)
        return "\n".join(lines)

    def _summarize_spot_metrics(self, rows: list[dict[str, object]]) -> list[str]:
        labels = {
            "stay_duration": "平均停留时长",
            "ticket_cost": "平均门票消费",
            "food_cost": "平均餐饮消费",
            "shopping_cost": "平均购物消费",
            "transport_cost": "平均交通消费",
            "entertainment_cost": "平均娱乐消费",
            "total_cost": "平均总消费",
            "group_size": "平均同行人数",
            "satisfaction": "平均满意度",
        }
        units = {
            "stay_duration": "分钟",
            "ticket_cost": "元",
            "food_cost": "元",
            "shopping_cost": "元",
            "transport_cost": "元",
            "entertainment_cost": "元",
            "total_cost": "元",
            "group_size": "人",
            "satisfaction": "分",
        }
        metrics = [f"记录数 {len(rows)} 条"]
        for field in NUMERIC_FIELDS:
            values = [_as_float(row.get(field)) for row in rows]
            values = [value for value in values if value is not None]
            if values:
                metrics.append(f"{labels[field]} {mean(values):.2f} {units[field]}")
        return metrics
