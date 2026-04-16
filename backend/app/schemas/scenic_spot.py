from pydantic import BaseModel


class ScenicSpotCreate(BaseModel):
    scenic_area_id: int
    spot_code: str
    name: str
    alias: str | None = None
    location_text: str | None = None
    open_status: str = "open"
    tags: list[str] = []


class ScenicSpotUpdate(BaseModel):
    scenic_area_id: int | None = None
    spot_code: str | None = None
    name: str | None = None
    alias: str | None = None
    location_text: str | None = None
    open_status: str | None = None
    tags: list[str] | None = None


class ScenicSpotRead(ScenicSpotCreate):
    id: int
