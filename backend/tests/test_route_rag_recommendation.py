from unittest.mock import AsyncMock, MagicMock, patch

import anyio
import pytest
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.models import load_all_models
from app.models.knowledge_chunk import KnowledgeChunk
from app.models.knowledge_document import KnowledgeDocument
from app.models.scenic_area import ScenicArea
from app.schemas.route_template import RouteRecommendationRequest


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
    session.add(ScenicArea(id=1, code="LS", name="灵山胜境", status="active"))
    session.commit()
    yield session
    session.close()


def test_route_rag_generates_structured_family_route(db_session):
    from app.services.route_rag_recommendation_service import RouteRAGRecommendationService

    llm_text = "推荐亲子家庭路线，全程约4小时，节奏轻松，适合带孩子边看表演边互动。"

    async def run():
        route_text = (
            "亲子家庭路线（4小时轻松游）\n"
            "路线规划：南门入园→九龙灌浴（观赏动态表演）→佛手广场（摸天下第一掌）"
            "→百子戏弥勒（亲子互动）→梵宫（欣赏艺术作品）→五印坛城（体验藏式文化）→出口\n"
            "讲解重点：九龙灌浴表演适合亲子观看。"
        )
        service = RouteRAGRecommendationService(db_session)
        llm_result = MagicMock()
        llm_result.text = llm_text

        with patch.object(service.rag_pipeline, "retrieve", new_callable=AsyncMock, return_value=[
            {"text": route_text, "title": "个性化游览路线推荐", "source": "knowledge_chunk", "score": 0.92}
        ]):
            with patch.object(service.rag_pipeline.llm_client, "generate", new_callable=AsyncMock, return_value=llm_result):
                return await service.generate(
                    RouteRecommendationRequest(
                        scenic_area_id=1,
                        interest_tags=["亲子"],
                        audience_tags=["家庭"],
                        duration_minutes=240,
                    )
                )

    result = anyio.run(run)

    assert result["fallback_used"] is False
    assert result["matched_template"]["template_type"] == "rag"
    assert result["matched_template"]["name"] == "亲子家庭路线（4小时轻松游）"
    assert result["summary"] == llm_text
    assert [spot["name"] for spot in result["spots"][:3]] == ["南门入园", "九龙灌浴", "佛手广场"]
    assert result["spots"][1]["highlight"] == "观赏动态表演"
    assert result["sources"][0]["title"] == "个性化游览路线推荐"


def test_route_rag_chat_answer_uses_knowledge_route(db_session):
    from app.services.route_rag_recommendation_service import RouteRAGRecommendationService

    async def run():
        service = RouteRAGRecommendationService(db_session)
        with patch.object(service, "generate", new_callable=AsyncMock, return_value={
            "matched_template": {
                "id": 0,
                "name": "自然风光爱好者路线（5小时全景游）",
                "template_type": "rag",
                "scenic_area_id": 1,
                "priority": 100,
            },
            "fallback_used": False,
            "match_reason": "基于知识库路线内容生成",
            "summary": "推荐自然风光路线，可重点游览佛足坛、九龙灌浴、菩提大道和灵山大佛。",
            "spots": [],
            "sources": [],
        }):
            return await service.generate_answer("我想看自然风光，推荐一条路线", scenic_area_id=1)

    answer = anyio.run(run)

    assert "自然风光路线" in answer
    assert "九龙灌浴" in answer


def test_route_rag_returns_structured_route_when_llm_is_slow(db_session):
    from app.services import route_rag_recommendation_service as route_service_module
    from app.services.route_rag_recommendation_service import RouteRAGRecommendationService

    async def run():
        route_text = (
            "亲子家庭路线（4小时轻松游）\n"
            "路线规划：南门入园→九龙灌浴（观赏动态表演）→佛手广场（摸天下第一掌）→出口\n"
            "讲解重点：九龙灌浴表演适合亲子观看。"
        )
        service = RouteRAGRecommendationService(db_session)

        async def slow_generate(*args, **kwargs):
            await anyio.sleep(0.2)
            result = MagicMock()
            result.text = "这段慢速模型文本不应该阻塞路线返回。"
            return result

        with patch.object(route_service_module, "ROUTE_LLM_TIMEOUT_SECONDS", 0.01):
            with patch.object(service.rag_pipeline, "retrieve", new_callable=AsyncMock, return_value=[
                {"text": route_text, "title": "个性化游览路线推荐", "source": "knowledge_chunk", "score": 0.92}
            ]):
                with patch.object(service.rag_pipeline.llm_client, "generate", side_effect=slow_generate):
                    start = time.perf_counter()
                    result = await service.generate(
                        RouteRecommendationRequest(
                            scenic_area_id=1,
                            interest_tags=["亲子"],
                            audience_tags=["家庭"],
                            duration_minutes=240,
                        )
                    )
                    elapsed = time.perf_counter() - start
                    return result, elapsed

    result, elapsed = anyio.run(run)

    assert elapsed < 0.12
    assert result["fallback_used"] is False
    assert result["matched_template"]["template_type"] == "rag"
    assert "亲子家庭路线" in result["summary"]
    assert [spot["name"] for spot in result["spots"]] == ["南门入园", "九龙灌浴", "佛手广场", "出口"]


