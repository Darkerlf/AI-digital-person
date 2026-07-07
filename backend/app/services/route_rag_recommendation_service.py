import asyncio
import logging
import re
from dataclasses import dataclass
from difflib import SequenceMatcher

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.knowledge_chunk import KnowledgeChunk
from app.models.knowledge_document import KnowledgeDocument
from app.models.route_recommendation_record import RouteRecommendationRecord
from app.schemas.route_template import RouteRecommendationRequest
from app.services.rag_pipeline import RAGPipeline
from app.services.route_recommendation_service import RouteRecommendationService


ROUTE_SYSTEM_PROMPT = """你是灵山胜境的真人导览员。请只依据参考资料中的路线内容，为游客生成路线推荐。
要求：
1. 先自然说明推荐路线名称和预计用时，不要像表格字段一样罗列。
2. 按游览顺序讲清关键景点，并用转场把前后景点串起来，让游客感觉是在被带着走。
3. 语气自然，适合微信小程序语音播报；不要使用emoji、Markdown标题或生硬编号。
4. 如果资料没有覆盖用户的具体偏好，说明已按最接近路线调整，不要编造景点。"""


ROUTE_TITLES = [
    "历史文化爱好者路线（6小时深度游）",
    "自然风光爱好者路线（5小时全景游）",
    "亲子家庭路线（4小时轻松游）",
]

ROUTE_KEYWORDS = (
    "个性化游览路线推荐",
    "路线规划",
    "历史文化爱好者路线",
    "自然风光爱好者路线",
    "亲子家庭路线",
    "讲解重点",
    "特色体验",
)

ROUTE_PROFILE_KEYWORDS = {
    "历史文化爱好者路线": ("历史", "文化", "佛教", "艺术", "深度", "禅寺"),
    "自然风光爱好者路线": ("自然", "风光", "太湖", "拍照", "全景", "休闲"),
    "亲子家庭路线": ("亲子", "孩子", "家庭"),
}

SCENIC_WALK_SEQUENCE = [
    "灵山大照壁",
    "五明桥",
    "佛足坛",
    "五智门",
    "菩提大道",
    "九龙灌浴",
    "降魔浮雕",
    "阿育王柱",
    "百子戏弥勒",
    "祥符禅寺",
    "灵山大佛",
    "佛教文化博览馆",
    "灵山梵宫",
    "五印坛城",
]

SCENIC_SPOT_ALIASES = {
    "大照壁": "灵山大照壁",
    "灵山照壁": "灵山大照壁",
    "五坛印城": "五印坛城",
    "五印城": "五印坛城",
    "五印坛": "五印坛城",
    "梵宫": "灵山梵宫",
    "大佛": "灵山大佛",
    "九龙灌浴广场": "九龙灌浴",
}

SCENIC_SPOT_HIGHLIGHTS = {
    "灵山大照壁": "从景区标志性入口出发，适合作为路线起点和拍照集合点。",
    "五明桥": "进入核心游线的过渡节点，节奏轻松。",
    "佛足坛": "适合补充佛教文化背景。",
    "五智门": "串联入口区和主游线的文化节点。",
    "菩提大道": "步行空间开阔，适合边走边听讲解。",
    "九龙灌浴": "灵山代表性动态景观，适合首次来访重点停留。",
    "降魔浮雕": "可串联佛教故事讲解。",
    "阿育王柱": "适合历史文化主题补充。",
    "百子戏弥勒": "氛围轻松，适合亲子和拍照。",
    "祥符禅寺": "历史文化路线的重要禅寺节点。",
    "灵山大佛": "核心地标，建议保留较完整的参观时间。",
    "佛教文化博览馆": "适合文化深度补充。",
    "灵山梵宫": "艺术与佛教文化展示重点。",
    "五印坛城": "藏传佛教文化展示节点，作为本次指定终点。",
}

SCENIC_SPOT_BASE_STAY_MINUTES = {
    "南门入园": 8,
    "出口": 6,
    "出园": 6,
    "灵山大照壁": 12,
    "五明桥": 10,
    "佛足坛": 18,
    "五智门": 12,
    "菩提大道": 15,
    "九龙灌浴": 32,
    "降魔浮雕": 15,
    "阿育王柱": 12,
    "百子戏弥勒": 22,
    "祥符禅寺": 28,
    "灵山大佛": 45,
    "佛教文化博览馆": 28,
    "灵山梵宫": 50,
    "五印坛城": 35,
    "佛手广场": 18,
}

