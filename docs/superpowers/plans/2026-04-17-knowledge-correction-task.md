# Knowledge Correction Task Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a traceable knowledge-correction loop so unresolved session questions become correction tasks that can be completed through FAQ or knowledge-document creation.

**Architecture:** Add a dedicated correction-task model and API layer in the backend, then thread task context through the existing session, FAQ, and knowledge-document views. Keep the loop explicit and narrow: one source message creates one active task, one task links one result, and task resolution updates the original conversation message state.

**Tech Stack:** Python 3.13, FastAPI, SQLAlchemy 2, Pydantic 2, pytest, Vue 3, TypeScript, Vue Router, Axios, Vitest, Vite.

---

## File Structure

### Backend

- Create: `backend/app/models/knowledge_correction_task.py`
- Create: `backend/app/schemas/knowledge_correction.py`
- Create: `backend/app/repositories/knowledge_correction_repo.py`
- Create: `backend/app/services/knowledge_correction_service.py`
- Create: `backend/app/api/routers/knowledge_correction_tasks.py`
- Modify: `backend/app/models/__init__.py`
- Modify: `backend/app/models/conversation_message.py`
- Modify: `backend/app/repositories/conversation_repo.py`
- Modify: `backend/app/repositories/knowledge_repo.py`
- Modify: `backend/app/services/conversation_service.py`
- Modify: `backend/app/services/knowledge_service.py`
- Modify: `backend/app/api/routers/faqs.py`
- Modify: `backend/app/api/routers/knowledge_documents.py`
- Modify: `backend/app/main.py`
- Modify: `backend/tests/test_sessions.py`
- Modify: `backend/tests/test_knowledge.py`
- Create: `backend/tests/test_knowledge_correction_tasks.py`

### Frontend

- Create: `admin-web/src/views/KnowledgeCorrectionTaskView.vue`
- Create: `admin-web/src/tests/KnowledgeCorrectionTaskView.test.ts`
- Modify: `admin-web/src/views/SessionManagementView.vue`
- Modify: `admin-web/src/views/FaqView.vue`
- Modify: `admin-web/src/views/KnowledgeDocumentView.vue`
- Modify: `admin-web/src/router/index.ts`
- Modify: `admin-web/src/components/AppSidebar.vue`
- Modify: `admin-web/src/tests/SessionManagementView.test.ts`

## Task 1: Backend Correction Task Core

**Files:**
- Create: `backend/tests/test_knowledge_correction_tasks.py`
- Create: `backend/app/models/knowledge_correction_task.py`
- Create: `backend/app/schemas/knowledge_correction.py`
- Create: `backend/app/repositories/knowledge_correction_repo.py`
- Create: `backend/app/services/knowledge_correction_service.py`
- Create: `backend/app/api/routers/knowledge_correction_tasks.py`
- Modify: `backend/app/models/__init__.py`
- Modify: `backend/app/models/conversation_message.py`
- Modify: `backend/app/repositories/conversation_repo.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: Write the failing correction-task tests**

```python
from fastapi.testclient import TestClient

from app.main import app
from app.models.conversation_message import ConversationMessage
from app.models.conversation_session import ConversationSession


def test_create_faq_correction_task_from_unresolved_message(test_db_session, content_auth_headers) -> None:
    conversation = ConversationSession(
        scenic_area_id=None,
        session_key="session-001",
        channel="miniprogram",
        visitor_id="visitor-001",
        status="completed",
    )
    test_db_session.add(conversation)
    test_db_session.commit()
    test_db_session.refresh(conversation)

    message = ConversationMessage(
        session_id=conversation.id,
        question_text="景区半日游路线怎么安排？",
        recognized_text="景区半日游路线怎么安排",
        answer_text="暂时没有找到合适路线。",
        matched_document_title=None,
        latency_ms=2100,
        feedback_status="disliked",
        is_missed=True,
        resolution_status="pending",
        resolution_note=None,
    )
    test_db_session.add(message)
    test_db_session.commit()
    test_db_session.refresh(message)

    client = TestClient(app)
    response = client.post(
        "/api/knowledge/correction-tasks",
        headers=content_auth_headers,
        json={
            "source_message_id": message.id,
            "correction_type": "faq",
            "resolution_note": "需要补 FAQ。",
        },
    )

    assert response.status_code == 201
    assert response.json()["status"] == "open"
    assert response.json()["question_text"] == "景区半日游路线怎么安排？"


