# Tourist Flow And ASR Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the visitor-facing demo loop by adding scenic narration, route recommendation, service POI lookup, full feedback entry, and real ASR integration.

**Architecture:** Keep the existing FastAPI + uni-app structure. Add visitor-safe read endpoints under `/api/tourist/*`, keep admin-only management endpoints separate, and build small mini-program pages that call these endpoints. ASR stays behind `ASRService` so the voice provider can be changed without touching routers.

**Tech Stack:** FastAPI, SQLAlchemy, pytest, uni-app/Vue 3, WeChat mini-program APIs, DashScope-compatible HTTP APIs.

---

### Task 1: Visitor Tour Data APIs

**Files:**
- Create: `backend/app/models/service_poi.py`
- Create: `backend/app/schemas/tourist.py`
- Modify: `backend/app/models/__init__.py`
- Modify: `backend/app/api/routers/tourist_chat.py`
- Test: `backend/tests/test_tourist_flow_api.py`

- [ ] Add failing tests for scenic narration, route recommendation without admin auth, service POI listing, and detailed feedback submission.
- [ ] Implement `ServicePOI` and visitor response schemas.
- [ ] Add visitor endpoints:
  - `GET /api/tourist/scenic-spots/{id}/narration?mode=brief|deep|family`
  - `POST /api/tourist/routes/recommend`
  - `GET /api/tourist/service-pois`
  - keep existing `POST /api/tourist/feedback`
- [ ] Seed service POI fallback data from code when DB has no rows.
- [ ] Run `python -m pytest tests/test_tourist_flow_api.py -q`.

### Task 2: Mini-Program Visitor Pages

**Files:**
- Modify: `miniprogram/src/pages.json`
- Modify: `miniprogram/src/api/tourist.ts`
- Modify: `miniprogram/src/types/api.ts`
- Modify: `miniprogram/src/pages/index/index.vue`
- Create: `miniprogram/src/pages/spot/spot.vue`
- Create: `miniprogram/src/pages/route/route.vue`
- Create: `miniprogram/src/pages/services/services.vue`
- Create: `miniprogram/src/pages/feedback/feedback.vue`
- Modify: `miniprogram/src/pages/guide/guide.vue`
- Modify: `miniprogram/src/pages/map/map.vue`

- [ ] Add pages and navigation routes.
- [ ] Build route recommendation form with interest, duration, audience, result list, and start-map action.
- [ ] Build scenic narration page with mode switch and ask-about-spot action.
- [ ] Build service POI page with category filters and map jump.
- [ ] Build feedback page with score, sentiment, and free text.
- [ ] Pass selected route to the map page through local storage.
- [ ] Run `npm.cmd run build:mp-weixin`.

### Task 3: Real ASR Integration

**Files:**
- Modify: `backend/app/services/asr_service.py`
- Modify: `backend/tests/test_tourist_voice_api.py`

- [ ] Add tests that mock DashScope ASR HTTP responses and verify recognized text is returned.
- [ ] Implement DashScope file transcription request with clear timeout and empty-text fallback.
- [ ] Keep failures non-fatal to the mini-program by returning empty text with existing UI retry messaging.
- [ ] Run `python -m pytest tests/test_tourist_voice_api.py -q`.

### Task 4: Verification

- [ ] Run focused backend tests:
  - `python -m pytest tests/test_tourist_flow_api.py tests/test_tourist_voice_api.py tests/test_route_templates.py tests/test_tourist_chat_api.py -q`
- [ ] Run mini-program build:
  - `npm.cmd run build:mp-weixin`
- [ ] Regenerate dev output:
  - `npm.cmd run dev:mp-weixin`