def test_route_rag_uses_local_route_chunk_lookup_without_generic_rag(db_session):
    from app.services.route_rag_recommendation_service import RouteRAGRecommendationService

    document = KnowledgeDocument(
        scenic_area_id=1,
        title="灵山胜境：历史、文化、景点特色与个性化游览指南",
        doc_type="docx",
        source_name="guide.docx",
        status="active",
    )
    db_session.add(document)
    db_session.flush()
    db_session.add(
        KnowledgeChunk(
            document_id=document.id,
            chunk_index=1,
            chunk_text=(
                "自然风光爱好者路线（5小时全景游）\n"
                "路线规划：南门入园→佛足坛→九龙灌浴（观赏表演）→菩提大道（欣赏太湖风光）→出口"
            ),
            token_count=50,
            source_section="个性化游览路线推荐",
            status="active",
        )
    )
    db_session.commit()

    async def run():
        service = RouteRAGRecommendationService(db_session)
        llm_result = MagicMock()
        llm_result.text = "推荐自然风光爱好者路线，适合欣赏太湖风光。"

        with patch.object(service.rag_pipeline, "retrieve", new_callable=AsyncMock, side_effect=AssertionError("generic RAG should not run")):
            with patch.object(service.rag_pipeline.llm_client, "generate", new_callable=AsyncMock, return_value=llm_result):
                return await service.generate(
                    RouteRecommendationRequest(
                        scenic_area_id=1,
                        interest_tags=["自然风光"],
                        duration_minutes=300,
                    )
                )

    result = anyio.run(run)

    assert result["matched_template"]["name"] == "自然风光爱好者路线（5小时全景游）"
    assert [spot["name"] for spot in result["spots"][:3]] == ["南门入园", "佛足坛", "九龙灌浴"]


def test_route_rag_prefers_history_over_family_for_elderly_culture_request(db_session):
    from app.services.route_rag_recommendation_service import RouteRAGRecommendationService

    document = KnowledgeDocument(
        scenic_area_id=1,
        title="灵山胜境：历史、文化、景点特色与个性化游览指南",
        doc_type="docx",
        source_name="guide.docx",
        status="active",
    )
    db_session.add(document)
    db_session.flush()
    db_session.add(
        KnowledgeChunk(
            document_id=document.id,
            chunk_index=1,
            chunk_text=(
                "历史文化爱好者路线（6小时深度游）\n"
                "路线规划：南门入园→灵山大照壁→五明桥→佛足坛→五智门→菩提大道→祥符禅寺→灵山大佛→梵宫→出口\n"
                "亲子家庭路线（4小时轻松游）\n"
                "路线规划：南门入园→九龙灌浴→佛手广场→百子戏弥勒→梵宫→五印坛城→出口"
            ),
            token_count=120,
            source_section="个性化游览路线推荐",
            status="active",
        )
    )
    db_session.commit()

    async def run():
        service = RouteRAGRecommendationService(db_session)
        llm_result = MagicMock()
        llm_result.text = "为老人推荐历史文化路线的半天舒缓版，减少折返和停留压力。"

        with patch.object(service.rag_pipeline, "retrieve", new_callable=AsyncMock, side_effect=AssertionError("generic RAG should not run")):
            with patch.object(service.rag_pipeline.llm_client, "generate", new_callable=AsyncMock, return_value=llm_result):
                return await service.generate(
                    RouteRecommendationRequest(
                        scenic_area_id=1,
                        interest_tags=["文化"],
                        duration_minutes=180,
                        audience_tags=["老人"],
                    )
                )

    result = anyio.run(run)

    assert result["matched_template"]["name"].startswith("历史文化爱好者路线")
    assert "亲子家庭路线" not in result["matched_template"]["name"]
    assert "半天" in result["matched_template"]["name"]
    assert len(result["spots"]) < 10
    assert [spot["name"] for spot in result["spots"][:3]] == ["南门入园", "灵山大照壁", "五明桥"]

def test_route_rag_prefers_reroute_anchor_before_duration_trimming(db_session):
    from app.services.route_rag_recommendation_service import ParsedRoute, RouteRAGRecommendationService

    service = RouteRAGRecommendationService(db_session)
    parsed_route = ParsedRoute(
        title="Test Route",
        plan_text="",
        duration_minutes=300,
        spots=[
            {"scenic_spot_id": None, "name": "South Gate", "stay_minutes": 30, "highlight": None},
            {"scenic_spot_id": None, "name": "Lake Walk", "stay_minutes": 30, "highlight": None},
            {"scenic_spot_id": None, "name": "Tea House", "stay_minutes": 30, "highlight": None},
            {"scenic_spot_id": None, "name": "Nine Dragon Falls", "stay_minutes": 30, "highlight": None},
            {"scenic_spot_id": None, "name": "Buddha Plaza", "stay_minutes": 30, "highlight": None},
            {"scenic_spot_id": None, "name": "Exit", "stay_minutes": 30, "highlight": None},
        ],
    )

    adapted = service._adapt_route_to_payload(
        parsed_route,
        RouteRecommendationRequest(
            duration_minutes=90,
            reroute_from_spot_name="Nine Dragon Falls",
            end_spot_name="Exit",
        ),
    )

    assert [spot["name"] for spot in adapted.spots] == ["Nine Dragon Falls", "Buddha Plaza", "Exit"]