def test_reject_duplicate_open_correction_task_for_same_message(test_db_session, content_auth_headers) -> None:
    client = TestClient(app)
    task_payload = {"source_message_id": 1, "correction_type": "faq", "resolution_note": "第一次创建"}

    first = client.post("/api/knowledge/correction-tasks", headers=content_auth_headers, json=task_payload)
    second = client.post("/api/knowledge/correction-tasks", headers=content_auth_headers, json=task_payload)

    assert first.status_code == 201
    assert second.status_code == 409
```

- [ ] **Step 2: Run the correction-task tests to verify they fail**

Run: `cd backend; .\.venv\Scripts\python -m pytest tests\test_knowledge_correction_tasks.py -q`
Expected: FAIL with missing model/router/import errors or `404 Not Found` for `/api/knowledge/correction-tasks`.

- [ ] **Step 3: Write the minimal correction-task implementation**

```python
# backend/app/models/knowledge_correction_task.py
class KnowledgeCorrectionTask(TimestampMixin, Base):
    __tablename__ = "knowledge_correction_task"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_message_id: Mapped[int] = mapped_column(ForeignKey("conversation_message.id"), index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("conversation_session.id"), index=True)
    scenic_area_id: Mapped[int | None] = mapped_column(ForeignKey("scenic_area.id"), nullable=True, index=True)
    question_text: Mapped[str] = mapped_column(Text)
    recognized_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    feedback_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    correction_type: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="open")
    resolution_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    linked_faq_id: Mapped[int | None] = mapped_column(ForeignKey("faq_item.id"), nullable=True)
    linked_document_id: Mapped[int | None] = mapped_column(ForeignKey("knowledge_document.id"), nullable=True)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("admin_user.id"), nullable=True)
    resolved_by: Mapped[int | None] = mapped_column(ForeignKey("admin_user.id"), nullable=True)


# backend/app/services/knowledge_correction_service.py
class KnowledgeCorrectionService:
    def create_task(self, payload: KnowledgeCorrectionTaskCreate, current_user) -> dict:
        message = self.conversation_repo.get_message(payload.source_message_id)
        if message is None:
            raise HTTPException(status_code=404, detail="Conversation message not found")
        if self.repo.get_open_by_source_message_id(payload.source_message_id) is not None:
            raise HTTPException(status_code=409, detail="Correction task already exists")
        task = self.repo.create_from_message(message=message, payload=payload, created_by=current_user.id)
        return self._to_read_dict(task)
```

Implementation requirements inside this step:
- add `correction_task_id` to `ConversationMessage` as nullable foreign-key-like integer only if needed for easy lookup; otherwise keep task lookup by `source_message_id`
- include task summary in unresolved-message list output so the session page can show existing task status
- register the new router under `/api/knowledge/correction-tasks`
- keep the slice limited to `open` and `resolved` statuses

- [ ] **Step 4: Run the correction-task tests to verify they pass**

Run: `cd backend; .\.venv\Scripts\python -m pytest tests\test_knowledge_correction_tasks.py -q`
Expected: PASS with the create and duplicate-protection tests green.

- [ ] **Step 5: Commit**

```bash
git add backend/app/models/knowledge_correction_task.py backend/app/schemas/knowledge_correction.py backend/app/repositories/knowledge_correction_repo.py backend/app/services/knowledge_correction_service.py backend/app/api/routers/knowledge_correction_tasks.py backend/app/models/__init__.py backend/app/models/conversation_message.py backend/app/repositories/conversation_repo.py backend/app/main.py backend/tests/test_knowledge_correction_tasks.py
git commit -m "feat: add knowledge correction task core"
```

## Task 2: Backend Link And Resolve Flow

**Files:**
- Modify: `backend/tests/test_knowledge_correction_tasks.py`
- Modify: `backend/tests/test_sessions.py`
- Modify: `backend/tests/test_knowledge.py`
- Modify: `backend/app/repositories/knowledge_repo.py`
- Modify: `backend/app/services/conversation_service.py`
- Modify: `backend/app/services/knowledge_service.py`
- Modify: `backend/app/api/routers/faqs.py`
- Modify: `backend/app/api/routers/knowledge_documents.py`

- [ ] **Step 1: Write the failing link-and-resolve tests**

```python
def test_link_faq_and_resolve_correction_task(test_db_session, content_auth_headers) -> None:
    client = TestClient(app)
    scenic_area_id, task_id = create_open_correction_task_seed(test_db_session, client, content_auth_headers, "faq")

    faq_response = client.post(
        "/api/knowledge/faqs",
        headers=content_auth_headers,
        json={
            "scenic_area_id": scenic_area_id,
            "question": "景区半日游路线怎么安排？",
            "answer": "建议先游览核心景点，再安排文化体验。",
            "category": "路线",
            "priority": 10,
            "status": "active",
            "source": "correction-task",
        },
        params={"correction_task_id": task_id},
    )

    assert faq_response.status_code == 201

    detail_response = client.get(f"/api/knowledge/correction-tasks/{task_id}", headers=content_auth_headers)
    assert detail_response.json()["linked_faq_id"] == faq_response.json()["id"]
    assert detail_response.json()["status"] == "resolved"


