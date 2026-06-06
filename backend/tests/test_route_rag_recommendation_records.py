from unittest.mock import AsyncMock, MagicMock, patch

import anyio
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.models import load_all_models
from app.models.route_recommendation_record import RouteRecommendationRecord
from app.models.scenic_area import ScenicArea
from app.schemas.route_template import RouteRecommendationRequest
from app.services.route_rag_recommendation_service import RouteRAGRecommendationService


@pytest.fixture
def db_session():
    load_all_models()
    engine = create_engine(
        "sqlite://",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)()
    session.add(ScenicArea(id=1, code="LS", name="Route Area", status="active"))
    session.commit()
    yield session
    session.close()


def test_route_rag_persists_recommendation_record(db_session):
    async def run():
        service = RouteRAGRecommendationService(db_session)
        llm_result = MagicMock()
        llm_result.text = "RAG route summary"
        route_chunks = [{"text": "route plan text", "title": "route", "source": "knowledge_chunk", "score": 0.9}]

        with patch.object(service.rag_pipeline, "retrieve", new_callable=AsyncMock, return_value=route_chunks) as retrieve:
            with patch.object(service, "_filter_route_chunks", return_value=route_chunks):
                with patch.object(service.rag_pipeline.llm_client, "generate", new_callable=AsyncMock, return_value=llm_result):
                    result = await service.generate(
                        RouteRecommendationRequest(
                            scenic_area_id=1,
                            interest_tags=["family"],
                            audience_tags=["family"],
                            duration_minutes=120,
                            start_spot_name="South Gate",
                            end_spot_name="Museum",
                            pace="relaxed",
                            mobility_tags=["low stairs"],
                            service_needs=["restroom"],
                            reroute_from_spot_name="Tea House",
                        ),
                        message="family route",
                    )
                    return result, retrieve.await_args.args[0]

    result, query = anyio.run(run)

    record = db_session.execute(select(RouteRecommendationRecord)).scalar_one()
    assert record.source == "rag"
    assert record.scenic_area_id == 1
    assert record.duration_minutes == 120
    assert record.matched_template_name == result["matched_template"]["name"]
    assert record.request_json["message"] == "family route"
    assert record.request_json["start_spot_name"] == "South Gate"
    assert record.request_json["end_spot_name"] == "Museum"
    assert record.request_json["pace"] == "relaxed"
    assert record.request_json["mobility_tags"] == ["low stairs"]
    assert record.request_json["service_needs"] == ["restroom"]
    assert record.request_json["reroute_from_spot_name"] == "Tea House"
    assert record.response_json["summary"] == "RAG route summary"
    assert "South Gate" in query
    assert "Museum" in query
    assert "relaxed" in query
    assert "low stairs" in query
    assert "restroom" in query
    assert "Tea House" in query


def test_route_rag_returns_result_when_record_persistence_fails(db_session):
    async def run():
        service = RouteRAGRecommendationService(db_session)
        llm_result = MagicMock()
        llm_result.text = "RAG route summary"
        route_chunks = [{"text": "route plan text", "title": "route", "source": "knowledge_chunk", "score": 0.9}]

        with patch.object(service.rag_pipeline, "retrieve", new_callable=AsyncMock, return_value=route_chunks):
            with patch.object(service, "_filter_route_chunks", return_value=route_chunks):
                with patch.object(service.rag_pipeline.llm_client, "generate", new_callable=AsyncMock, return_value=llm_result):
                    with patch.object(db_session, "commit", side_effect=SQLAlchemyError("record table missing")):
                        with patch.object(db_session, "rollback") as rollback:
                            result = await service.generate(
                                RouteRecommendationRequest(
                                    scenic_area_id=1,
                                    interest_tags=["family"],
                                    audience_tags=["family"],
                                    duration_minutes=120,
                                )
                            )
                            return result, rollback.called

    result, rollback_called = anyio.run(run)

    assert result["summary"] == "RAG route summary"
    assert result["matched_template"]["template_type"] == "rag"
    assert rollback_called is True
