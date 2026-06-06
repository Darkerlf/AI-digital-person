import math
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.scenic_spot import ScenicSpot
from app.models.service_poi import ServicePOI
from app.schemas.tourist import WalkGuideRequest
from app.services.tencent_map_client import TencentMapClient
from app.services.tourist_experience_service import FALLBACK_SERVICE_POIS, SCENIC_SPOT_GCJ02_COORDINATES

WALKING_SPEED_METERS_PER_MINUTE = 70
ALONG_ROUTE_THRESHOLD_METERS = 90

SERVICE_NEED_CATEGORY_ALIASES = {
    "卫生间": "toilet",
    "厕所": "toilet",
    "公共厕所": "toilet",
    "餐饮": "restaurant",
    "吃饭": "restaurant",
    "游客服务中心": "service_center",
    "服务中心": "service_center",
    "停车": "parking",
    "停车场": "parking",
}


class WalkGuideService:
    def __init__(self, db: Session, map_client: Any | None = None) -> None:
        self.db = db
        self.map_client = map_client or TencentMapClient()

    def build(self, payload: WalkGuideRequest | dict) -> dict:
        data = payload.model_dump() if hasattr(payload, "model_dump") else dict(payload)
        warnings: list[str] = []
        stops = self._resolve_stops(data, warnings)
        if data.get("start_location") and stops:
            start_location = self._coerce_valid_point(data["start_location"])
            if start_location is None:
                warnings.append("当前位置坐标异常，已忽略当前位置并按原路线导览。")
            else:
                stops = [
                    {
                        "scenic_spot_id": None,
                        "name": "当前位置",
                        "latitude": start_location["latitude"],
                        "longitude": start_location["longitude"],
                    },
                    *stops,
                ]

        legs = []
        full_polyline: list[dict] = []
        fallback_used = False
        for start, end in zip(stops, stops[1:]):
            leg = self._build_leg(start, end)
            if leg["fallback_used"]:
                fallback_used = True
                warnings.append(f"腾讯步行路线暂不可用，已使用直线连接：{start['name']} 到 {end['name']}。")
            legs.append(leg)
            if not full_polyline:
                full_polyline.extend(leg["polyline"])
            else:
                full_polyline.extend(leg["polyline"][1:])

        total_distance = sum(leg["distance_meters"] for leg in legs)
        total_duration = sum(leg["duration_minutes"] for leg in legs)
        service_pois = self._filter_service_pois_along_route(
            scenic_area_id=data.get("scenic_area_id"),
            polyline=full_polyline,
            service_needs=list(data.get("service_needs") or []),
        )
        return {
            "total_distance_meters": total_distance,
            "total_duration_minutes": total_duration,
            "polyline": full_polyline,
            "legs": legs,
            "stops": stops,
            "service_pois": service_pois,
            "fallback_used": fallback_used,
            "warnings": warnings,
        }

    def _resolve_stops(self, data: dict, warnings: list[str]) -> list[dict]:
        scenic_area_id = data.get("scenic_area_id")
        db_spots = self._list_spots(scenic_area_id)
        by_id = {spot.id: spot for spot in db_spots}
        by_name = {self._normalize_name(spot.name): spot for spot in db_spots}

        stops = []
        for route_spot in data.get("spots") or []:
            spot = None
            spot_id = route_spot.get("scenic_spot_id")
            if isinstance(spot_id, int):
                spot = by_id.get(spot_id)
            if spot is None:
                spot = by_name.get(self._normalize_name(route_spot.get("name") or ""))
            resolved = self._resolved_stop(route_spot, spot)
            if resolved is None:
                warnings.append(f"路线点缺少坐标，已跳过：{route_spot.get('name') or '未命名景点'}。")
                continue
            stops.append(resolved)
        return stops

    def _resolved_stop(self, route_spot: dict, spot: ScenicSpot | None) -> dict | None:
        name = route_spot.get("name") or (spot.name if spot else "")
        latitude = spot.latitude if spot else None
        longitude = spot.longitude if spot else None
        if latitude is None or longitude is None:
            preset = SCENIC_SPOT_GCJ02_COORDINATES.get(name) or (SCENIC_SPOT_GCJ02_COORDINATES.get(spot.name) if spot else None)
            if preset:
                latitude = preset["latitude"]
                longitude = preset["longitude"]
        if latitude is None or longitude is None:
            return None
        point = self._coerce_valid_point({"latitude": latitude, "longitude": longitude})
        if point is None:
            return None
        return {
            "scenic_spot_id": spot.id if spot else route_spot.get("scenic_spot_id"),
            "name": name,
            "latitude": point["latitude"],
            "longitude": point["longitude"],
        }

    def _build_leg(self, start: dict, end: dict) -> dict:
        from_point = {"latitude": start["latitude"], "longitude": start["longitude"]}
        to_point = {"latitude": end["latitude"], "longitude": end["longitude"]}
        route = self.map_client.direction_walking(from_point=from_point, to_point=to_point)
        if route and self._is_valid_polyline(route.get("polyline") or []):
            distance = int(route["distance_meters"])
            duration = max(1, int(route["duration_minutes"]))
            polyline = route["polyline"]
            provider = route["provider"]
            fallback = False
        else:
            distance = max(1, round(self._distance_meters(from_point, to_point)))
            duration = max(1, math.ceil(distance / WALKING_SPEED_METERS_PER_MINUTE))
            polyline = [from_point, to_point]
            provider = "straight_line_fallback"
            fallback = True
        return {
            "from_name": start["name"],
            "to_name": end["name"],
            "distance_meters": distance,
            "duration_minutes": duration,
            "polyline": polyline,
            "provider": provider,
            "fallback_used": fallback,
        }

    def _filter_service_pois_along_route(
        self,
        *,
        scenic_area_id: int | None,
        polyline: list[dict],
        service_needs: list[str],
    ) -> list[dict]:
        if not polyline:
            return []
        categories = self._service_categories(service_needs)
        pois = self._list_service_pois(scenic_area_id)
        selected = []
        for poi in pois:
            if categories and poi.category not in categories:
                continue
            if poi.latitude is None or poi.longitude is None:
                continue
            point = self._coerce_valid_point({"latitude": poi.latitude, "longitude": poi.longitude})
            if point is None:
                continue
            if self._distance_to_polyline_meters(point, polyline) <= ALONG_ROUTE_THRESHOLD_METERS:
                selected.append(self._service_poi_summary(poi))
        return selected

    def _list_spots(self, scenic_area_id: int | None) -> list[ScenicSpot]:
        statement = select(ScenicSpot).where(ScenicSpot.open_status == "open")
        if scenic_area_id:
            statement = statement.where(ScenicSpot.scenic_area_id == scenic_area_id)
        return list(self.db.execute(statement).scalars().all())

    def _list_service_pois(self, scenic_area_id: int | None) -> list[ServicePOI]:
        statement = select(ServicePOI).where(ServicePOI.status == "active")
        if scenic_area_id:
            statement = statement.where(ServicePOI.scenic_area_id == scenic_area_id)
        rows = list(self.db.execute(statement).scalars().all())
        if rows:
            return rows
        return [ServicePOI(**item) for item in FALLBACK_SERVICE_POIS]

    @staticmethod
    def _service_categories(service_needs: list[str]) -> set[str]:
        return {
            SERVICE_NEED_CATEGORY_ALIASES[item]
            for item in service_needs
            if item in SERVICE_NEED_CATEGORY_ALIASES
        }

    @staticmethod
    def _service_poi_summary(row: ServicePOI) -> dict:
        return {
            "id": row.id,
            "name": row.name,
            "category": row.category,
            "area_text": row.area_text,
            "description": row.description,
            "open_hours": row.open_hours,
            "latitude": row.latitude,
            "longitude": row.longitude,
        }

    @classmethod
    def _distance_to_polyline_meters(cls, point: dict, polyline: list[dict]) -> float:
        if len(polyline) == 1:
            return cls._distance_meters(point, polyline[0])
        return min(
            cls._distance_to_segment_meters(point, start, end)
            for start, end in zip(polyline, polyline[1:])
        )

    @classmethod
    def _distance_to_segment_meters(cls, point: dict, start: dict, end: dict) -> float:
        origin_lat = math.radians(point["latitude"])
        x1, y1 = cls._project(start, origin_lat)
        x2, y2 = cls._project(end, origin_lat)
        xp, yp = cls._project(point, origin_lat)
        dx = x2 - x1
        dy = y2 - y1
        if dx == 0 and dy == 0:
            return math.hypot(xp - x1, yp - y1)
        ratio = max(0.0, min(1.0, ((xp - x1) * dx + (yp - y1) * dy) / (dx * dx + dy * dy)))
        closest_x = x1 + ratio * dx
        closest_y = y1 + ratio * dy
        return math.hypot(xp - closest_x, yp - closest_y)

    @staticmethod
    def _project(point: dict, origin_lat_radians: float) -> tuple[float, float]:
        meters_per_degree_lat = 111_320
        meters_per_degree_lng = 111_320 * math.cos(origin_lat_radians)
        return point["longitude"] * meters_per_degree_lng, point["latitude"] * meters_per_degree_lat

    @classmethod
    def _is_valid_polyline(cls, polyline: list[dict]) -> bool:
        return len(polyline) >= 2 and all(cls._coerce_valid_point(point) is not None for point in polyline)

    @staticmethod
    def _coerce_valid_point(point: Any) -> dict | None:
        try:
            latitude = float(point["latitude"])
            longitude = float(point["longitude"])
        except (KeyError, TypeError, ValueError):
            return None
        if not math.isfinite(latitude) or not math.isfinite(longitude):
            return None
        if latitude < -90 or latitude > 90 or longitude < -180 or longitude > 180:
            return None
        return {"latitude": latitude, "longitude": longitude}

    @staticmethod
    def _distance_meters(start: dict, end: dict) -> float:
        earth_radius_meters = 6_371_000
        lat1 = math.radians(start["latitude"])
        lat2 = math.radians(end["latitude"])
        d_lat = math.radians(end["latitude"] - start["latitude"])
        d_lng = math.radians(end["longitude"] - start["longitude"])
        a = (
            math.sin(d_lat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(d_lng / 2) ** 2
        )
        return earth_radius_meters * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    @staticmethod
    def _normalize_name(value: str) -> str:
        return value.strip().lower()
