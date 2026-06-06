from pydantic import BaseModel


class ServicePOICreate(BaseModel):
    scenic_area_id: int | None = None
    name: str
    category: str
    area_text: str | None = None
    description: str | None = None
    open_hours: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    status: str = "active"


class ServicePOIUpdate(BaseModel):
    scenic_area_id: int | None = None
    name: str | None = None
    category: str | None = None
    area_text: str | None = None
    description: str | None = None
    open_hours: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    status: str | None = None


class ServicePOIRead(ServicePOICreate):
    id: int


class ServicePOIListResponse(BaseModel):
    items: list[ServicePOIRead]
