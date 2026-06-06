from pydantic import BaseModel, ConfigDict


class AIProviderCreate(BaseModel):
    provider_name: str
    model_type: str
    endpoint: str | None = None
    api_key_masked: str | None = None
    extra_config_json: dict | None = None
    status: str = "inactive"


class AIProviderUpdate(BaseModel):
    provider_name: str | None = None
    model_type: str | None = None
    endpoint: str | None = None
    api_key_masked: str | None = None
    extra_config_json: dict | None = None
    status: str | None = None


class AdminUserCreate(BaseModel):
    username: str
    password: str
    role: str
    status: str = "active"


class AdminUserUpdate(BaseModel):
    role: str | None = None
    status: str | None = None
    password: str | None = None


class AdminUserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: str
    status: str
    last_login_at: str | None = None
