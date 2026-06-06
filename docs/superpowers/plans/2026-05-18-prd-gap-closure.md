# PRD Gap Closure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the highest-impact PRD gaps that affect the tourist-side demonstration flow.

**Architecture:** Add a small `TouristExperienceService` for PRD-level tourist aggregation endpoints instead of spreading homepage, map-guide, and recent-record logic across routers. Keep route recommendation fast by preferring local route knowledge chunks before generic RAG and LLM calls.

**Tech Stack:** FastAPI, SQLAlchemy, Pydantic, pytest, UniApp/Vue 3, TypeScript.

---

### Task 1: Fast Route Knowledge Lookup

**Files:**
- Modify: `backend/app/services/route_rag_recommendation_service.py`
- Test: `backend/tests/test_route_rag_recommendation.py`

- [x] **Step 1: Write the failing test**

Add a test proving route recommendation can use local route chunks without calling generic RAG retrieval.

- [x] **Step 2: Run the test to verify it fails**

Run: `python -m pytest tests/test_route_rag_recommendation.py -q`

Expected: FAIL with `generic RAG should not run`.

- [x] **Step 3: Implement local route chunk lookup**

Add `_retrieve_route_chunks_from_db()` and call it before `rag_pipeline.retrieve()`.

- [x] **Step 4: Verify**

Run: `python -m pytest tests/test_route_rag_recommendation.py -q`

Expected: PASS.

### Task 2: Tourist Home, Map Guide, Recent Records APIs

**Files:**
- Create: `backend/app/services/tourist_experience_service.py`
- Modify: `backend/app/api/routers/tourist_chat.py`
- Modify: `backend/app/schemas/tourist.py`
- Test: `backend/tests/test_prd_tourist_api.py`

- [x] **Step 1: Write failing API tests**

Cover:
- `GET /api/tourist/home`
- `GET /api/tourist/map-guide`
- `GET /api/tourist/recent-records`

- [x] **Step 2: Run the test to verify it fails**

Run: `python -m pytest tests/test_prd_tourist_api.py -q`

Expected: FAIL with 404.

- [x] **Step 3: Implement schemas and service**

Add typed response models and aggregation service.

- [x] **Step 4: Wire router endpoints**

Register public tourist endpoints without admin auth.

- [x] **Step 5: Verify**

Run: `python -m pytest tests/test_prd_tourist_api.py -q`

Expected: PASS.

### Task 3: Mini Program Integration

**Files:**
- Modify: `miniprogram/src/types/api.ts`
- Modify: `miniprogram/src/api/tourist.ts`
- Modify: `miniprogram/src/pages/index/index.vue`
- Modify: `miniprogram/src/pages/map/map.vue`
- Modify: `miniprogram/src/pages/my/my.vue`

- [x] **Step 1: Add API types and clients**

Add `TouristHomeConfig`, `MapGuideData`, `RecentRecord` and client functions.

- [x] **Step 2: Connect pages**

Use:
- `getTouristHomeConfig()` on homepage
- `getMapGuideData()` on map page
- `getRecentRecords()` from My page history entry

- [x] **Step 3: Verify build**

Run: `npm.cmd run build:mp-weixin`

Expected: build complete.

### Task 4: PRD Audit Documentation

**Files:**
- Create: `docs/prd-gap-analysis-and-plan-2026-05-18.md`

- [x] **Step 1: Summarize implemented and missing PRD items**

Group by P0, P1, P2.

- [x] **Step 2: Record development roadmap**

List stabilization, backend analytics, and polish phases.

- [x] **Step 3: Include verification commands**

Document backend test and mini-program build commands.

### Task 5: Route And Map Runtime Stabilization

**Files:**
- Modify: `backend/app/services/route_rag_recommendation_service.py`
- Modify: `backend/app/services/tourist_experience_service.py`
- Test: `backend/tests/test_prd_tourist_api.py`

- [x] **Step 1: Add fallback service POI test**

Verify `GET /api/tourist/map-guide` still returns service points when the database has none.

- [x] **Step 2: Implement fallback POIs**

Return toilet, service center, restaurant, and parking fallback entries from `TouristExperienceService`.

- [x] **Step 3: Shorten route LLM wait**

Set route RAG LLM timeout to 2 seconds so route pages can return a structured fallback quickly.

- [x] **Step 4: Verify**

Run: `python -m pytest tests/test_prd_tourist_api.py tests/test_route_rag_recommendation.py -q`

Expected: PASS.
