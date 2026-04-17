from pydantic import BaseModel


class DigitalHumanCreate(BaseModel):
    scenic_area_id: int | None = None
    name: str
    avatar_url: str | None = None
    voice_style: str | None = None
    welcome_text: str | None = None
    default_mode: str | None = None
    config_json: dict | None = None
    status: str = "active"


class DigitalHumanUpdate(BaseModel):
    scenic_area_id: int | None = None
    name: str | None = None
    avatar_url: str | None = None
    voice_style: str | None = None
    welcome_text: str | None = None
    default_mode: str | None = None
    config_json: dict | None = None
    status: str | None = None
