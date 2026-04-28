from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers.auth import router as auth_router
from app.api.routers.dashboard import router as dashboard_router
from app.api.routers.digital_humans import router as digital_humans_router
from app.api.routers.faqs import router as faqs_router
from app.api.routers.health import router as health_router
from app.api.routers.imports import router as imports_router
from app.api.routers.knowledge_correction_tasks import router as knowledge_correction_tasks_router
from app.api.routers.knowledge_documents import router as knowledge_documents_router
from app.api.routers.operation_logs import router as operation_logs_router
from app.api.routers.route_recommendations import router as route_recommendations_router
from app.api.routers.route_templates import router as route_templates_router
from app.api.routers.scenic_areas import router as scenic_areas_router
from app.api.routers.scenic_spots import router as scenic_spots_router
from app.api.routers.sessions import router as sessions_router
from app.api.routers.settings import router as settings_router
from app.api.routers.tourist_chat import router as tourist_chat_router
from app.api.routers.tourist_voice import router as tourist_voice_router
from app.core.config import settings

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(scenic_areas_router, prefix=settings.api_prefix)
app.include_router(scenic_spots_router, prefix=settings.api_prefix)
app.include_router(knowledge_correction_tasks_router, prefix=settings.api_prefix)
app.include_router(knowledge_documents_router, prefix=settings.api_prefix)
app.include_router(faqs_router, prefix=settings.api_prefix)
app.include_router(imports_router, prefix=settings.api_prefix)
app.include_router(dashboard_router, prefix=settings.api_prefix)
app.include_router(digital_humans_router, prefix=settings.api_prefix)
app.include_router(settings_router, prefix=settings.api_prefix)
app.include_router(operation_logs_router, prefix=settings.api_prefix)
app.include_router(route_recommendations_router, prefix=settings.api_prefix)
app.include_router(route_templates_router, prefix=settings.api_prefix)
app.include_router(sessions_router, prefix=settings.api_prefix)
app.include_router(tourist_chat_router, prefix=settings.api_prefix)
app.include_router(tourist_voice_router, prefix=settings.api_prefix)