def test_link_document_and_resolve_updates_message_state(test_db_session, content_auth_headers) -> None:
    client = TestClient(app)
    scenic_area_id, task_id, message_id = create_open_document_task_seed(test_db_session, client, content_auth_headers)

    document_response = client.post(
        "/api/knowledge/documents/upload",
        headers=content_auth_headers,
        json={
            "scenic_area_id": scenic_area_id,
            "title": "景区半日游路线说明",
            "doc_type": "markdown",
            "source_name": "manual-entry",
            "content_text": "推荐路线：先核心景点，后体验项目。",
        },
        params={"correction_task_id": task_id},
    )

    assert document_response.status_code == 201

    detail = client.get(f"/api/knowledge/correction-tasks/{task_id}", headers=content_auth_headers)
    assert detail.json()["linked_document_id"] == document_response.json()["id"]
    assert detail.json()["status"] == "resolved"

    unresolved = client.get("/api/sessions/unresolved", headers=content_auth_headers)
    assert all(item["id"] != message_id for item in unresolved.json()["items"])
```

- [ ] **Step 2: Run the backend link-and-resolve tests to verify they fail**

Run: `cd backend; .\.venv\Scripts\python -m pytest tests\test_knowledge_correction_tasks.py tests\test_sessions.py tests\test_knowledge.py -q`
Expected: FAIL because FAQ and document creation do not yet accept `correction_task_id` or resolve tasks.

- [ ] **Step 3: Write the minimal link-and-resolve implementation**

```python
# backend/app/api/routers/faqs.py
@router.post("", status_code=status.HTTP_201_CREATED)
def create_faq(
    payload: FAQCreate,
    correction_task_id: int | None = None,
    current_user=Depends(require_content_roles),
    db: Session = Depends(get_db),
):
    return KnowledgeService(db).create_faq(payload, correction_task_id=correction_task_id, current_user=current_user)


# backend/app/services/knowledge_service.py
def create_faq(self, payload: FAQCreate, correction_task_id: int | None = None, current_user=None):
    faq = self.repo.create_faq(**payload.model_dump())
    if correction_task_id is not None:
        KnowledgeCorrectionService(self.db).link_faq_and_resolve(
            correction_task_id=correction_task_id,
            faq_id=faq.id,
            current_user=current_user,
        )
    return faq
```

Implementation requirements inside this step:
- accept `correction_task_id` as optional query parameter on FAQ and document creation routes
- auto-link and auto-resolve the task after successful FAQ or document creation
- when a task resolves, update `ConversationMessage.resolution_status = "resolved"` and preserve/update `resolution_note`
- keep duplicate task creation blocked even after link logic lands

- [ ] **Step 4: Run the backend link-and-resolve tests to verify they pass**

Run: `cd backend; .\.venv\Scripts\python -m pytest tests\test_knowledge_correction_tasks.py tests\test_sessions.py tests\test_knowledge.py -q`
Expected: PASS with task linking and message resolution green.

- [ ] **Step 5: Commit**

```bash
git add backend/app/repositories/knowledge_repo.py backend/app/services/conversation_service.py backend/app/services/knowledge_service.py backend/app/api/routers/faqs.py backend/app/api/routers/knowledge_documents.py backend/tests/test_knowledge_correction_tasks.py backend/tests/test_sessions.py backend/tests/test_knowledge.py
git commit -m "feat: link correction tasks to knowledge updates"
```

## Task 3: Session Page And Correction Task View

**Files:**
- Modify: `admin-web/src/views/SessionManagementView.vue`
- Create: `admin-web/src/views/KnowledgeCorrectionTaskView.vue`
- Modify: `admin-web/src/router/index.ts`
- Modify: `admin-web/src/components/AppSidebar.vue`
- Modify: `admin-web/src/tests/SessionManagementView.test.ts`
- Create: `admin-web/src/tests/KnowledgeCorrectionTaskView.test.ts`

- [ ] **Step 1: Write the failing frontend task-entry tests**

```ts
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import SessionManagementView from '../views/SessionManagementView.vue'

