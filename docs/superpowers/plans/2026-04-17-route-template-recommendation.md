# Route Template Recommendation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build route-template CRUD and a deterministic route-recommendation API, then expose both through the admin page so operators can curate templates and preview recommendation results.

**Architecture:** Extend the existing FastAPI modular monolith with a new `route_templates` slice that follows the current `models -> repositories -> services -> routers` pattern. Keep recommendation logic in a dedicated service so the admin preview and future visitor-side clients call the same backend contract, while the Vue admin page stays as a thin form/list/preview client over those APIs.

**Tech Stack:** Python 3.13, FastAPI, SQLAlchemy 2, Pydantic 2, pytest, Vue 3, TypeScript, Vue Router, Axios, Vitest, Vite.

---

## File Structure

### Backend

- Create: `backend/app/models/route_template.py`
- Create: `backend/app/models/route_template_spot.py`
- Create: `backend/app/schemas/route_template.py`
- Create: `backend/app/repositories/route_template_repo.py`
- Create: `backend/app/services/route_template_service.py`
- Create: `backend/app/services/route_recommendation_service.py`
- Create: `backend/app/api/routers/route_templates.py`
- Create: `backend/app/api/routers/route_recommendations.py`
- Create: `backend/tests/test_route_templates.py`
- Modify: `backend/app/models/scenic_area.py`
- Modify: `backend/app/models/scenic_spot.py`
- Modify: `backend/app/models/__init__.py`
- Modify: `backend/app/main.py`

### Frontend

- Create: `admin-web/src/views/RouteTemplateView.vue`
- Create: `admin-web/src/tests/RouteTemplateView.test.ts`
- Modify: `admin-web/src/router/index.ts`
- Modify: `admin-web/src/components/AppSidebar.vue`

## Task 1: Backend Route Template CRUD

**Files:**
- Create: `backend/tests/test_route_templates.py`
- Create: `backend/app/models/route_template.py`
- Create: `backend/app/models/route_template_spot.py`
- Create: `backend/app/schemas/route_template.py`
- Create: `backend/app/repositories/route_template_repo.py`
- Create: `backend/app/services/route_template_service.py`
- Create: `backend/app/api/routers/route_templates.py`
- Modify: `backend/app/models/scenic_area.py`
- Modify: `backend/app/models/scenic_spot.py`
- Modify: `backend/app/models/__init__.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: Write the failing CRUD test**

```python
from fastapi.testclient import TestClient

from app.main import app


