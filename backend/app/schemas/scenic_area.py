from pydantic import BaseModel


class ScenicAreaCreate(BaseModel):
    code: str
    name: str
    description: str | None = None
    status: str = "active"


class ScenicAreaUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    description: str | None = None
    status: str | None = None


class ScenicAreaRead(ScenicAreaCreate):
    id: int

    model_config = {"from_attributes": True}
