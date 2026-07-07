from typing import Annotated, Literal

from pydantic import BaseModel, StringConstraints


RequiredText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
OptionalText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
ScenicAreaStatus = Literal["active", "inactive"]


class ScenicAreaCreate(BaseModel):
    code: RequiredText
    name: RequiredText
    description: str | None = None
    status: ScenicAreaStatus = "active"


class ScenicAreaUpdate(BaseModel):
    code: OptionalText | None = None
    name: OptionalText | None = None
    description: str | None = None
    status: ScenicAreaStatus | None = None


class ScenicAreaRead(ScenicAreaCreate):
    id: int

    model_config = {"from_attributes": True}