def test_route_rag_preserves_requested_end_spot_when_trimming(db_session):
    from app.services.route_rag_recommendation_service import ParsedRoute, RouteRAGRecommendationService

    service = RouteRAGRecommendationService(db_session)
    parsed_route = ParsedRoute(
        title="Test Route",
        plan_text="",
        duration_minutes=300,
        spots=[
            {"scenic_spot_id": None, "name": "South Gate", "stay_minutes": 30, "highlight": None},
            {"scenic_spot_id": None, "name": "Lake Walk", "stay_minutes": 30, "highlight": None},
            {"scenic_spot_id": None, "name": "Tea House", "stay_minutes": 30, "highlight": None},
            {"scenic_spot_id": None, "name": "Buddha Plaza", "stay_minutes": 30, "highlight": None},
            {"scenic_spot_id": None, "name": "Museum", "stay_minutes": 30, "highlight": None},
        ],
    )

    adapted = service._adapt_route_to_payload(
        parsed_route,
        RouteRecommendationRequest(
            duration_minutes=90,
            start_spot_name="South Gate",
            end_spot_name="Museum",
        ),
    )

    assert adapted.spots[-1]["name"] == "Museum"


def test_route_rag_builds_flexible_path_for_requested_lingshan_endpoints(db_session):
    from app.services.route_rag_recommendation_service import ParsedRoute, RouteRAGRecommendationService

    service = RouteRAGRecommendationService(db_session)
    parsed_route = ParsedRoute(
        title="历史文化爱好者路线（6小时深度游）",
        plan_text="",
        duration_minutes=360,
        spots=[
            {"scenic_spot_id": None, "name": "南门入园", "stay_minutes": 30, "highlight": None},
            {"scenic_spot_id": None, "name": "灵山大照壁", "stay_minutes": 30, "highlight": None},
            {"scenic_spot_id": None, "name": "胜境广场", "stay_minutes": 30, "highlight": None},
            {"scenic_spot_id": None, "name": "佛手广场", "stay_minutes": 30, "highlight": None},
            {"scenic_spot_id": None, "name": "祥符禅寺", "stay_minutes": 30, "highlight": None},
            {"scenic_spot_id": None, "name": "杏坛广场", "stay_minutes": 30, "highlight": None},
            {"scenic_spot_id": None, "name": "出口", "stay_minutes": 30, "highlight": None},
        ],
    )

    adapted = service._adapt_route_to_payload(
        parsed_route,
        RouteRecommendationRequest(
            duration_minutes=180,
            interest_tags=["历史文化"],
            audience_tags=["首次来访"],
            pace="normal",
            start_spot_name="灵山大照壁",
            end_spot_name="五坛印城",
        ),
    )

    spot_names = [spot["name"] for spot in adapted.spots]
    assert spot_names[0] == "灵山大照壁"
    assert spot_names[-1] == "五印坛城"
    assert "出口" not in spot_names
    assert "灵山梵宫" in spot_names


def test_route_rag_prefers_flexible_path_even_when_template_contains_requested_endpoint(db_session):
    from app.services.route_rag_recommendation_service import ParsedRoute, RouteRAGRecommendationService

    service = RouteRAGRecommendationService(db_session)
    parsed_route = ParsedRoute(
        title="历史文化爱好者路线（6小时深度游）",
        plan_text="",
        duration_minutes=360,
        spots=[
            {"scenic_spot_id": None, "name": "南门入园", "stay_minutes": 30, "highlight": None},
            {"scenic_spot_id": None, "name": "灵山大照壁", "stay_minutes": 30, "highlight": None},
            {"scenic_spot_id": None, "name": "胜境广场", "stay_minutes": 30, "highlight": None},
            {"scenic_spot_id": None, "name": "佛手广场", "stay_minutes": 30, "highlight": None},
            {"scenic_spot_id": None, "name": "祥符禅寺", "stay_minutes": 30, "highlight": None},
            {"scenic_spot_id": None, "name": "杏坛广场", "stay_minutes": 30, "highlight": None},
            {"scenic_spot_id": None, "name": "五印坛城", "stay_minutes": 30, "highlight": None},
        ],
    )

    adapted = service._adapt_route_to_payload(
        parsed_route,
        RouteRecommendationRequest(
            duration_minutes=180,
            interest_tags=["历史文化"],
            start_spot_name="灵山大照壁",
            end_spot_name="五印坛城",
        ),
    )

    spot_names = [spot["name"] for spot in adapted.spots]
    assert spot_names == ["灵山大照壁", "九龙灌浴", "祥符禅寺", "灵山大佛", "灵山梵宫", "五印坛城"]
    assert adapted.adapted_from_constraints is True
