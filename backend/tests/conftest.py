from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.config import settings
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models import load_all_models
from app.models.admin_user import AdminUser
from app.models.visitor import Visitor


@pytest.fixture(autouse=True)
def disable_external_storage() -> Generator[None, None, None]:
    original_backend = settings.storage_backend
    settings.storage_backend = "local"
    try:
        yield
    finally:
        settings.storage_backend = original_backend


@pytest.fixture()
def test_db_session() -> Generator[Session, None, None]:
    load_all_models()
    engine = create_engine(
        "sqlite://",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(bind=engine)
    session = testing_session_local()
    session.add(
        AdminUser(
            username="admin",
            password_hash=hash_password("admin123"),
            role="super_admin",
            status="active",
        )
    )
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


@pytest.fixture()
def content_auth_headers(test_db_session) -> dict[str, str]:
    test_db_session.add(
        AdminUser(
            username="content_admin",
            password_hash=hash_password("content123"),
            role="content_admin",
            status="active",
        )
    )
    test_db_session.commit()

    client = TestClient(app)
    response = client.post(
        "/api/auth/login",
        json={"username": "content_admin", "password": "content123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def ops_auth_headers(test_db_session) -> dict[str, str]:
    test_db_session.add(
        AdminUser(
            username="ops_admin",
            password_hash=hash_password("ops123"),
            role="ops_admin",
            status="active",
        )
    )
    test_db_session.commit()

    client = TestClient(app)
    response = client.post(
        "/api/auth/login",
        json={"username": "ops_admin", "password": "ops123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def visitor_auth_headers(test_db_session) -> dict[str, str]:
    visitor = Visitor(openid="wx-test-visitor", nickname="测试游客")
    test_db_session.add(visitor)
    test_db_session.commit()
    test_db_session.refresh(visitor)
    token = create_access_token(f"visitor:{visitor.id}")
    return {"Authorization": f"Bearer {token}"}