vi.mock('../api/client', () => ({
  apiClient: {
    get: vi.fn(async (path: string) => {
      if (path === '/sessions') return { data: { items: [] } }
      if (path === '/sessions/unresolved') {
        return {
          data: {
            items: [
              {
                id: 11,
                session_id: 1,
                session_key: 'session-001',
                question_text: '景区半日游路线怎么安排？',
                recognized_text: '景区半日游路线怎么安排',
                feedback_status: 'disliked',
                resolution_status: 'pending',
                correction_task: null,
              },
            ],
          },
        }
      }
      return { data: { id: 1, session_key: 'session-001', messages: [] } }
    }),
    post: vi.fn(async () => ({ data: { id: 9, correction_type: 'faq', status: 'open' } })),
  },
}))

it('renders create correction task actions', async () => {
  const wrapper = mount(SessionManagementView, { global: { stubs: { RouterLink: { template: '<a><slot /></a>' } } } })
  await Promise.resolve()
  await Promise.resolve()
  expect(wrapper.text()).toContain('创建 FAQ 修正任务')
  expect(wrapper.text()).toContain('创建文档修正任务')
})
```

- [ ] **Step 2: Run the frontend task-entry tests to verify they fail**

Run: `cd admin-web; npm.cmd run test -- SessionManagementView KnowledgeCorrectionTaskView`
Expected: FAIL because the current session page still shows a generic resolve textarea/button and there is no task view yet.

- [ ] **Step 3: Write the minimal session/task-view implementation**

```vue
<!-- admin-web/src/views/SessionManagementView.vue -->
<button type="button" @click="createCorrectionTask(item, 'faq')">创建 FAQ 修正任务</button>
<button type="button" @click="createCorrectionTask(item, 'document')">创建文档修正任务</button>
<RouterLink v-if="item.correction_task" :to="buildContinueLink(item)">继续处理</RouterLink>
```

```vue
<!-- admin-web/src/views/KnowledgeCorrectionTaskView.vue -->
<template>
  <section class="page-shell">
    <section class="page-shell__panel">
      <h2>知识修正任务</h2>
      <ul class="page-shell__list">
        <li v-for="item in tasks" :key="item.id">
          <div>
            <strong>{{ item.question_text }}</strong>
            <p>{{ item.correction_type }} · {{ item.status }}</p>
          </div>
        </li>
      </ul>
    </section>
  </section>
</template>
```

Implementation requirements inside this step:
- load correction-task summaries into the unresolved-message list payload
- create task via `POST /knowledge/correction-tasks`
- add a new route such as `/knowledge/correction-tasks`
- add a sidebar entry under the content-admin knowledge area
- show linked result summary and current status in the task list view

- [ ] **Step 4: Run the frontend task-entry tests to verify they pass**

Run: `cd admin-web; npm.cmd run test -- SessionManagementView KnowledgeCorrectionTaskView`
Expected: PASS with the new task entry actions and task list view rendered.

- [ ] **Step 5: Commit**

```bash
git add admin-web/src/views/SessionManagementView.vue admin-web/src/views/KnowledgeCorrectionTaskView.vue admin-web/src/router/index.ts admin-web/src/components/AppSidebar.vue admin-web/src/tests/SessionManagementView.test.ts admin-web/src/tests/KnowledgeCorrectionTaskView.test.ts
git commit -m "feat: add correction task session workflow"
```

## Task 4: FAQ And Document Prefill Flow

**Files:**
- Modify: `admin-web/src/views/FaqView.vue`
- Modify: `admin-web/src/views/KnowledgeDocumentView.vue`
- Create: `admin-web/src/tests/FaqView.test.ts`
- Create: `admin-web/src/tests/KnowledgeDocumentView.test.ts`

- [ ] **Step 1: Write the failing prefill/link tests**

```ts
it('prefills FAQ form from correction-task query params', async () => {
  const route = { query: { taskId: '9', question: '景区半日游路线怎么安排？', scenicAreaId: '1' } }
  const wrapper = mount(FaqView, { global: { mocks: { $route: route } } })
  await Promise.resolve()
  expect(wrapper.find('input[placeholder=\"问题\"]').element.value).toContain('景区半日游路线怎么安排？')
})
```

```ts
it('submits correction_task_id when creating a knowledge document', async () => {
  // mount view with query taskId=9 and assert post call contains correction_task_id query parameter
})
```

- [ ] **Step 2: Run the prefill/link tests to verify they fail**

Run: `cd admin-web; npm.cmd run test -- FaqView KnowledgeDocumentView`
Expected: FAIL because the current views do not read route query or send `correction_task_id`.

- [ ] **Step 3: Write the minimal prefill/link implementation**

```ts
// admin-web/src/views/FaqView.vue
const route = useRoute()
onMounted(() => {
  if (typeof route.query.question === 'string') form.question = route.query.question
  if (typeof route.query.scenicAreaId === 'string') form.scenic_area_id = route.query.scenicAreaId
})

