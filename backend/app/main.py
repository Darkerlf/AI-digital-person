from fastapi import FastAPI

from app.api.routers.auth import router as auth_router
from app.api.routers.health import router as health_router
from app.core.config import settings

app = FastAPI(title=settings.app_name)
app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(auth_router, prefix=settings.api_prefix)