FLEXIBLE_ROUTE_PRIORITY = {
    "history": ["九龙灌浴", "祥符禅寺", "灵山大佛", "灵山梵宫", "佛足坛", "五印坛城"],
    "nature": ["五明桥", "菩提大道", "九龙灌浴", "百子戏弥勒", "灵山大佛", "五印坛城"],
    "family": ["五明桥", "九龙灌浴", "百子戏弥勒", "灵山大佛", "灵山梵宫", "五印坛城"],
}

ROUTE_LLM_TIMEOUT_SECONDS = 2.0
logger = logging.getLogger(__name__)


@dataclass
class ParsedRoute:
    title: str
    plan_text: str
    spots: list[dict]
    duration_minutes: int
    adapted_from_constraints: bool = False


class RouteRAGRecommendationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.rag_pipeline = RAGPipeline(db)
        self.template_service = RouteRecommendationService(db)

    async def generate_answer(
        self,
        message: str,
        scenic_area_id: int | None = None,
        history: list[dict[str, str]] | None = None,
    ) -> str:
        payload = RouteRecommendationRequest(
            scenic_area_id=scenic_area_id,
            duration_minutes=self._infer_duration_minutes(message),
            interest_tags=self._infer_interest_tags(message),
            audience_tags=self._infer_audience_tags(message),
        )
        result = await self.generate(payload, message=message, history=history)
        return result.get("summary") or result["match_reason"]

    async def generate(
        self,
        payload: RouteRecommendationRequest,
        message: str | None = None,
        history: list[dict[str, str]] | None = None,
    ) -> dict:
        query = self._build_query(payload, message)
        route_chunks = self._retrieve_route_chunks_from_db(query, payload.scenic_area_id)
        if not route_chunks:
            chunks = await self.rag_pipeline.retrieve(query)
            route_chunks = self._filter_route_chunks(chunks)

        if not route_chunks:
            return self._fallback_to_template(payload)

        context = self.rag_pipeline.build_context(route_chunks)
        parsed_route = self._parse_best_route("\n".join(chunk["text"] for chunk in route_chunks), query)
        user_message = message or query
        if not parsed_route:
            parsed_route = ParsedRoute(
                title="知识库推荐路线",
                plan_text="",
                spots=[],
                duration_minutes=payload.duration_minutes,
            )
        parsed_route = self._adapt_route_to_payload(parsed_route, payload)

        summary = await self._generate_summary_with_timeout(
            user_message=user_message,
            context=context,
            history=history,
            parsed_route=parsed_route,
        )

        result = {
            "matched_template": {
                "id": 0,
                "name": parsed_route.title,
                "template_type": "dynamic_rag" if parsed_route.adapted_from_constraints else "rag",
                "scenic_area_id": payload.scenic_area_id or 1,
                "priority": 100,
            },
            "fallback_used": False,
            "match_reason": (
                "已按用户指定起终点动态规划路线，并参考知识库中的路线主题和讲解重点。"
                if parsed_route.adapted_from_constraints
                else "基于知识库中“个性化游览路线推荐”内容检索并生成。"
            ),
            "summary": summary,
            "spots": parsed_route.spots,
            "sources": [
                {
                    "title": chunk.get("title"),
                    "source": chunk.get("source"),
                    "score": chunk.get("score"),
                }
                for chunk in route_chunks[:5]
            ],
            "duration_breakdown": self._build_duration_breakdown(
                parsed_route.spots,
                parsed_route.duration_minutes,
                pace=payload.pace,
            ),
        }
        self._record_generation(payload, result, message=message, history=history)
        return result

    def _record_generation(
        self,
        payload: RouteRecommendationRequest,
        result: dict,
        message: str | None = None,
        history: list[dict[str, str]] | None = None,
    ) -> None:
        matched_template = result["matched_template"]
        request_json = payload.model_dump()
        if message is not None:
            request_json["message"] = message
        if history:
            request_json["history"] = history
        try:
            self.db.add(
                RouteRecommendationRecord(
                    scenic_area_id=payload.scenic_area_id,
                    source=matched_template["template_type"],
                    duration_minutes=payload.duration_minutes,
                    matched_template_id=matched_template["id"] or None,
                    matched_template_name=matched_template["name"],
                    fallback_used=result["fallback_used"],
                    request_json=request_json,
                    response_json=result,
                )
            )
            self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()
            logger.exception("Failed to persist route recommendation record")

    async def _generate_summary_with_timeout(
        self,
        user_message: str,
        context: str,
        history: list[dict[str, str]] | None,
        parsed_route: ParsedRoute,
    ) -> str:
        try:
            result = await asyncio.wait_for(
                self.rag_pipeline.llm_client.generate(
                    system_prompt=ROUTE_SYSTEM_PROMPT,
                    user_message=user_message,
                    context=context,
                    history=history,
                ),
                timeout=ROUTE_LLM_TIMEOUT_SECONDS,
            )
            text = result.text.strip()
            if text:
                return text
        except Exception:
            pass
        return self._build_fast_summary(parsed_route)

    def _build_fast_summary(self, parsed_route: ParsedRoute) -> str:
        spot_names = [spot["name"] for spot in parsed_route.spots]
        route_line = "→".join(spot_names) if spot_names else parsed_route.plan_text
        hours = parsed_route.duration_minutes / 60
        duration_text = f"{hours:g}小时" if parsed_route.duration_minutes % 60 == 0 else f"{parsed_route.duration_minutes}分钟"
        if route_line:
            return (
                f"为您推荐{parsed_route.title}，预计用时约{duration_text}。"
                f"游览顺序为：{route_line}。"
                "这条路线来自知识库中的个性化游览路线内容，已优先保证可以快速生成和展示。"
            )
        return f"为您推荐{parsed_route.title}，预计用时约{duration_text}。"

    def _fallback_to_template(self, payload: RouteRecommendationRequest) -> dict:
        try:
            result = self.template_service.generate(payload)
            result.setdefault("sources", [])
            return result
        except Exception:
            return {
                "matched_template": {
                    "id": 0,
                    "name": "灵山胜境推荐路线",
                    "template_type": "fallback",
                    "scenic_area_id": payload.scenic_area_id or 1,
                    "priority": 0,
                },
                "fallback_used": True,
                "match_reason": "当前知识库和路线模板暂未命中，请补充游览时长或偏好后重试。",
                "summary": "可以告诉我您的游览时长、是否带老人孩子、偏好历史文化还是自然风光，我会再为您规划路线。",
                "spots": [],
                "sources": [],
            }

    def _build_query(self, payload: RouteRecommendationRequest, message: str | None) -> str:
        tags = " ".join(
            payload.interest_tags
            + payload.audience_tags
            + payload.mobility_tags
            + payload.service_needs
        )
        duration = f"{payload.duration_minutes}分钟"
        route_context = " ".join(
            part
            for part in [
                f"从{payload.start_spot_name}出发" if payload.start_spot_name else "",
                f"到{payload.end_spot_name}结束" if payload.end_spot_name else "",
                f"从{payload.reroute_from_spot_name}重新规划" if payload.reroute_from_spot_name else "",
                f"{payload.pace}节奏" if payload.pace else "",
            ]
            if part
        )
        route_hints = " ".join(self._route_query_hints(payload, message))
        raw_query = " ".join(part for part in [message, tags, duration, route_context, route_hints] if part)
        return (
            f"{raw_query} 个性化游览路线推荐 路线规划 讲解重点 特色体验"
        ).strip()

    def _route_query_hints(self, payload: RouteRecommendationRequest, message: str | None) -> list[str]:
        query = " ".join(
            [
                message or "",
                *payload.interest_tags,
                *payload.audience_tags,
                *payload.mobility_tags,
                *payload.service_needs,
                payload.start_spot_name or "",
                payload.end_spot_name or "",
                payload.reroute_from_spot_name or "",
            ]
        )
        hints = []
        if any(word in query for word in ROUTE_PROFILE_KEYWORDS["历史文化爱好者路线"]):
            hints.append("历史文化爱好者路线")
        if any(word in query for word in ROUTE_PROFILE_KEYWORDS["自然风光爱好者路线"]):
            hints.append("自然风光爱好者路线")
        if any(word in query for word in ROUTE_PROFILE_KEYWORDS["亲子家庭路线"]):
            hints.append("亲子家庭路线")
        return hints

    def _filter_route_chunks(self, chunks: list[dict]) -> list[dict]:
        return [
            chunk for chunk in chunks
            if any(keyword in chunk.get("text", "") for keyword in ROUTE_KEYWORDS)
        ]

    def _retrieve_route_chunks_from_db(self, query: str, scenic_area_id: int | None) -> list[dict]:
        statement = (
            select(KnowledgeChunk, KnowledgeDocument)
            .join(KnowledgeDocument, KnowledgeDocument.id == KnowledgeChunk.document_id)
            .where(KnowledgeChunk.status == "active", KnowledgeDocument.status == "active")
            .order_by(KnowledgeDocument.id.asc(), KnowledgeChunk.chunk_index.asc())
        )
        if scenic_area_id:
            statement = statement.where(KnowledgeDocument.scenic_area_id == scenic_area_id)

        rows = self.db.execute(statement).all()
        scored_chunks = []
        query_terms = set(self._infer_interest_tags(query) + self._infer_audience_tags(query))
        for chunk, document in rows:
            text = chunk.chunk_text or ""
            keyword_hits = sum(1 for keyword in ROUTE_KEYWORDS if keyword in text)
            if keyword_hits == 0:
                continue
            preference_hits = sum(1 for term in query_terms if term and term in text)
            score = min(0.98, 0.72 + keyword_hits * 0.04 + preference_hits * 0.06)
            scored_chunks.append(
                (
                    document.id,
                    chunk.chunk_index,
                    {
                        "text": text,
                        "source": "document_route",
                        "title": chunk.source_section or f"文档片段#{chunk.chunk_index}",
                        "score": score,
                    },
                )
            )

        scored_chunks.sort(key=lambda item: (item[0], item[1]))
        return [item[2] for item in scored_chunks[:8]]

    def _parse_best_route(self, text: str, query: str) -> ParsedRoute | None:
        title = self._select_route_title(text, query)
        if not title:
            return None

        section = self._extract_route_section(text, title)
        plan_match = re.search(r"路线规划[:：]\s*(.+)", section)
        if not plan_match:
            return ParsedRoute(title=title, plan_text="", spots=[], duration_minutes=self._route_duration(title, 240))

        plan_text = plan_match.group(1).splitlines()[0].strip()
        stops = [item.strip() for item in re.split(r"\s*→\s*", plan_text) if item.strip()]
        duration_minutes = self._route_duration(title, 240)
        spots = []
        for stop in stops:
            name, highlight = self._split_stop(stop)
            spots.append(
                {
                    "scenic_spot_id": None,
                    "name": name,
                    "stay_minutes": self._base_stay_minutes(name),
                    "highlight": highlight,
                }
            )

        return ParsedRoute(title=title, plan_text=plan_text, spots=spots, duration_minutes=duration_minutes)

    def _adapt_route_to_payload(self, parsed_route: ParsedRoute, payload: RouteRecommendationRequest) -> ParsedRoute:
        if not parsed_route.spots:
            return parsed_route

        target_minutes = payload.duration_minutes
        flexible_spots = self._build_flexible_route_spots(parsed_route.spots, payload)
        context_spots = flexible_spots or self._trim_spots_for_route_context(parsed_route.spots, payload)
        dynamic_route_used = flexible_spots is not None
        context_changed = context_spots != parsed_route.spots
        selected_spots = context_spots
        duration_adjusted = payload.duration_minutes < parsed_route.duration_minutes
        if duration_adjusted:
            max_stops = max(3, min(len(context_spots), target_minutes // 35 + 1))
            has_exit = context_spots[-1]["name"] in {"出口", "出园", "南门出园", "Exit"}
            end_requested = (
                payload.end_spot_name
                and self._find_spot_index([context_spots[-1]], payload.end_spot_name) is not None
            )
            preserve_last_spot = has_exit or end_requested
            if preserve_last_spot and max_stops < len(context_spots):
                selected_spots = context_spots[: max_stops - 1] + [context_spots[-1]]
            else:
                selected_spots = context_spots[:max_stops]

        adjusted_spots = [dict(spot) for spot in selected_spots]
        if dynamic_route_used:
            title_base = f"{adjusted_spots[0]['name']}至{adjusted_spots[-1]['name']}灵活路线"
        else:
            title_base = parsed_route.title.split("（")[0]
        title = (
            f"{title_base}（{self._duration_variant_label(payload)}）"
            if duration_adjusted or dynamic_route_used
            else parsed_route.title
        )
        adjusted_spots = self._redistribute_stay_minutes(
            adjusted_spots,
            total_minutes=target_minutes,
            pace=payload.pace,
        )
        return ParsedRoute(
            title=title,
            plan_text="→".join(spot["name"] for spot in adjusted_spots),
            spots=adjusted_spots,
            duration_minutes=target_minutes,
            adapted_from_constraints=dynamic_route_used,
        )

    def _build_duration_breakdown(
        self,
        spots: list[dict],
        total_minutes: int,
        pace: str | None = None,
    ) -> dict[str, int]:
        walking_minutes = self._estimate_walking_minutes(spots, pace)
        buffer_minutes = self._estimate_buffer_minutes(total_minutes, spots, pace)
        visit_minutes = max(0, total_minutes - walking_minutes - buffer_minutes)
        actual_visit_minutes = sum(int(spot.get("stay_minutes") or 0) for spot in spots)
        if actual_visit_minutes > 0:
            visit_minutes = actual_visit_minutes
        return {
            "total_minutes": total_minutes,
            "visit_minutes": visit_minutes,
            "walking_minutes": walking_minutes,
            "buffer_minutes": max(0, total_minutes - visit_minutes - walking_minutes),
        }

    def _redistribute_stay_minutes(
        self,
        spots: list[dict],
        *,
        total_minutes: int,
        pace: str | None = None,
    ) -> list[dict]:
        if not spots:
            return spots
        walking_minutes = self._estimate_walking_minutes(spots, pace)
        buffer_minutes = self._estimate_buffer_minutes(total_minutes, spots, pace)
        visit_budget = max(len(spots) * 10, total_minutes - walking_minutes - buffer_minutes)
        base_minutes = [self._base_stay_minutes(str(spot.get("name") or "")) for spot in spots]
        total_base = sum(base_minutes) or len(spots)
        allocated = [
            max(6, round(visit_budget * base_minute / total_base))
            for base_minute in base_minutes
        ]
        delta = visit_budget - sum(allocated)
        if delta:
            ordered_indexes = sorted(
                range(len(spots)),
                key=lambda index: base_minutes[index],
                reverse=delta > 0,
            )
            step = 1 if delta > 0 else -1
            remaining = abs(delta)
            cursor = 0
            while remaining and ordered_indexes:
                index = ordered_indexes[cursor % len(ordered_indexes)]
                if step > 0 or allocated[index] > 6:
                    allocated[index] += step
                    remaining -= 1
                cursor += 1
        return [
            {
                **spot,
                "stay_minutes": allocated[index],
            }
            for index, spot in enumerate(spots)
        ]

    @classmethod
    def _base_stay_minutes(cls, name: str) -> int:
        resolved_name = cls._resolve_scenic_spot_name(name) or name
        for keyword, minutes in SCENIC_SPOT_BASE_STAY_MINUTES.items():
            if keyword in resolved_name or keyword in name:
                return minutes
        return 20

    @staticmethod
    def _estimate_walking_minutes(spots: list[dict], pace: str | None = None) -> int:
        transitions = max(0, len(spots) - 1)
        per_leg = {
            "fast": 6,
            "standard": 8,
            "normal": 8,
            "relaxed": 10,
        }.get(pace or "standard", 8)
        return transitions * per_leg

    @staticmethod
    def _estimate_buffer_minutes(total_minutes: int, spots: list[dict], pace: str | None = None) -> int:
        if total_minutes < 90 or len(spots) <= 1:
            return 0
        ratio = 0.12 if pace == "relaxed" else 0.08
        return max(5, round(total_minutes * ratio))

    def _build_flexible_route_spots(
        self,
        template_spots: list[dict],
        payload: RouteRecommendationRequest,
    ) -> list[dict] | None:
        start_name = self._resolve_scenic_spot_name(payload.reroute_from_spot_name or payload.start_spot_name)
        end_name = self._resolve_scenic_spot_name(payload.end_spot_name)
        if not start_name or not end_name:
            return None

        try:
            start_index = SCENIC_WALK_SEQUENCE.index(start_name)
            end_index = SCENIC_WALK_SEQUENCE.index(end_name)
        except ValueError:
            return None

        if start_index <= end_index:
            route_names = SCENIC_WALK_SEQUENCE[start_index : end_index + 1]
        else:
            route_names = list(reversed(SCENIC_WALK_SEQUENCE[end_index : start_index + 1]))

        max_stops = max(3, min(len(route_names), payload.duration_minutes // 35 + 1))
        selected_names = self._select_flexible_spot_names(route_names, payload, max_stops)
        stay_minutes = max(10, payload.duration_minutes // max(len(selected_names), 1))
        return [
            {
                "scenic_spot_id": None,
                "name": name,
                "stay_minutes": stay_minutes,
                "highlight": SCENIC_SPOT_HIGHLIGHTS.get(name),
            }
            for name in selected_names
        ]

    def _select_flexible_spot_names(
        self,
        route_names: list[str],
        payload: RouteRecommendationRequest,
        max_stops: int,
    ) -> list[str]:
        if len(route_names) <= max_stops:
            return route_names

        selected = {route_names[0], route_names[-1]}
        priority_names = self._priority_spot_names(payload)
        for name in priority_names:
            if name in route_names:
                selected.add(name)
            if len(selected) >= max_stops:
                break

        if len(selected) < max_stops:
            interior = route_names[1:-1]
            if interior:
                step = max(1, len(interior) // max(max_stops - 2, 1))
                for name in interior[::step]:
                    selected.add(name)
                    if len(selected) >= max_stops:
                        break

        return [name for name in route_names if name in selected]

    def _priority_spot_names(self, payload: RouteRecommendationRequest) -> list[str]:
        query = " ".join([*payload.interest_tags, *payload.audience_tags, payload.pace or ""])
        if any(word in query for word in ("亲子", "孩子", "家庭")):
            return FLEXIBLE_ROUTE_PRIORITY["family"]
        if any(word in query for word in ("自然", "风光", "拍照", "轻松")):
            return FLEXIBLE_ROUTE_PRIORITY["nature"]
        return FLEXIBLE_ROUTE_PRIORITY["history"]

    def _trim_spots_for_route_context(self, spots: list[dict], payload: RouteRecommendationRequest) -> list[dict]:
        anchor = payload.reroute_from_spot_name or payload.start_spot_name
        selected_spots = spots
        if anchor:
            start_index = self._find_spot_index(selected_spots, anchor)
            if start_index is not None:
                selected_spots = selected_spots[start_index:]

        if payload.end_spot_name:
            end_index = self._find_spot_index(selected_spots, payload.end_spot_name)
            if end_index is not None:
                selected_spots = selected_spots[: end_index + 1]

        return selected_spots or spots

    @classmethod
    def _find_spot_index(cls, spots: list[dict], name: str) -> int | None:
        normalized_name = name.strip()
        resolved_name = cls._resolve_scenic_spot_name(normalized_name)
        for index, spot in enumerate(spots):
            spot_name = str(spot.get("name") or "").strip()
            if spot_name == normalized_name or normalized_name in spot_name or spot_name in normalized_name:
                return index
            resolved_spot_name = cls._resolve_scenic_spot_name(spot_name)
            if resolved_name and resolved_spot_name and resolved_name == resolved_spot_name:
                return index
        return None

    @classmethod
    def _resolve_scenic_spot_name(cls, name: str | None) -> str | None:
        if not name:
            return None
        normalized_name = cls._normalize_spot_name(name)
        alias_name = SCENIC_SPOT_ALIASES.get(normalized_name)
        if alias_name:
            return alias_name

        candidates = [*SCENIC_WALK_SEQUENCE, *SCENIC_SPOT_ALIASES.values()]
        unique_candidates = list(dict.fromkeys(candidates))
        for candidate in unique_candidates:
            normalized_candidate = cls._normalize_spot_name(candidate)
            if (
                normalized_name == normalized_candidate
                or normalized_name in normalized_candidate
                or normalized_candidate in normalized_name
            ):
                return candidate

        scored_candidates = [
            (
                SequenceMatcher(None, normalized_name, cls._normalize_spot_name(candidate)).ratio(),
                candidate,
            )
            for candidate in unique_candidates
        ]
        score, candidate = max(scored_candidates, default=(0, None))
        return candidate if score >= 0.72 else None

    @staticmethod
    def _normalize_spot_name(name: str) -> str:
        return re.sub(r"[\s,，。.!！?？、\-_/（）()]+", "", name.strip())

    @staticmethod
    def _duration_variant_label(payload: RouteRecommendationRequest) -> str:
        if payload.duration_minutes <= 75:
            return "1小时精简版"
        if payload.duration_minutes <= 210:
            return "半天舒缓版" if "老人" in payload.audience_tags else "半天精简版"
        return f"{payload.duration_minutes // 60}小时调整版"

    def _select_route_title(self, text: str, query: str) -> str | None:
        available_titles = [title for title in ROUTE_TITLES if title in text]
        if not available_titles:
            return None

        query = query.lower()
        requested_minutes = self._duration_from_query(query)
        scored_titles = []
        for title in available_titles:
            prefix = self._route_prefix(title)
            score = self._route_preference_score(prefix, query)
            if requested_minutes is not None:
                duration_gap = abs(requested_minutes - self._route_duration(title, requested_minutes))
                score += max(0, 30 - duration_gap / 10)
            if "老人" in query and prefix == "亲子家庭路线" and not any(word in query for word in ROUTE_PROFILE_KEYWORDS["亲子家庭路线"]):
                score -= 40
            scored_titles.append((score, -available_titles.index(title), title))

        scored_titles.sort(reverse=True)
        return scored_titles[0][2]

    def _extract_route_section(self, text: str, title: str) -> str:
        start = text.find(title)
        if start < 0:
            return text
        next_positions = [
            text.find(other_title, start + len(title))
            for other_title in ROUTE_TITLES
            if other_title != title and text.find(other_title, start + len(title)) > -1
        ]
        end = min(next_positions) if next_positions else len(text)
        return text[start:end]

    @staticmethod
    def _first_available(titles: list[str], prefix: str) -> str:
        for title in titles:
            if title.startswith(prefix):
                return title
        return titles[0]

    @staticmethod
    def _route_prefix(title: str) -> str:
        for prefix in ROUTE_PROFILE_KEYWORDS:
            if title.startswith(prefix):
                return prefix
        return title

    @staticmethod
    def _route_preference_score(prefix: str, query: str) -> float:
        keywords = ROUTE_PROFILE_KEYWORDS.get(prefix, ())
        return sum(100 for word in keywords if word in query)

    @staticmethod
    def _duration_from_query(query: str) -> int | None:
        minute_match = re.search(r"(\d+)\s*分钟", query)
        if minute_match:
            return int(minute_match.group(1))
        hour_match = re.search(r"(\d+)\s*小时", query)
        if hour_match:
            return int(hour_match.group(1)) * 60
        return None

    @staticmethod
    def _split_stop(stop: str) -> tuple[str, str | None]:
        match = re.match(r"(.+?)[（(](.+?)[）)]$", stop)
        if not match:
            return stop, None
        return match.group(1).strip(), match.group(2).strip()

    @staticmethod
    def _route_duration(title: str, default_minutes: int) -> int:
        match = re.search(r"(\d+)小时", title)
        if not match:
            return default_minutes
        return int(match.group(1)) * 60

    @staticmethod
    def _infer_duration_minutes(message: str) -> int:
        hour_match = re.search(r"(\d+)\s*小时", message)
        if hour_match:
            return int(hour_match.group(1)) * 60
        minute_match = re.search(r"(\d+)\s*分钟", message)
        if minute_match:
            return int(minute_match.group(1))
        if any(word in message for word in ("亲子", "家庭", "轻松")):
            return 240
        if any(word in message for word in ("自然", "风光")):
            return 300
        if any(word in message for word in ("历史", "文化", "深度")):
            return 360
        return 240

    @staticmethod
    def _infer_interest_tags(message: str) -> list[str]:
        tags = []
        if any(word in message for word in ("历史", "文化", "佛教", "深度")):
            tags.append("历史文化")
        if any(word in message for word in ("自然", "风光", "太湖", "拍照")):
            tags.append("自然风光")
        if any(word in message for word in ("亲子", "孩子", "家庭")):
            tags.append("亲子")
        return tags

    @staticmethod
    def _infer_audience_tags(message: str) -> list[str]:
        tags = []
        if any(word in message for word in ("亲子", "孩子", "家庭")):
            tags.append("家庭")
        if "老人" in message:
            tags.append("老人")
        return tags
