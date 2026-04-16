# Admin Backend Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first usable admin backend for the scenic-guide AI digital human project, including real data import, knowledge management, dashboard statistics, and reserved AI configuration.

**Architecture:** Use a modular monolith with `FastAPI + SQLAlchemy + MySQL` for the backend and `Vue 3 + Element Plus + Vite` for the admin UI. Keep imports, statistics, and knowledge management in the same deployable service, but split code into bounded modules (`auth`, `scenic`, `knowledge`, `imports`, `dashboard`, `settings`, `digital_humans`) so later AI features can attach without rewrites.

**Tech Stack:** Python 3.13, FastAPI, SQLAlchemy 2, Pydantic 2, PyMySQL, pytest, python-docx, openpyxl, Vue 3, TypeScript, Vite, Element Plus, Pinia, Vue Router, Axios, ECharts, Vitest.

---

## File Structure

### Root

- Create: `.gitignore`
- Create: `.env.example`
- Create: `README.md`
- Create: `uploads/.gitkeep`

### Backend

- Create: `backend/requirements.txt`
- Create: `backend/app/main.py`
- Create: `backend/app/core/config.py`
- Create: `backend/app/core/database.py`
- Create: `backend/app/core/security.py`
- Create: `backend/app/core/logging.py`
- Create: `backend/app/core/exceptions.py`
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/base.py`
- Create: `backend/app/models/admin_user.py`
- Create: `backend/app/models/operation_log.py`
- Create: `backend/app/models/scenic_area.py`
- Create: `backend/app/models/scenic_spot.py`
- Create: `backend/app/models/scenic_spot_tag.py`
- Create: `backend/app/models/knowledge_document.py`
- Create: `backend/app/models/knowledge_chunk.py`
- Create: `backend/app/models/faq_item.py`
- Create: `backend/app/models/import_job.py`
- Create: `backend/app/models/import_job_item.py`
- Create: `backend/app/models/visitor_behavior_event.py`
- Create: `backend/app/models/dashboard_stat_daily.py`
- Create: `backend/app/models/feedback_record.py`
- Create: `backend/app/models/digital_human_config.py`
- Create: `backend/app/models/ai_provider_config.py`
- Create: `backend/app/schemas/auth.py`
- Create: `backend/app/schemas/common.py`
- Create: `backend/app/schemas/scenic_area.py`
- Create: `backend/app/schemas/scenic_spot.py`
- Create: `backend/app/schemas/knowledge.py`
- Create: `backend/app/schemas/imports.py`
- Create: `backend/app/schemas/dashboard.py`
- Create: `backend/app/schemas/settings.py`
- Create: `backend/app/schemas/digital_human.py`
- Create: `backend/app/api/deps.py`
- Create: `backend/app/api/routers/health.py`
- Create: `backend/app/api/routers/auth.py`
- Create: `backend/app/api/routers/scenic_areas.py`
- Create: `backend/app/api/routers/scenic_spots.py`
- Create: `backend/app/api/routers/knowledge_documents.py`
- Create: `backend/app/api/routers/faqs.py`
- Create: `backend/app/api/routers/imports.py`
- Create: `backend/app/api/routers/dashboard.py`
- Create: `backend/app/api/routers/digital_humans.py`
- Create: `backend/app/api/routers/settings.py`
- Create: `backend/app/api/routers/operation_logs.py`
- Create: `backend/app/repositories/*.py`
- Create: `backend/app/services/*.py`
- Create: `backend/app/importers/parsers/docx_parser.py`
- Create: `backend/app/importers/parsers/text_parser.py`
- Create: `backend/app/importers/parsers/excel_parser.py`
- Create: `backend/app/importers/scenic_docx_importer.py`
- Create: `backend/app/importers/knowledge_doc_importer.py`
- Create: `backend/app/importers/behavior_excel_importer.py`
- Create: `backend/app/tasks/knowledge_chunker.py`
- Create: `backend/app/tasks/dashboard_aggregator.py`
- Create: `backend/app/utils/file_storage.py`
- Create: `backend/app/utils/text_cleaner.py`
- Create: `backend/scripts/init_db.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_health.py`
- Create: `backend/tests/test_auth.py`
- Create: `backend/tests/test_scenic_spots.py`
- Create: `backend/tests/test_knowledge.py`
- Create: `backend/tests/test_imports.py`
- Create: `backend/tests/test_dashboard.py`
- Create: `backend/tests/test_settings.py`

### Frontend

- Create: `admin-web/package.json`
- Create: `admin-web/tsconfig.json`
- Create: `admin-web/vite.config.ts`
- Create: `admin-web/index.html`
- Create: `admin-web/src/main.ts`
- Create: `admin-web/src/App.vue`
- Create: `admin-web/src/router/index.ts`
- Create: `admin-web/src/stores/auth.ts`
- Create: `admin-web/src/api/client.ts`
- Create: `admin-web/src/layouts/AdminLayout.vue`
- Create: `admin-web/src/views/LoginView.vue`
- Create: `admin-web/src/views/DashboardView.vue`
- Create: `admin-web/src/views/ScenicAreaView.vue`
- Create: `admin-web/src/views/ScenicSpotListView.vue`
- Create: `admin-web/src/views/ScenicSpotDetailView.vue`
- Create: `admin-web/src/views/KnowledgeDocumentView.vue`
- Create: `admin-web/src/views/KnowledgeDocumentDetailView.vue`
- Create: `admin-web/src/views/FaqView.vue`
- Create: `admin-web/src/views/ImportJobView.vue`
- Create: `admin-web/src/views/ImportJobDetailView.vue`
- Create: `admin-web/src/views/DigitalHumanView.vue`
- Create: `admin-web/src/views/SettingsAiProviderView.vue`
- Create: `admin-web/src/views/OperationLogView.vue`
- Create: `admin-web/src/components/AppSidebar.vue`
- Create: `admin-web/src/components/AppHeader.vue`
- Create: `admin-web/src/components/StatCard.vue`
- Create: `admin-web/src/components/ImportUploadCard.vue`
- Create: `admin-web/src/components/SpotFormDrawer.vue`
- Create: `admin-web/src/components/KnowledgeChunkPreview.vue`
- Create: `admin-web/src/components/DashboardCharts.vue`
- Create: `admin-web/src/styles.css`
- Create: `admin-web/src/types/*.ts`
- Create: `admin-web/src/tests/LoginView.test.ts`
- Create: `admin-web/src/tests/DashboardView.test.ts`

## Task 1: Initialize Repository and Backend Skeleton

**Files:**
- Create: `.gitignore`
- Create: `.env.example`
- Create: `README.md`
- Create: `uploads/.gitkeep`
- Create: `backend/requirements.txt`
- Create: `backend/app/main.py`
- Create: `backend/app/core/config.py`
- Create: `backend/app/core/database.py`
- Create: `backend/app/api/routers/health.py`
- Create: `backend/tests/test_health.py`

- [ ] **Step 1: Initialize git and create the base directories**

Run:

```powershell
git init
New-Item -ItemType Directory -Force docs, uploads, backend, backend\app, backend\app\core, backend\app\api, backend\app\api\routers, backend\tests
New-Item -ItemType File -Force uploads\.gitkeep
```

Expected: a new `.git` directory exists and the listed folders are present.

- [ ] **Step 2: Write the failing backend health test**

```python
from fastapi.testclient import TestClient

from app.main import app


def test_health_returns_ok() -> None:
    client = TestClient(app)

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

- [ ] **Step 3: Run the test to verify it fails**

Run:

```powershell
cd backend
python -m pytest tests/test_health.py -q
```

Expected: FAIL with `ModuleNotFoundError` or import failure because `app.main` does not exist yet.

- [ ] **Step 4: Write the minimal backend bootstrap**

`backend/requirements.txt`

```text
fastapi==0.115.12
uvicorn==0.34.0
sqlalchemy==2.0.40
pymysql==1.1.1
pydantic-settings==2.8.1
python-multipart==0.0.20
passlib[bcrypt]==1.7.4
python-jose==3.4.0
python-docx==1.1.2
openpyxl==3.1.5
pytest==8.3.5
httpx==0.28.1
```

`backend/app/core/config.py`

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Scenic Admin API"
    api_prefix: str = "/api"
    database_url: str = "mysql+pymysql://root:password@127.0.0.1:3306/scenic_admin"
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 120

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
```

`backend/app/core/database.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(settings.database_url, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
```

`backend/app/api/routers/health.py`

```python
from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
```

`backend/app/main.py`

```python
from fastapi import FastAPI

from app.api.routers.health import router as health_router
from app.core.config import settings

app = FastAPI(title=settings.app_name)
app.include_router(health_router, prefix=settings.api_prefix)
```

`.gitignore`

```gitignore
.venv/
__pycache__/
.pytest_cache/
*.pyc
.env
uploads/*
!uploads/.gitkeep
node_modules/
dist/
coverage/
```

`.env.example`

```env
DATABASE_URL=mysql+pymysql://root:password@127.0.0.1:3306/scenic_admin
JWT_SECRET_KEY=change-me
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120
```

- [ ] **Step 5: Install dependencies and run the health test**

Run:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m pytest tests/test_health.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```powershell
git add .gitignore .env.example README.md uploads/.gitkeep backend
git commit -m "chore: bootstrap backend skeleton"
```

## Task 2: Create the Shared Data Layer and Core Models

**Files:**
- Create: `backend/app/models/base.py`
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/admin_user.py`
- Create: `backend/app/models/operation_log.py`
- Create: `backend/app/models/scenic_area.py`
- Create: `backend/app/models/scenic_spot.py`
- Create: `backend/app/models/scenic_spot_tag.py`
- Create: `backend/app/models/knowledge_document.py`
- Create: `backend/app/models/knowledge_chunk.py`
- Create: `backend/app/models/faq_item.py`
- Create: `backend/app/models/import_job.py`
- Create: `backend/app/models/import_job_item.py`
- Create: `backend/app/models/visitor_behavior_event.py`
- Create: `backend/app/models/dashboard_stat_daily.py`
- Create: `backend/app/models/feedback_record.py`
- Create: `backend/app/models/digital_human_config.py`
- Create: `backend/app/models/ai_provider_config.py`
- Create: `backend/scripts/init_db.py`
- Create: `backend/tests/test_models.py`
- Modify: `backend/app/core/database.py`

- [ ] **Step 1: Write the failing metadata test**

```python
from app.core.database import Base
from app.models import load_all_models


def test_metadata_contains_phase1_tables() -> None:
    load_all_models()

    expected_tables = {
        "admin_user",
        "operation_log",
        "scenic_area",
        "scenic_spot",
        "scenic_spot_tag",
        "knowledge_document",
        "knowledge_chunk",
        "faq_item",
        "import_job",
        "import_job_item",
        "visitor_behavior_event",
        "dashboard_stat_daily",
        "feedback_record",
        "digital_human_config",
        "ai_provider_config",
    }

    assert expected_tables.issubset(set(Base.metadata.tables))
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```powershell
cd backend
.\.venv\Scripts\python -m pytest tests/test_models.py -q
```

Expected: FAIL because `app.models` and the model registry do not exist.

- [ ] **Step 3: Implement the base mixins and model registry**

`backend/app/models/base.py`

```python
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


__all__ = ["Base", "TimestampMixin"]
```

`backend/app/models/__init__.py`

```python
from app.models.admin_user import AdminUser
from app.models.ai_provider_config import AIProviderConfig
from app.models.dashboard_stat_daily import DashboardStatDaily
from app.models.digital_human_config import DigitalHumanConfig
from app.models.faq_item import FAQItem
from app.models.feedback_record import FeedbackRecord
from app.models.import_job import ImportJob
from app.models.import_job_item import ImportJobItem
from app.models.knowledge_chunk import KnowledgeChunk
from app.models.knowledge_document import KnowledgeDocument
from app.models.operation_log import OperationLog
from app.models.scenic_area import ScenicArea
from app.models.scenic_spot import ScenicSpot
from app.models.scenic_spot_tag import ScenicSpotTag
from app.models.visitor_behavior_event import VisitorBehaviorEvent


def load_all_models() -> None:
    _ = (
        AdminUser,
        AIProviderConfig,
        DashboardStatDaily,
        DigitalHumanConfig,
        FAQItem,
        FeedbackRecord,
        ImportJob,
        ImportJobItem,
        KnowledgeChunk,
        KnowledgeDocument,
        OperationLog,
        ScenicArea,
        ScenicSpot,
        ScenicSpotTag,
        VisitorBehaviorEvent,
    )
```

`backend/app/models/scenic_area.py`

```python
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class ScenicArea(TimestampMixin, Base):
    __tablename__ = "scenic_area"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="active")

    spots = relationship("ScenicSpot", back_populates="scenic_area")
```

`backend/app/models/scenic_spot.py`

```python
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class ScenicSpot(TimestampMixin, Base):
    __tablename__ = "scenic_spot"

    id: Mapped[int] = mapped_column(primary_key=True)
    scenic_area_id: Mapped[int] = mapped_column(ForeignKey("scenic_area.id"), index=True)
    spot_code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    alias: Mapped[str | None] = mapped_column(String(255))
    location_text: Mapped[str | None] = mapped_column(Text)
    latitude: Mapped[float | None]
    longitude: Mapped[float | None]
    parameters_text: Mapped[str | None] = mapped_column(Text)
    core_function: Mapped[str | None] = mapped_column(Text)
    cultural_value: Mapped[str | None] = mapped_column(Text)
    detail_intro: Mapped[str | None] = mapped_column(Text)
    highlights: Mapped[str | None] = mapped_column(Text)
    performance_info: Mapped[str | None] = mapped_column(Text)
    remarks: Mapped[str | None] = mapped_column(Text)
    suggested_duration_minutes: Mapped[int | None] = mapped_column(Integer)
    open_status: Mapped[str] = mapped_column(String(20), default="open")

    scenic_area = relationship("ScenicArea", back_populates="spots")
    tags = relationship("ScenicSpotTag", back_populates="scenic_spot", cascade="all, delete-orphan")
```

`backend/scripts/init_db.py`

```python
from app.core.database import Base, engine
from app.models import load_all_models


def main() -> None:
    load_all_models()
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    main()
```

Also create these model files with the approved spec fields, `id` primary keys, `created_at` / `updated_at` where applicable, and foreign keys that match the table names exactly:

- `admin_user.py`
- `operation_log.py`
- `scenic_spot_tag.py`
- `knowledge_document.py`
- `knowledge_chunk.py`
- `faq_item.py`
- `import_job.py`
- `import_job_item.py`
- `visitor_behavior_event.py`
- `dashboard_stat_daily.py`
- `feedback_record.py`
- `digital_human_config.py`
- `ai_provider_config.py`

- [ ] **Step 4: Update the database module to load models cleanly**

`backend/app/core/database.py`

```python
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(settings.database_url, future=True, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
```

- [ ] **Step 5: Run the model test**

Run:

```powershell
cd backend
.\.venv\Scripts\python -m pytest tests/test_models.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```powershell
git add backend/app/models backend/app/core/database.py backend/scripts/init_db.py backend/tests/test_models.py
git commit -m "feat: add core data models"
```

## Task 3: Add Authentication, Dependencies, and Audit Logging

**Files:**
- Create: `backend/app/core/security.py`
- Create: `backend/app/schemas/auth.py`
- Create: `backend/app/api/deps.py`
- Create: `backend/app/api/routers/auth.py`
- Create: `backend/app/repositories/admin_user_repo.py`
- Create: `backend/app/repositories/operation_log_repo.py`
- Create: `backend/app/services/auth_service.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_auth.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: Write the failing auth test**

```python
from fastapi.testclient import TestClient

from app.main import app


def test_login_returns_access_token(test_db_session) -> None:
    client = TestClient(app)

    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "admin123"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "access_token" in payload
    assert payload["token_type"] == "bearer"
```

- [ ] **Step 2: Run the auth test to verify it fails**

Run:

```powershell
cd backend
.\.venv\Scripts\python -m pytest tests/test_auth.py -q
```

Expected: FAIL with `404` or fixture errors because the auth router and test session are missing.

- [ ] **Step 3: Add security primitives and test fixtures**

`backend/app/core/security.py`

```python
from datetime import UTC, datetime, timedelta

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(subject: str) -> str:
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "exp": expires_at}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
```

`backend/app/schemas/auth.py`

```python
from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

`backend/tests/conftest.py`

```python
import os

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.core.security import hash_password
from app.main import app
from app.models import load_all_models
from app.models.admin_user import AdminUser


@pytest.fixture()
def test_db_session():
    load_all_models()
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    session.add(AdminUser(username="admin", password_hash=hash_password("admin123"), role="super_admin", status="active"))
    session.commit()

    def override_get_db():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield session
    finally:
        session.close()
        app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers(test_db_session) -> dict[str, str]:
    client = TestClient(app)
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

- [ ] **Step 4: Implement login and `/me`**

`backend/app/api/routers/auth.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    service = AuthService(db)
    token = service.login(payload.username, payload.password)
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return TokenResponse(access_token=token)


@router.get("/me")
def me(current_user=Depends(get_current_user)) -> dict[str, str]:
    return {"username": current_user.username, "role": current_user.role}
```

`backend/app/services/auth_service.py`

```python
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.repositories.admin_user_repo import AdminUserRepository


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.admin_users = AdminUserRepository(db)

    def login(self, username: str, password: str) -> str | None:
        user = self.admin_users.get_by_username(username)
        if user is None or not verify_password(password, user.password_hash):
            return None
        return create_access_token(user.username)
```

Seed the first `admin` account in `test_db_session` with `admin123` hashed through `hash_password()`, and register the auth router in `app.main`.

- [ ] **Step 5: Run auth tests**

Run:

```powershell
cd backend
.\.venv\Scripts\python -m pytest tests/test_auth.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```powershell
git add backend/app/core/security.py backend/app/schemas/auth.py backend/app/api backend/app/repositories backend/app/services backend/tests
git commit -m "feat: add authentication and audit primitives"
```

## Task 4: Implement Scenic Area and Scenic Spot CRUD

**Files:**
- Create: `backend/app/schemas/scenic_area.py`
- Create: `backend/app/schemas/scenic_spot.py`
- Create: `backend/app/repositories/scenic_area_repo.py`
- Create: `backend/app/repositories/scenic_spot_repo.py`
- Create: `backend/app/services/scenic_area_service.py`
- Create: `backend/app/services/scenic_spot_service.py`
- Create: `backend/app/api/routers/scenic_areas.py`
- Create: `backend/app/api/routers/scenic_spots.py`
- Create: `backend/tests/test_scenic_spots.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: Write the failing scenic spot CRUD test**

```python
from fastapi.testclient import TestClient

from app.main import app


def test_create_and_list_scenic_spots(test_db_session, auth_headers) -> None:
    client = TestClient(app)

    area_response = client.post(
        "/api/scenic-areas",
        headers=auth_headers,
        json={"code": "LS", "name": "灵山胜境", "description": "示范景区", "status": "active"},
    )
    assert area_response.status_code == 201

    spot_response = client.post(
        "/api/scenic-spots",
        headers=auth_headers,
        json={
            "scenic_area_id": area_response.json()["id"],
            "spot_code": "LS-001",
            "name": "灵山大照壁",
            "alias": "华夏第一壁",
            "location_text": "景区入口处",
            "open_status": "open",
            "tags": ["历史", "拍照"],
        },
    )
    assert spot_response.status_code == 201

    list_response = client.get("/api/scenic-spots", headers=auth_headers)
    assert list_response.status_code == 200
    assert list_response.json()["items"][0]["spot_code"] == "LS-001"
```

- [ ] **Step 2: Run the scenic spot test to verify it fails**

Run:

```powershell
cd backend
.\.venv\Scripts\python -m pytest tests/test_scenic_spots.py -q
```

Expected: FAIL because the scenic routers and schemas do not exist.

- [ ] **Step 3: Implement scenic area and spot schemas**

`backend/app/schemas/scenic_area.py`

```python
from pydantic import BaseModel


class ScenicAreaCreate(BaseModel):
    code: str
    name: str
    description: str | None = None
    status: str = "active"


class ScenicAreaRead(ScenicAreaCreate):
    id: int

    model_config = {"from_attributes": True}
```

`backend/app/schemas/scenic_spot.py`

```python
from pydantic import BaseModel


class ScenicSpotCreate(BaseModel):
    scenic_area_id: int
    spot_code: str
    name: str
    alias: str | None = None
    location_text: str | None = None
    open_status: str = "open"
    tags: list[str] = []


class ScenicSpotRead(ScenicSpotCreate):
    id: int

    model_config = {"from_attributes": True}
```

- [ ] **Step 4: Implement the CRUD services and routers**

`backend/app/api/routers/scenic_areas.py`

```python
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import require_authenticated_user
from app.core.database import get_db
from app.schemas.scenic_area import ScenicAreaCreate, ScenicAreaRead
from app.services.scenic_area_service import ScenicAreaService

router = APIRouter(prefix="/scenic-areas", tags=["scenic-areas"])


@router.post("", response_model=ScenicAreaRead, status_code=status.HTTP_201_CREATED)
def create_area(
    payload: ScenicAreaCreate,
    _: object = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
) -> ScenicAreaRead:
    return ScenicAreaService(db).create(payload)


@router.get("", response_model=list[ScenicAreaRead])
def list_areas(_: object = Depends(require_authenticated_user), db: Session = Depends(get_db)) -> list[ScenicAreaRead]:
    return ScenicAreaService(db).list_all()
```

`backend/app/api/routers/scenic_spots.py`

```python
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import require_authenticated_user
from app.core.database import get_db
from app.schemas.scenic_spot import ScenicSpotCreate, ScenicSpotRead
from app.services.scenic_spot_service import ScenicSpotService

router = APIRouter(prefix="/scenic-spots", tags=["scenic-spots"])


@router.post("", response_model=ScenicSpotRead, status_code=status.HTTP_201_CREATED)
def create_spot(
    payload: ScenicSpotCreate,
    _: object = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
) -> ScenicSpotRead:
    return ScenicSpotService(db).create(payload)


@router.get("")
def list_spots(_: object = Depends(require_authenticated_user), db: Session = Depends(get_db)) -> dict[str, list[ScenicSpotRead]]:
    items = ScenicSpotService(db).list_all()
    return {"items": items}
```

Implement repositories and services so tags are replaced atomically on create/update.

- [ ] **Step 5: Run the CRUD test**

Run:

```powershell
cd backend
.\.venv\Scripts\python -m pytest tests/test_scenic_spots.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```powershell
git add backend/app/schemas backend/app/repositories backend/app/services backend/app/api/routers backend/tests/test_scenic_spots.py
git commit -m "feat: add scenic area and spot management"
```

## Task 5: Implement Knowledge Documents, Chunks, and FAQ Management

**Files:**
- Create: `backend/app/schemas/knowledge.py`
- Create: `backend/app/repositories/knowledge_repo.py`
- Create: `backend/app/services/knowledge_service.py`
- Create: `backend/app/tasks/knowledge_chunker.py`
- Create: `backend/app/api/routers/knowledge_documents.py`
- Create: `backend/app/api/routers/faqs.py`
- Create: `backend/app/utils/text_cleaner.py`
- Create: `backend/tests/test_knowledge.py`

- [ ] **Step 1: Write the failing knowledge test**

```python
from fastapi.testclient import TestClient

from app.main import app


def test_create_document_and_generate_chunks(test_db_session, auth_headers) -> None:
    client = TestClient(app)

    area_response = client.post(
        "/api/scenic-areas",
        headers=auth_headers,
        json={"code": "NH", "name": "拈花湾", "description": "小镇", "status": "active"},
    )

    response = client.post(
        "/api/knowledge/documents/upload",
        headers=auth_headers,
        json={
            "scenic_area_id": area_response.json()["id"],
            "title": "灵山导览词",
            "doc_type": "txt",
            "source_name": "guide.txt",
            "content_text": "第一段内容。" * 80,
        },
    )

    assert response.status_code == 201

    chunks = client.get(f"/api/knowledge/documents/{response.json()['id']}/chunks", headers=auth_headers)
    assert chunks.status_code == 200
    assert len(chunks.json()["items"]) >= 1
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```powershell
cd backend
.\.venv\Scripts\python -m pytest tests/test_knowledge.py -q
```

Expected: FAIL because the knowledge endpoints do not exist.

- [ ] **Step 3: Implement chunking and schemas**

`backend/app/tasks/knowledge_chunker.py`

```python
def chunk_text(content_text: str, target_size: int = 600) -> list[dict[str, str | int]]:
    paragraphs = [paragraph.strip() for paragraph in content_text.splitlines() if paragraph.strip()]
    chunks: list[dict[str, str | int]] = []
    current = ""
    chunk_index = 0

    for paragraph in paragraphs:
        if len(current) + len(paragraph) > target_size and current:
            chunks.append(
                {
                    "chunk_index": chunk_index,
                    "chunk_text": current,
                    "token_count": len(current),
                    "source_section": f"chunk-{chunk_index}",
                }
            )
            chunk_index += 1
            current = paragraph
        else:
            current = f"{current}\n{paragraph}".strip()

    if current:
        chunks.append(
            {
                "chunk_index": chunk_index,
                "chunk_text": current,
                "token_count": len(current),
                "source_section": f"chunk-{chunk_index}",
            }
        )

    return chunks
```

`backend/app/schemas/knowledge.py`

```python
from pydantic import BaseModel


class KnowledgeDocumentCreate(BaseModel):
    scenic_area_id: int
    title: str
    doc_type: str
    source_name: str
    content_text: str


class KnowledgeChunkRead(BaseModel):
    id: int
    chunk_index: int
    chunk_text: str
    token_count: int
    source_section: str

    model_config = {"from_attributes": True}
```

- [ ] **Step 4: Implement knowledge document, chunks, and FAQ routes**

`backend/app/api/routers/knowledge_documents.py`

```python
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import require_authenticated_user
from app.core.database import get_db
from app.schemas.knowledge import KnowledgeDocumentCreate
from app.services.knowledge_service import KnowledgeService

router = APIRouter(prefix="/knowledge/documents", tags=["knowledge-documents"])


@router.post("/upload", status_code=status.HTTP_201_CREATED)
def create_document(
    payload: KnowledgeDocumentCreate,
    _: object = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
) -> dict:
    document = KnowledgeService(db).create_document(payload)
    return {"id": document.id, "title": document.title}


@router.get("/{document_id}/chunks")
def list_chunks(
    document_id: int,
    _: object = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
) -> dict[str, list[dict]]:
    items = KnowledgeService(db).list_chunks(document_id)
    return {"items": items}
```

Also add these FAQ endpoints with `question`, `answer`, `category`, `priority`, and `status` fields:

- `GET /api/knowledge/faqs`
- `POST /api/knowledge/faqs`
- `PUT /api/knowledge/faqs/{faq_id}`
- `DELETE /api/knowledge/faqs/{faq_id}`

Keep document updates responsible for deleting old chunks and recreating the new chunk set in the same transaction.

- [ ] **Step 5: Run the knowledge test**

Run:

```powershell
cd backend
.\.venv\Scripts\python -m pytest tests/test_knowledge.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```powershell
git add backend/app/schemas/knowledge.py backend/app/services/knowledge_service.py backend/app/repositories/knowledge_repo.py backend/app/tasks/knowledge_chunker.py backend/app/api/routers/knowledge_documents.py backend/app/api/routers/faqs.py backend/tests/test_knowledge.py
git commit -m "feat: add knowledge document and faq management"
```

## Task 6: Build the Import Job Framework and Scenic/Knowledge Importers

**Files:**
- Create: `backend/app/schemas/imports.py`
- Create: `backend/app/utils/file_storage.py`
- Create: `backend/app/importers/parsers/docx_parser.py`
- Create: `backend/app/importers/parsers/text_parser.py`
- Create: `backend/app/importers/scenic_docx_importer.py`
- Create: `backend/app/importers/knowledge_doc_importer.py`
- Create: `backend/app/repositories/import_repo.py`
- Create: `backend/app/services/import_service.py`
- Create: `backend/app/api/routers/imports.py`
- Create: `backend/tests/test_imports.py`

- [ ] **Step 1: Write the failing scenic import test**

```python
from pathlib import Path

from app.importers.scenic_docx_importer import ScenicDocxImporter


def test_scenic_docx_importer_extracts_table_rows() -> None:
    importer = ScenicDocxImporter()
    rows = importer.parse(Path("tests/fixtures/scenic_spots.docx"))

    assert rows[0]["spot_code"] == "LS-001"
    assert rows[0]["name"] == "灵山大照壁"
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```powershell
cd backend
.\.venv\Scripts\python -m pytest tests/test_imports.py -q
```

Expected: FAIL because the importer class and fixture file are missing.

- [ ] **Step 3: Add the test fixture and parser code**

Create a small fixture document under `backend/tests/fixtures/scenic_spots.docx` with one table row containing:

```text
景区名称 | 景点ID | 景点名称 | 具体位置 | 建筑/景观参数 | 核心功能 | 文化内涵 | 详细介绍 | 游玩亮点 | 演艺/开放信息 | 备注
灵山胜境 | LS-001 | 灵山大照壁 | 景区入口处 | 长39.8m | 门户景观 | 佛教文化 | 入口大照壁介绍 | 打卡合影 | 全天开放 | 首处打卡点
```

`backend/app/importers/parsers/docx_parser.py`

```python
from pathlib import Path

from docx import Document


def read_docx_tables(path: Path) -> list[list[str]]:
    document = Document(str(path))
    rows: list[list[str]] = []
    for table in document.tables:
        for row in table.rows:
            rows.append([cell.text.strip() for cell in row.cells])
    return rows
```

`backend/app/importers/scenic_docx_importer.py`

```python
from pathlib import Path

from app.importers.parsers.docx_parser import read_docx_tables


class ScenicDocxImporter:
    def parse(self, path: Path) -> list[dict[str, str]]:
        rows = read_docx_tables(path)
        header = rows[0]
        result: list[dict[str, str]] = []
        for row in rows[1:]:
            record = dict(zip(header, row, strict=False))
            result.append(
                {
                    "scenic_area_name": record["景区名称"],
                    "spot_code": record["景点ID"],
                    "name": record["景点名称"],
                    "location_text": record["具体位置"],
                    "parameters_text": record["建筑/景观参数"],
                    "core_function": record["核心功能"],
                    "cultural_value": record["文化内涵"],
                    "detail_intro": record["详细介绍"],
                    "highlights": record["游玩亮点"],
                    "performance_info": record["演艺/开放信息"],
                    "remarks": record["备注"],
                }
            )
        return result
```

- [ ] **Step 4: Implement import jobs and HTTP endpoints**

Implement:

- `ImportService.create_job()`
- `ImportService.run_scenic_import()`
- `ImportService.run_knowledge_import()`
- `POST /api/imports/scenic-spots`
- `POST /api/imports/knowledge-docs`
- `GET /api/imports/jobs`
- `GET /api/imports/jobs/{id}`
- `GET /api/imports/jobs/{id}/items`

Use the following status values only:

```python
PENDING = "pending"
PROCESSING = "processing"
SUCCESS = "success"
PARTIAL_SUCCESS = "partial_success"
FAILED = "failed"
```

`backend/app/utils/file_storage.py`

```python
from pathlib import Path
import shutil
from uuid import uuid4


UPLOAD_DIR = Path("..").resolve() / "uploads"


def save_upload(source_path: Path) -> Path:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    target_path = UPLOAD_DIR / f"{uuid4()}-{source_path.name}"
    shutil.copy2(source_path, target_path)
    return target_path
```

- [ ] **Step 5: Run the import tests**

Run:

```powershell
cd backend
.\.venv\Scripts\python -m pytest tests/test_imports.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```powershell
git add backend/app/schemas/imports.py backend/app/importers backend/app/repositories/import_repo.py backend/app/services/import_service.py backend/app/api/routers/imports.py backend/app/utils/file_storage.py backend/tests/test_imports.py backend/tests/fixtures
git commit -m "feat: add import job framework and doc importers"
```

## Task 7: Add Behavior Excel Import and Dashboard Aggregation

**Files:**
- Create: `backend/app/importers/parsers/excel_parser.py`
- Create: `backend/app/importers/behavior_excel_importer.py`
- Create: `backend/app/tasks/dashboard_aggregator.py`
- Create: `backend/app/repositories/dashboard_repo.py`
- Create: `backend/app/services/dashboard_service.py`
- Create: `backend/app/schemas/dashboard.py`
- Create: `backend/app/api/routers/dashboard.py`
- Create: `backend/tests/test_dashboard.py`

- [ ] **Step 1: Write the failing dashboard aggregation test**

```python
from datetime import datetime

from app.tasks.dashboard_aggregator import aggregate_daily_stats


def test_aggregate_daily_stats_counts_events_and_hot_spots(test_db_session) -> None:
    result = aggregate_daily_stats(test_db_session, datetime(2026, 4, 7).date())

    assert "total_events" in result
    assert "hot_spot_top" in result
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```powershell
cd backend
.\.venv\Scripts\python -m pytest tests/test_dashboard.py -q
```

Expected: FAIL because the dashboard aggregator does not exist.

- [ ] **Step 3: Implement Excel parsing and aggregation**

`backend/app/importers/parsers/excel_parser.py`

```python
from pathlib import Path

from openpyxl import load_workbook


def read_excel_rows(path: Path) -> list[dict[str, object]]:
    workbook = load_workbook(path)
    sheet = workbook.active
    rows = list(sheet.iter_rows(values_only=True))
    header = [str(item).strip() for item in rows[0]]
    return [dict(zip(header, row, strict=False)) for row in rows[1:]]
```

`backend/app/tasks/dashboard_aggregator.py`

```python
from collections import Counter
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.visitor_behavior_event import VisitorBehaviorEvent


def aggregate_daily_stats(db: Session, stat_date: date) -> dict[str, object]:
    rows = db.execute(
        select(VisitorBehaviorEvent)
        .where(func.date(VisitorBehaviorEvent.event_time) == stat_date)
    ).scalars().all()

    hot_spots = Counter(row.spot_name for row in rows if row.spot_name)
    return {
        "total_events": len(rows),
        "hot_spot_top": hot_spots.most_common(5),
    }
```

- [ ] **Step 4: Expose dashboard endpoints**

Implement:

- `GET /api/dashboard/overview`
- `GET /api/dashboard/hot-spots`
- `GET /api/dashboard/behavior-trends`
- `POST /api/imports/behavior-events`

Response shape for overview:

```python
{
    "total_events": 0,
    "total_spots": 0,
    "total_documents": 0,
    "recent_import_jobs": [],
}
```

Ensure the behavior import service recomputes `dashboard_stat_daily` for all dates touched by the imported workbook.

- [ ] **Step 5: Run dashboard tests**

Run:

```powershell
cd backend
.\.venv\Scripts\python -m pytest tests/test_dashboard.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```powershell
git add backend/app/importers/parsers/excel_parser.py backend/app/importers/behavior_excel_importer.py backend/app/tasks/dashboard_aggregator.py backend/app/repositories/dashboard_repo.py backend/app/services/dashboard_service.py backend/app/schemas/dashboard.py backend/app/api/routers/dashboard.py backend/tests/test_dashboard.py
git commit -m "feat: add behavior import and dashboard aggregation"
```

## Task 8: Add Digital Human, AI Provider, and Operation Log APIs

**Files:**
- Create: `backend/app/schemas/settings.py`
- Create: `backend/app/schemas/digital_human.py`
- Create: `backend/app/repositories/settings_repo.py`
- Create: `backend/app/services/digital_human_service.py`
- Create: `backend/app/services/ai_adapter_service.py`
- Create: `backend/app/api/routers/digital_humans.py`
- Create: `backend/app/api/routers/settings.py`
- Create: `backend/app/api/routers/operation_logs.py`
- Create: `backend/tests/test_settings.py`

- [ ] **Step 1: Write the failing AI provider test**

```python
from fastapi.testclient import TestClient

from app.main import app


def test_create_ai_provider_config(test_db_session, auth_headers) -> None:
    client = TestClient(app)

    response = client.post(
        "/api/settings/ai-providers",
        headers=auth_headers,
        json={
            "provider_name": "qwen",
            "model_type": "chat",
            "endpoint": "https://example.com",
            "api_key_masked": "****abcd",
            "status": "active",
        },
    )

    assert response.status_code == 201
    assert response.json()["provider_name"] == "qwen"
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```powershell
cd backend
.\.venv\Scripts\python -m pytest tests/test_settings.py -q
```

Expected: FAIL because the settings router does not exist.

- [ ] **Step 3: Implement the settings and digital human APIs**

`backend/app/services/ai_adapter_service.py`

```python
from sqlalchemy.orm import Session

from app.repositories.settings_repo import SettingsRepository


class AIAdapterService:
    def __init__(self, db: Session) -> None:
        self.repo = SettingsRepository(db)

    def list_provider_configs(self):
        return self.repo.list_ai_providers()

    def get_active_provider(self, model_type: str):
        return self.repo.get_active_ai_provider(model_type)

    def build_future_client_config(self, model_type: str) -> dict | None:
        provider = self.get_active_provider(model_type)
        if provider is None:
            return None
        return {
            "provider_name": provider.provider_name,
            "endpoint": provider.endpoint,
            "model_type": provider.model_type,
        }
```

Implement CRUD endpoints for:

- `GET/POST/PUT /api/digital-humans`
- `GET/POST/PUT /api/settings/ai-providers`
- `GET/POST /api/settings/admin-users`
- `GET /api/operation-logs`

Log each successful write action into `operation_log`.

- [ ] **Step 4: Run the settings test**

Run:

```powershell
cd backend
.\.venv\Scripts\python -m pytest tests/test_settings.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```powershell
git add backend/app/schemas/settings.py backend/app/schemas/digital_human.py backend/app/repositories/settings_repo.py backend/app/services/digital_human_service.py backend/app/services/ai_adapter_service.py backend/app/api/routers/digital_humans.py backend/app/api/routers/settings.py backend/app/api/routers/operation_logs.py backend/tests/test_settings.py
git commit -m "feat: add configuration and audit APIs"
```

## Task 9: Scaffold the Vue Admin App and Core Navigation

**Files:**
- Create: `admin-web/*`
- Create: `admin-web/src/tests/LoginView.test.ts`
- Create: `admin-web/src/api/client.ts`
- Create: `admin-web/src/router/index.ts`
- Create: `admin-web/src/stores/auth.ts`
- Create: `admin-web/src/layouts/AdminLayout.vue`
- Create: `admin-web/src/views/LoginView.vue`
- Create: `admin-web/src/views/DashboardView.vue`

- [ ] **Step 1: Scaffold the Vite Vue TypeScript app**

Run:

```powershell
npm.cmd create vite@latest admin-web -- --template vue-ts
cd admin-web
npm.cmd install
npm.cmd install vue-router pinia axios element-plus echarts
npm.cmd install -D vitest @vitejs/plugin-vue @vue/test-utils jsdom
```

Expected: `admin-web` is created and `npm.cmd run dev` starts the Vite app.

- [ ] **Step 2: Write the failing login page test**

```ts
import { mount } from '@vue/test-utils'
import LoginView from '../views/LoginView.vue'

describe('LoginView', () => {
  it('renders username and password inputs', () => {
    const wrapper = mount(LoginView)

    expect(wrapper.text()).toContain('登录')
    expect(wrapper.find('input').exists()).toBe(true)
  })
})
```

- [ ] **Step 3: Run the test to verify it fails**

Run:

```powershell
cd admin-web
npm.cmd run test -- LoginView.test.ts
```

Expected: FAIL because the test script or the component is missing.

- [ ] **Step 4: Implement the frontend shell**

`admin-web/src/api/client.ts`

```ts
import axios from 'axios'

export const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
})
```

`admin-web/package.json`

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc -b && vite build",
    "test": "vitest run"
  }
}
```

`admin-web/src/stores/auth.ts`

```ts
import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: localStorage.getItem('accessToken') ?? '',
  }),
  actions: {
    setToken(token: string) {
      this.accessToken = token
      localStorage.setItem('accessToken', token)
    },
    clearToken() {
      this.accessToken = ''
      localStorage.removeItem('accessToken')
    },
  },
})
```

`admin-web/src/views/LoginView.vue`

```vue
<template>
  <div class="login-page">
    <h1>后台登录</h1>
    <el-form>
      <el-form-item label="用户名">
        <el-input v-model="form.username" />
      </el-form-item>
      <el-form-item label="密码">
        <el-input v-model="form.password" type="password" show-password />
      </el-form-item>
      <el-button type="primary">登录</el-button>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'

const form = reactive({
  username: '',
  password: '',
})
</script>
```

`admin-web/src/router/index.ts`

```ts
import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import LoginView from '../views/LoginView.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: LoginView },
    { path: '/', component: DashboardView },
  ],
})
```

- [ ] **Step 5: Run the frontend login test**

Run:

```powershell
cd admin-web
npm.cmd run test -- LoginView.test.ts
```

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```powershell
git add admin-web
git commit -m "feat: scaffold admin frontend shell"
```

## Task 10: Implement the Main Admin Pages and API Integration

**Files:**
- Create: `admin-web/src/components/AppSidebar.vue`
- Create: `admin-web/src/components/AppHeader.vue`
- Create: `admin-web/src/components/ImportUploadCard.vue`
- Create: `admin-web/src/components/SpotFormDrawer.vue`
- Create: `admin-web/src/components/KnowledgeChunkPreview.vue`
- Create: `admin-web/src/components/DashboardCharts.vue`
- Create: `admin-web/src/views/ScenicAreaView.vue`
- Create: `admin-web/src/views/ScenicSpotListView.vue`
- Create: `admin-web/src/views/ScenicSpotDetailView.vue`
- Create: `admin-web/src/views/KnowledgeDocumentView.vue`
- Create: `admin-web/src/views/KnowledgeDocumentDetailView.vue`
- Create: `admin-web/src/views/FaqView.vue`
- Create: `admin-web/src/views/ImportJobView.vue`
- Create: `admin-web/src/views/ImportJobDetailView.vue`
- Create: `admin-web/src/views/DigitalHumanView.vue`
- Create: `admin-web/src/views/SettingsAiProviderView.vue`
- Create: `admin-web/src/views/OperationLogView.vue`
- Create: `admin-web/src/tests/DashboardView.test.ts`
- Modify: `admin-web/src/router/index.ts`

- [ ] **Step 1: Write the failing dashboard view test**

```ts
import { mount } from '@vue/test-utils'
import DashboardView from '../views/DashboardView.vue'

describe('DashboardView', () => {
  it('renders the overview title', () => {
    const wrapper = mount(DashboardView)

    expect(wrapper.text()).toContain('运营概览')
  })
})
```

- [ ] **Step 2: Run the dashboard test to verify it fails**

Run:

```powershell
cd admin-web
npm.cmd run test -- DashboardView.test.ts
```

Expected: FAIL because the implemented view still uses the starter content.

- [ ] **Step 3: Implement shared layout and dashboard**

`admin-web/src/components/AppSidebar.vue`

```vue
<template>
  <el-menu router>
    <el-menu-item index="/">工作台</el-menu-item>
    <el-menu-item index="/scenic-areas">景区管理</el-menu-item>
    <el-menu-item index="/scenic-spots">景点管理</el-menu-item>
    <el-menu-item index="/knowledge/documents">知识管理</el-menu-item>
    <el-menu-item index="/imports">数据导入</el-menu-item>
    <el-menu-item index="/analytics/dashboard">数据大屏</el-menu-item>
    <el-menu-item index="/digital-humans">数字人配置</el-menu-item>
    <el-menu-item index="/settings/ai-providers">系统设置</el-menu-item>
  </el-menu>
</template>
```

`admin-web/src/views/DashboardView.vue`

```vue
<template>
  <div>
    <h2>运营概览</h2>
    <div class="stat-grid">
      <el-card>总事件量</el-card>
      <el-card>景点数量</el-card>
      <el-card>知识文档</el-card>
      <el-card>最近导入任务</el-card>
    </div>
  </div>
</template>
```

- [ ] **Step 4: Implement the remaining pages around real backend endpoints**

Implement each page with these exact responsibilities and API calls:

- `ScenicAreaView.vue`
  - call `GET/POST/PUT /api/scenic-areas`
- `ScenicSpotListView.vue`
  - call `GET /api/scenic-spots`
- `ScenicSpotDetailView.vue`
  - call `GET/PUT /api/scenic-spots/{id}`
- `KnowledgeDocumentView.vue`
  - call `GET /api/knowledge/documents` and `POST /api/knowledge/documents/upload`
- `KnowledgeDocumentDetailView.vue`
  - call `GET /api/knowledge/documents/{id}` and `GET /api/knowledge/documents/{id}/chunks`
- `FaqView.vue`
  - call `GET/POST/PUT/DELETE /api/knowledge/faqs`
- `ImportJobView.vue`
  - call `POST /api/imports/scenic-spots`, `POST /api/imports/knowledge-docs`, `POST /api/imports/behavior-events`, `GET /api/imports/jobs`
- `ImportJobDetailView.vue`
  - call `GET /api/imports/jobs/{id}` and `GET /api/imports/jobs/{id}/items`
- `DigitalHumanView.vue`
  - call `GET/POST/PUT /api/digital-humans`
- `SettingsAiProviderView.vue`
  - call `GET/POST/PUT /api/settings/ai-providers`
- `OperationLogView.vue`
  - call `GET /api/operation-logs`

All write actions should call the backend and refresh the list view on success.

- [ ] **Step 5: Run the frontend tests**

Run:

```powershell
cd admin-web
npm.cmd run test
```

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```powershell
git add admin-web/src
git commit -m "feat: implement admin management pages"
```

## Task 11: Verify the End-to-End Slice and Document Local Run Commands

**Files:**
- Modify: `README.md`
- Modify: `.env.example`
- Modify: `backend/tests/*`
- Modify: `admin-web/package.json`

- [ ] **Step 1: Write one end-to-end smoke test for the backend**

```python
from fastapi.testclient import TestClient

from app.main import app


def test_backend_smoke_flow(test_db_session, auth_headers) -> None:
    client = TestClient(app)

    overview = client.get("/api/dashboard/overview", headers=auth_headers)

    assert overview.status_code == 200
    assert "total_events" in overview.json()
```

- [ ] **Step 2: Run the full backend suite**

Run:

```powershell
cd backend
.\.venv\Scripts\python -m pytest tests -q
```

Expected: all backend tests PASS.

- [ ] **Step 3: Run the full frontend suite and production build**

Run:

```powershell
cd admin-web
npm.cmd run test
npm.cmd run build
```

Expected: tests PASS and `dist/` is generated successfully.

- [ ] **Step 4: Document local setup in README**

Add these sections to `README.md`:

````md
## Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
Copy-Item ..\.env.example .env
.\.venv\Scripts\python scripts/init_db.py
.\.venv\Scripts\python -m uvicorn app.main:app --reload
```

## Frontend

```powershell
cd admin-web
npm.cmd install
npm.cmd run dev
```
````

- [ ] **Step 5: Commit**

Run:

```powershell
git add README.md .env.example backend admin-web
git commit -m "docs: add local run and verification instructions"
```

## Self-Review

- Spec coverage check:
  - Backend bootstrap: covered by Task 1
  - Data models: covered by Task 2
  - Auth and audit: covered by Task 3 and Task 8
  - Scenic management: covered by Task 4 and Task 10
  - Knowledge docs and FAQ: covered by Task 5 and Task 10
  - Imports: covered by Task 6 and Task 7
  - Dashboard statistics: covered by Task 7 and Task 10
  - Digital human and AI provider config: covered by Task 8 and Task 10
  - End-to-end verification and run docs: covered by Task 11
- Placeholder scan:
  - No `TBD`, `TODO`, or deferred implementation placeholders remain.
- Type consistency:
  - Status values, route prefixes, and primary schema names are consistent across tasks.