def test_route_template_crud_returns_nested_spots(test_db_session, auth_headers) -> None:
    client = TestClient(app)

    area_response = client.post(
        "/api/scenic-areas",
        headers=auth_headers,
        json={"code": "LS", "name": "灵山胜境", "description": "示范景区", "status": "active"},
    )
    scenic_area_id = area_response.json()["id"]

    spot_one = client.post(
        "/api/scenic-spots",
        headers=auth_headers,
        json={
            "scenic_area_id": scenic_area_id,
            "spot_code": "LS-001",
            "name": "灵山大佛",
            "alias": None,
            "location_text": "核心游览区",
            "open_status": "open",
            "tags": ["文化", "经典"],
        },
    ).json()
    spot_two = client.post(
        "/api/scenic-spots",
        headers=auth_headers,
        json={
            "scenic_area_id": scenic_area_id,
            "spot_code": "LS-002",
            "name": "梵宫",
            "alias": None,
            "location_text": "文化展示区",
            "open_status": "open",
            "tags": ["艺术"],
        },
    ).json()

    create_response = client.post(
        "/api/route-templates",
        headers=auth_headers,
        json={
            "scenic_area_id": scenic_area_id,
            "name": "经典半日游",
            "template_type": "fixed",
            "interest_tags": ["文化", "经典"],
            "audience_tags": ["亲子"],
            "duration_min_minutes": 180,
            "duration_max_minutes": 240,
            "summary": "覆盖核心文化景点的半日路线。",
            "status": "active",
            "priority": 10,
            "rule_notes": "优先给首次来访游客。",
            "spots": [
                {
                    "scenic_spot_id": spot_one["id"],
                    "sort_order": 1,
                    "stay_minutes": 90,
                    "highlight": "核心地标",
                },
                {
                    "scenic_spot_id": spot_two["id"],
                    "sort_order": 2,
                    "stay_minutes": 60,
                    "highlight": "建筑与演艺",
                },
            ],
        },
    )

    assert create_response.status_code == 201
    assert create_response.json()["spots"][0]["name"] == "灵山大佛"

    list_response = client.get("/api/route-templates", headers=auth_headers)
    assert list_response.status_code == 200
    assert list_response.json()["items"][0]["name"] == "经典半日游"

    template_id = create_response.json()["id"]
    update_response = client.put(
        f"/api/route-templates/{template_id}",
        headers=auth_headers,
        json={"priority": 20, "summary": "更新后的半日路线。"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["priority"] == 20

    delete_response = client.delete(f"/api/route-templates/{template_id}", headers=auth_headers)
    assert delete_response.status_code == 204
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend; .\.venv\Scripts\python -m pytest tests\test_route_templates.py::test_route_template_crud_returns_nested_spots -q`
Expected: FAIL with `404 Not Found` for `/api/route-templates` or import errors for the new route-template modules.

- [ ] **Step 3: Write minimal backend implementation**

```python
# backend/app/models/route_template.py
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class RouteTemplate(TimestampMixin, Base):
    __tablename__ = "route_template"

    id: Mapped[int] = mapped_column(primary_key=True)
    scenic_area_id: Mapped[int] = mapped_column(ForeignKey("scenic_area.id"), index=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    template_type: Mapped[str] = mapped_column(String(20), default="fixed")
    interest_tags_json: Mapped[str] = mapped_column(Text, default="[]")
    audience_tags_json: Mapped[str] = mapped_column(Text, default="[]")
    duration_min_minutes: Mapped[int] = mapped_column(Integer)
    duration_max_minutes: Mapped[int] = mapped_column(Integer)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active")
    priority: Mapped[int] = mapped_column(Integer, default=0)
    rule_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    scenic_area = relationship("ScenicArea", back_populates="route_templates")
    spots = relationship(
        "RouteTemplateSpot",
        back_populates="template",
        cascade="all, delete-orphan",
        order_by="RouteTemplateSpot.sort_order.asc()",
    )


# backend/app/models/route_template_spot.py
class RouteTemplateSpot(TimestampMixin, Base):
    __tablename__ = "route_template_spot"

    id: Mapped[int] = mapped_column(primary_key=True)
    template_id: Mapped[int] = mapped_column(ForeignKey("route_template.id"), index=True)
    scenic_spot_id: Mapped[int] = mapped_column(ForeignKey("scenic_spot.id"), index=True)
    sort_order: Mapped[int] = mapped_column(Integer)
    stay_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    highlight: Mapped[str | None] = mapped_column(Text, nullable=True)

    template = relationship("RouteTemplate", back_populates="spots")
    scenic_spot = relationship("ScenicSpot")


# backend/app/schemas/route_template.py
class RouteTemplateSpotWrite(BaseModel):
    scenic_spot_id: int
    sort_order: int
    stay_minutes: int | None = None
    highlight: str | None = None


class RouteTemplateCreate(BaseModel):
    scenic_area_id: int
    name: str
    template_type: str = "fixed"
    interest_tags: list[str] = []
    audience_tags: list[str] = []
    duration_min_minutes: int
    duration_max_minutes: int
    summary: str | None = None
    status: str = "active"
    priority: int = 0
    rule_notes: str | None = None
    spots: list[RouteTemplateSpotWrite] = []


class RouteTemplateUpdate(BaseModel):
    name: str | None = None
    template_type: str | None = None
    interest_tags: list[str] | None = None
    audience_tags: list[str] | None = None
    duration_min_minutes: int | None = None
    duration_max_minutes: int | None = None
    summary: str | None = None
    status: str | None = None
    priority: int | None = None
    rule_notes: str | None = None
    spots: list[RouteTemplateSpotWrite] | None = None


# backend/app/services/route_template_service.py
class RouteTemplateService:
    def create(self, payload: RouteTemplateCreate) -> dict:
        template = self.repo.create(**payload.model_dump())
        return self._to_read_dict(template)

    def list_all(self) -> list[dict]:
        return [self._to_read_dict(item) for item in self.repo.list_all()]

    def update(self, template_id: int, payload: RouteTemplateUpdate) -> dict:
        template = self.get(template_id)
        values = payload.model_dump(exclude_unset=True)
        updated = self.repo.update(template, **values)
        return self._to_read_dict(updated)


# backend/app/api/routers/route_templates.py
router = APIRouter(prefix="/route-templates", tags=["route-templates"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_template(payload: RouteTemplateCreate, _: object = Depends(require_authenticated_user), db: Session = Depends(get_db)):
    return RouteTemplateService(db).create(payload)


@router.get("")
def list_templates(_: object = Depends(require_authenticated_user), db: Session = Depends(get_db)):
    return {"items": RouteTemplateService(db).list_all()}
```

Implementation requirements inside this step:
- serialize `interest_tags_json` and `audience_tags_json` with `json.dumps(..., ensure_ascii=False)`
- deserialize them inside `_to_read_dict`
- include nested `spots` with `scenic_spot_id`, `name`, `sort_order`, `stay_minutes`, and `highlight`
- register reverse relationships in `ScenicArea` and `ScenicSpot`
- include the new routers in `backend/app/main.py`
- include `RouteTemplate` and `RouteTemplateSpot` in `backend/app/models/__init__.py`

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend; .\.venv\Scripts\python -m pytest tests\test_route_templates.py::test_route_template_crud_returns_nested_spots -q`
Expected: PASS with `1 passed`.

- [ ] **Step 5: Commit**

```bash
git add backend/app/models/route_template.py backend/app/models/route_template_spot.py backend/app/models/scenic_area.py backend/app/models/scenic_spot.py backend/app/models/__init__.py backend/app/schemas/route_template.py backend/app/repositories/route_template_repo.py backend/app/services/route_template_service.py backend/app/api/routers/route_templates.py backend/app/main.py backend/tests/test_route_templates.py
git commit -m "feat: add route template crud"
```

## Task 2: Backend Recommendation API

**Files:**
- Modify: `backend/tests/test_route_templates.py`
- Create: `backend/app/services/route_recommendation_service.py`
- Create: `backend/app/api/routers/route_recommendations.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: Write the failing recommendation tests**

```python
def test_generate_route_recommendation_exact_match(test_db_session, auth_headers) -> None:
    client = TestClient(app)
    scenic_area_id, spot_ids = _create_route_template_seed(client, auth_headers)

    response = client.post(
        "/api/route-recommendations/generate",
        headers=auth_headers,
        json={
            "scenic_area_id": scenic_area_id,
            "interest_tags": ["文化"],
            "duration_minutes": 210,
            "audience_tags": ["亲子"],
        },
    )

    assert response.status_code == 200
    assert response.json()["fallback_used"] is False
    assert response.json()["matched_template"]["name"] == "经典半日游"
    assert response.json()["spots"][0]["scenic_spot_id"] == spot_ids[0]


def test_generate_route_recommendation_falls_back_to_nearest_template(test_db_session, auth_headers) -> None:
    client = TestClient(app)
    scenic_area_id, _ = _create_route_template_seed(client, auth_headers)

    response = client.post(
        "/api/route-recommendations/generate",
        headers=auth_headers,
        json={
            "scenic_area_id": scenic_area_id,
            "interest_tags": ["禅修"],
            "duration_minutes": 320,
            "audience_tags": ["老人"],
        },
    )

    assert response.status_code == 200
    assert response.json()["fallback_used"] is True
    assert "duration" in response.json()["match_reason"]
    assert response.json()["matched_template"]["name"] == "经典半日游"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend; .\.venv\Scripts\python -m pytest tests\test_route_templates.py -q`
Expected: FAIL with `404 Not Found` for `/api/route-recommendations/generate`.

- [ ] **Step 3: Write minimal recommendation implementation**

```python
# backend/app/services/route_recommendation_service.py
class RouteRecommendationService:
    def generate(self, payload: RouteRecommendationRequest) -> dict:
        candidates = self.repo.list_active_by_area(payload.scenic_area_id)
        if not candidates:
            raise HTTPException(status_code=404, detail="No active route template found")

        ranked = sorted(
            (self._score_candidate(item, payload) for item in candidates),
            key=lambda result: (
                0 if result["exact_match"] else 1,
                result["duration_distance"],
                -result["interest_overlap"],
                -result["audience_overlap"],
                -result["priority"],
            ),
        )
        winner = ranked[0]
        template = winner["template"]
        return {
            "matched_template": {
                "id": template.id,
                "name": template.name,
                "template_type": template.template_type,
            },
            "fallback_used": not winner["exact_match"],
            "match_reason": self._build_match_reason(winner),
            "summary": template.summary,
            "spots": [
                {
                    "scenic_spot_id": spot.scenic_spot_id,
                    "name": spot.scenic_spot.name,
                    "stay_minutes": spot.stay_minutes,
                    "highlight": spot.highlight,
                }
                for spot in template.spots
            ],
        }


# backend/app/api/routers/route_recommendations.py
router = APIRouter(prefix="/route-recommendations", tags=["route-recommendations"])


@router.post("/generate")
def generate_recommendation(
    payload: RouteRecommendationRequest,
    _: object = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    return RouteRecommendationService(db).generate(payload)
```

Implementation requirements inside this step:
- add `RouteRecommendationRequest` schema with `scenic_area_id`, `interest_tags`, `duration_minutes`, `audience_tags`
- add `RouteRecommendationResponse` schema with `matched_template`, `fallback_used`, `match_reason`, `summary`, `spots`
- exact-match rule: duration in range and at least one overlapping interest tag when `interest_tags` is non-empty
- fallback rule: return the best-ranked active template even when exact match fails
- ranking order: duration exactness, interest overlap, audience overlap, priority
- keep output deterministic by ordering spots with `sort_order`

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend; .\.venv\Scripts\python -m pytest tests\test_route_templates.py -q`
Expected: PASS with `3 passed`.

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/route_recommendation_service.py backend/app/api/routers/route_recommendations.py backend/app/schemas/route_template.py backend/app/main.py backend/tests/test_route_templates.py
git commit -m "feat: add route recommendation api"
```

## Task 3: Admin Route Template Management View

**Files:**
- Create: `admin-web/src/views/RouteTemplateView.vue`
- Create: `admin-web/src/tests/RouteTemplateView.test.ts`
- Modify: `admin-web/src/router/index.ts`
- Modify: `admin-web/src/components/AppSidebar.vue`

- [ ] **Step 1: Write the failing render test**

```ts
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import RouteTemplateView from '../views/RouteTemplateView.vue'

vi.mock('../api/client', () => ({
  apiClient: {
    get: vi.fn(async (path: string) => {
      if (path === '/scenic-areas') {
        return { data: [{ id: 1, code: 'LS', name: '灵山胜境', description: null, status: 'active' }] }
      }
      if (path === '/scenic-spots') {
        return { data: { items: [{ id: 1, scenic_area_id: 1, spot_code: 'LS-001', name: '灵山大佛' }] } }
      }
      if (path === '/route-templates') {
        return { data: { items: [] } }
      }
      return { data: {} }
    }),
    post: vi.fn(async () => ({ data: { matched_template: null, fallback_used: false, match_reason: '', summary: '', spots: [] } })),
    put: vi.fn(async () => ({ data: {} })),
    delete: vi.fn(async () => ({ data: {} })),
  },
}))

describe('RouteTemplateView', () => {
  it('renders template management and preview areas', async () => {
    const wrapper = mount(RouteTemplateView)
    await Promise.resolve()

    expect(wrapper.text()).toContain('路线模板管理')
    expect(wrapper.text()).toContain('推荐预览')
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd admin-web; npm.cmd run test -- RouteTemplateView`
Expected: FAIL with `Failed to resolve import "../views/RouteTemplateView.vue"` or route-template view render errors.

- [ ] **Step 3: Write minimal frontend implementation**

```vue
<template>
  <section class="page-shell">
    <div class="route-template-grid">
      <form class="page-shell__panel page-shell__form" @submit.prevent="submitTemplate">
        <h2>{{ editingId ? '编辑路线模板' : '新增路线模板' }}</h2>
        <input v-model="form.name" placeholder="模板名称" type="text" />
        <select v-model="form.scenic_area_id">
          <option :value="0">请选择景区</option>
          <option v-for="item in scenicAreas" :key="item.id" :value="item.id">{{ item.name }}</option>
        </select>
        <input v-model="form.interest_tags_text" placeholder="兴趣标签，逗号分隔" type="text" />
        <input v-model="form.audience_tags_text" placeholder="人群标签，逗号分隔" type="text" />
        <button type="submit">{{ editingId ? '更新模板' : '创建模板' }}</button>
      </form>

      <section class="page-shell__panel">
        <h2>模板列表</h2>
        <ul class="page-shell__list">
          <li v-for="item in templates" :key="item.id">
            <div>
              <strong>{{ item.name }}</strong>
              <p>{{ item.summary || '未填写摘要' }}</p>
            </div>
            <button type="button" @click="startEdit(item)">编辑</button>
          </li>
        </ul>
      </section>
    </div>

    <section class="page-shell__panel">
      <h2>推荐预览</h2>
      <form class="route-preview-form" @submit.prevent="generatePreview">
        <input v-model="preview.interest_tags_text" placeholder="兴趣标签，逗号分隔" type="text" />
        <input v-model="preview.duration_minutes" placeholder="游玩时长（分钟）" type="number" />
        <button type="submit">生成推荐路线</button>
      </form>
      <p>{{ previewResult.match_reason || '提交条件后查看推荐结果。' }}</p>
    </section>
  </section>
</template>
```

Implementation requirements inside this step:
- load scenic areas, scenic spots, and templates on mount
- allow adding/removing ordered route spots in the form payload
- reuse the same `/route-recommendations/generate` backend contract for preview
- add route metadata to `admin-web/src/router/index.ts` at path `/route-templates`
- add a sidebar entry labeled `路线模板`

- [ ] **Step 4: Run test to verify it passes**

Run: `cd admin-web; npm.cmd run test -- RouteTemplateView`
Expected: PASS with `1 passed`.

- [ ] **Step 5: Commit**

```bash
git add admin-web/src/views/RouteTemplateView.vue admin-web/src/tests/RouteTemplateView.test.ts admin-web/src/router/index.ts admin-web/src/components/AppSidebar.vue
git commit -m "feat: add route template admin view"
```

## Task 4: Slice Verification

**Files:**
- Modify: `backend/tests/test_route_templates.py`
- Modify: `admin-web/src/views/RouteTemplateView.vue`
- Modify: `backend/app/schemas/route_template.py`

- [ ] **Step 1: Run backend test suite**

Run: `cd backend; .\.venv\Scripts\python -m pytest tests -q`
Expected: PASS with existing suites plus the new route-template tests.

- [ ] **Step 2: Run frontend test suite**

Run: `cd admin-web; npm.cmd run test`
Expected: PASS with the existing render tests plus `RouteTemplateView.test.ts`.

- [ ] **Step 3: Run frontend production build**

Run: `cd admin-web; npm.cmd run build`
Expected: PASS and emit the Vite production bundle.

- [ ] **Step 4: Apply the minimal verification polish**

```python
class RouteTemplateSpotRead(BaseModel):
    scenic_spot_id: int
    name: str
    sort_order: int
    stay_minutes: int | None = None
    highlight: str | None = None
```

```ts
const durationMinutes = Number(preview.duration_minutes || 0)
```

Apply this step only as narrowly as needed:
- keep response schemas aligned with the final backend payload
- normalize numeric inputs before preview submission
- do not expand the feature scope during verification

- [ ] **Step 5: Commit**

```bash
git add backend/tests/test_route_templates.py admin-web/src/views/RouteTemplateView.vue admin-web/src/tests/RouteTemplateView.test.ts
git commit -m "test: verify route template slice"
```

## Self-Review

- Spec coverage: Task 1 covers route-template data model and CRUD with nested spots. Task 2 covers exact match, fallback, and future-facing recommendation API payload/response. Task 3 covers the admin management page, ordered spot editor entry point, and recommendation preview. Task 4 covers full-slice verification required by the spec.
- Placeholder scan: this plan avoids open-ended placeholders and repeated "same as above" shortcuts; every task has explicit files, commands, and code examples.
- Type consistency: the plan consistently uses `interest_tags`, `audience_tags`, `duration_minutes`, `matched_template`, and nested `spots` across backend tests, schemas, service logic, and frontend preview payloads.
