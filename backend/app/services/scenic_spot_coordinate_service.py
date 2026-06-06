import json
import math
from difflib import SequenceMatcher

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.scenic_spot import ScenicSpot
from app.schemas.scenic_spot import ScenicSpotCoordinateConfirm
from app.services.scenic_spot_service import ScenicSpotService
from app.services.tencent_map_client import TencentMapClient


DEFAULT_SCENIC_CENTER = {"latitude": 31.428076, "longitude": 120.098006}


class ScenicSpotCoordinateService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.spot_service = ScenicSpotService(db)

    def list_candidates(self, spot_id: int) -> dict:
        spot = self.spot_service.get(spot_id)
        return self._list_candidates_for_spot(spot, TencentMapClient())

    def list_batch_candidates(self, only_unverified: bool = True, limit: int = 50) -> dict:
        client = TencentMapClient()
        spots = self.spot_service.repo.list_all()
        if only_unverified:
            spots = [
                spot for spot in spots
                if spot.latitude is None or spot.longitude is None or not spot.coordinate_verified
            ]
        items = []
        for spot in spots[:limit]:
            item = self._list_candidates_for_spot(spot, client)
            item["spot_name"] = spot.name
            items.append(item)
        return {"items": items}

    def _list_candidates_for_spot(self, spot: ScenicSpot, client: TencentMapClient) -> dict:
        center = self._search_center(spot)
        search_keyword = self._search_keyword(spot)
        raw_places = client.search_places(
            keyword=search_keyword,
            latitude=center["latitude"],
            longitude=center["longitude"],
            radius=settings.tencent_map_search_radius_meters,
        )
        candidates = [
            self._candidate_from_place(place, spot, center)
            for place in raw_places
            if self._place_location(place) is not None
        ]
        candidates.sort(key=lambda item: item["confidence"], reverse=True)
        return {
            "spot_id": spot.id,
            "search_keyword": search_keyword,
            "center": center,
            "candidates": candidates,
        }

    def confirm_candidate(self, spot_id: int, payload: ScenicSpotCoordinateConfirm, current_user=None) -> dict:
        spot = self.spot_service.get(spot_id)
        if not (-90 <= payload.latitude <= 90 and -180 <= payload.longitude <= 180):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid coordinate")

        spot.latitude = payload.latitude
        spot.longitude = payload.longitude
        spot.coordinate_source = payload.coordinate_source
        spot.coordinate_confidence = payload.coordinate_confidence
        spot.coordinate_verified = True
        spot.tencent_poi_id = payload.tencent_poi_id
        spot.coordinate_address = payload.coordinate_address
        spot.coordinate_raw_json = (
            json.dumps(payload.coordinate_raw_json, ensure_ascii=False)
            if payload.coordinate_raw_json is not None
            else None
        )
        self.db.commit()
        self.db.refresh(spot)
        return self.spot_service._to_read_dict(spot)

    def _search_keyword(self, spot: ScenicSpot) -> str:
        area_name = spot.scenic_area.name if spot.scenic_area else ""
        return " ".join(part for part in [area_name, spot.name] if part).strip()

    def _search_center(self, spot: ScenicSpot) -> dict:
        if spot.latitude is not None and spot.longitude is not None:
            return {"latitude": spot.latitude, "longitude": spot.longitude}
        return DEFAULT_SCENIC_CENTER

    def _candidate_from_place(self, place: dict, spot: ScenicSpot, center: dict) -> dict:
        location = self._place_location(place)
        assert location is not None
        latitude = float(location["lat"])
        longitude = float(location["lng"])
        distance_meters = round(self._distance_meters(center["latitude"], center["longitude"], latitude, longitude))
        confidence = self._confidence(place, spot, distance_meters)
        return {
            "provider": "tencent_place",
            "title": str(place.get("title") or ""),
            "address": place.get("address"),
            "category": place.get("category"),
            "latitude": latitude,
            "longitude": longitude,
            "confidence": confidence,
            "distance_meters": distance_meters,
            "tencent_poi_id": place.get("id"),
            "raw": place,
        }

    @staticmethod
    def _place_location(place: dict) -> dict | None:
        location = place.get("location")
        if not isinstance(location, dict):
            return None
        if "lat" not in location or "lng" not in location:
            return None
        return location

    @staticmethod
    def _confidence(place: dict, spot: ScenicSpot, distance_meters: int) -> int:
        title = str(place.get("title") or "")
        address = str(place.get("address") or "")
        name_score = SequenceMatcher(None, spot.name.lower(), title.lower()).ratio()
        if spot.name in title or title in spot.name:
            name_score = max(name_score, 0.92)
        distance_score = max(0.0, 1.0 - min(distance_meters, settings.tencent_map_search_radius_meters) / settings.tencent_map_search_radius_meters)
        area_name = spot.scenic_area.name if spot.scenic_area else ""
        area_bonus = 0.08 if area_name and (area_name in address or area_name in title) else 0.0
        score = name_score * 0.72 + distance_score * 0.2 + area_bonus
        return max(0, min(100, round(score * 100)))

    @staticmethod
    def _distance_meters(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        earth_radius_meters = 6371000
        d_lat = math.radians(lat2 - lat1)
        d_lng = math.radians(lng2 - lng1)
        a = (
            math.sin(d_lat / 2) ** 2
            + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lng / 2) ** 2
        )
        return earth_radius_meters * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
