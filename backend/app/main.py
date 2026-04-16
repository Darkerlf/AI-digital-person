from fastapi import FastAPI

from app.api.routers.auth import router as auth_router
from app.api.routers.health import router as health_router
from app.api.routers.scenic_areas import router as scenic_areas_router
from app.api.routers.scenic_spots import router as scenic_spots_router
from app.core.config import settings

app = FastAPI(title=settings.app_name)
app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(scenic_areas_router, prefix=settings.api_prefix)
app.include_router(scenic_spots_router, prefix=settings.api_prefix)
