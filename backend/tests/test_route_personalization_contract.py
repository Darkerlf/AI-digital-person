from unittest.mock import AsyncMock, MagicMock, patch

import anyio

from app.models.knowledge_chunk import KnowledgeChunk
from app.models.knowledge_document import KnowledgeDocument
from app.models.route_recommendation_record import RouteRecommendationRecord
from app.schemas.route_template import RouteRecommendationRequest
from app.services.route_rag_recommendation_service import RouteRAGRecommendationService


def test_route_request_accepts_richer_personalization_fields() -> None:
    payload = RouteRecommendationRequest(
        scenic_area_id=1,
        duration_minutes=180,
        interest_tags=["文化"],
        audience_tags=["老人"],
        start_spot_name="南门入口",
        end_spot_name="出口",
        pace="relaxed",
        mobility_tags=["少台阶"],
        service_needs=["卫生间"],
        reroute_from_spot_name="九龙灌浴",
    )

    assert payload.start_spot_name == "南门入口"
    assert payload.reroute_from_spot_name == "九龙灌浴"
    assert payload.service_needs == ["卫生间"]


def test_route_rag_uses_reroute_context_and_persists_request(test_db_session) -> None:
    document = KnowledgeDocument(
        scenic_area_id=1,
        title="Route Knowledge",
        doc_type="markdown",
        source_name="route.md",
        status="active",
    )
    test_db_session.add(document)
    test_db_session.flush()
    test_db_session.add(
        KnowledgeChunk(
            document_id=document.id,
            chunk_index=1,
            chunk_text=(
                "亲子家庭路线（4小时轻松游）\n"
                "路线规划：南门入口→九龙灌浴（观看演出）→佛手广场（拍照）→梵宫（艺术）→出口\n"
                "讲解重点：节奏轻松，适合亲子和老人。"
            ),
            token_count=80,
            source_section="个性化游览路线推荐",
            status="active",
        )
    )
    test_db_session.commit()

    async def run():
        service = RouteRAGRecommendationService(test_db_session)
        llm_result = MagicMock()
        llm_result.text = "从九龙灌浴继续游览，优先少走路并预留卫生间休息。"
        with patch.object(service.rag_pipeline.llm_client, "generate", new_callable=AsyncMock, return_value=llm_result):
            return await service.generate(
                RouteRecommendationRequest(
                    scenic_area_id=1,
                    duration_minutes=120,
                    interest_tags=["艺术"],
                    audience_tags=["老人"],
                    start_spot_name="南门入口",
                    end_spot_name="出口",
                    pace="relaxed",
                    mobility_tags=["少台阶"],
                    service_needs=["卫生间"],
                    reroute_from_spot_name="九龙灌浴",
                )
            )

    result = anyio.run(run)

    assert result["spots"][0]["name"] == "九龙灌浴"
    assert result["spots"][-1]["name"] == "出口"
    record = test_db_session.query(RouteRecommendationRecord).one()
    assert record.request_json["reroute_from_spot_name"] == "九龙灌浴"
    assert record.request_json["mobility_tags"] == ["少台阶"]
    assert record.request_json["service_needs"] == ["卫生间"]