await apiClient.post(`/knowledge/faqs${buildTaskQuery(route.query.taskId)}`, payload)
```

```ts
// admin-web/src/views/KnowledgeDocumentView.vue
onMounted(() => {
  if (typeof route.query.question === 'string' && !form.title) form.title = route.query.question
  if (typeof route.query.recognizedText === 'string' && !form.content_text) form.content_text = route.query.recognizedText
})
```

Implementation requirements inside this step:
- use `useRoute()` in both views
- keep normal creation flow unchanged when no task query is present
- send `correction_task_id` only when a task context exists
- do not add a separate modal; reuse the current form pages

- [ ] **Step 4: Run the prefill/link tests to verify they pass**

Run: `cd admin-web; npm.cmd run test -- FaqView KnowledgeDocumentView`
Expected: PASS with query-prefill and task-link submissions working.

- [ ] **Step 5: Commit**

```bash
git add admin-web/src/views/FaqView.vue admin-web/src/views/KnowledgeDocumentView.vue admin-web/src/tests/FaqView.test.ts admin-web/src/tests/KnowledgeDocumentView.test.ts
git commit -m "feat: prefill knowledge edits from correction tasks"
```

## Task 5: Full Verification

**Files:**
- Modify: `backend/tests/test_knowledge_correction_tasks.py`
- Modify: `admin-web/src/tests/KnowledgeCorrectionTaskView.test.ts`
- Modify: `admin-web/src/tests/FaqView.test.ts`
- Modify: `admin-web/src/tests/KnowledgeDocumentView.test.ts`

- [ ] **Step 1: Run the full backend test suite**

Run: `cd backend; .\.venv\Scripts\python -m pytest tests -q`
Expected: PASS with session, knowledge, and correction-task suites green.

- [ ] **Step 2: Run the full frontend test suite**

Run: `cd admin-web; npm.cmd run test`
Expected: PASS with session, FAQ, knowledge-document, and correction-task tests green.

- [ ] **Step 3: Run the frontend build**

Run: `cd admin-web; npm.cmd run build`
Expected: PASS and emit the production bundle.

- [ ] **Step 4: Apply the narrow verification polish**

```python
assert detail_response.json()["linked_document_id"] == document_response.json()["id"]
```

```ts
expect(wrapper.text()).toContain('resolved')
```

Apply this step only as narrowly as needed:
- keep one-task-one-result semantics intact
- keep task status transitions limited to `open` and `resolved`
- do not expand into assignee, comment, or priority features

- [ ] **Step 5: Commit**

```bash
git add backend/tests/test_knowledge_correction_tasks.py admin-web/src/tests/KnowledgeCorrectionTaskView.test.ts admin-web/src/tests/FaqView.test.ts admin-web/src/tests/KnowledgeDocumentView.test.ts
git commit -m "test: verify knowledge correction task slice"
```

## Self-Review

- Spec coverage: Task 1 covers the task model, task creation, duplicate prevention, and API registration. Task 2 covers FAQ/document linking and resolution back into conversation-message state. Task 3 covers session-page task creation plus the dedicated task list view. Task 4 covers FAQ/document query-prefill and link flow. Task 5 covers full-slice verification.
- Placeholder scan: this plan avoids open-ended stubs and includes explicit file paths, commands, and code snippets for each task.
- Type consistency: the plan consistently uses `correction_type`, `linked_faq_id`, `linked_document_id`, `status`, and `correction_task_id` across backend tests, backend services, frontend queries, and task-list rendering.
