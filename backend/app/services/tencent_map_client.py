import httpx

from app.core.config import settings


class TencentMapClient:
    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key if api_key is not None else settings.tencent_map_key

    def search_places(self, *, keyword: str, latitude: float, longitude: float, radius: int) -> list[dict]:
        if not self.api_key:
            return []

        params = {
            "keyword": keyword,
            "boundary": f"nearby({latitude},{longitude},{radius})",
            "page_size": 10,
            "page_index": 1,
            "key": self.api_key,
        }
        with httpx.Client(timeout=5.0) as client:
            response = client.get(settings.tencent_map_place_search_url, params=params)
            response.raise_for_status()
        payload = response.json()
        if payload.get("status") != 0:
            return []
        return list(payload.get("data") or [])

    def direction_walking(self, *, from_point: dict, to_point: dict) -> dict | None:
        if not self.api_key:
            return None

        params = {
            "from": f"{from_point['latitude']},{from_point['longitude']}",
            "to": f"{to_point['latitude']},{to_point['longitude']}",
            "key": self.api_key,
        }
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(settings.tencent_map_direction_walking_url, params=params)
                response.raise_for_status()
        except httpx.HTTPError:
            return None

        payload = response.json()
        if payload.get("status") != 0:
            return None
        routes = (payload.get("result") or {}).get("routes") or []
        if not routes:
            return None
        route = routes[0]
        polyline = self._decode_polyline(route.get("polyline") or [])
        if not polyline:
            polyline = [from_point, to_point]
        return {
            "distance_meters": int(route.get("distance") or 0),
            "duration_minutes": int(route.get("duration") or 0),
            "polyline": polyline,
            "provider": "tencent_walking",
            "raw": route,
        }

    @staticmethod
    def _decode_polyline(values: list) -> list[dict]:
        if len(values) < 2:
            return []
        coordinates = [float(value) for value in values]
        for index in range(2, len(coordinates)):
            coordinates[index] = coordinates[index - 2] + coordinates[index] / 1_000_000
        return [
            {
                "latitude": round(coordinates[index], 6),
                "longitude": round(coordinates[index + 1], 6),
            }
            for index in range(0, len(coordinates) - 1, 2)
        ]
