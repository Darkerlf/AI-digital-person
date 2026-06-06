# AI Guide Feedback Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the DH_live AI guide page to match the approved immersive layout and connect per-answer visitor feedback to the admin report.

**Architecture:** Reuse the existing `feedback_record` table and bind feedback to `conversation_message.id` through `source_id`. Extend the stream metadata so the DH_live page receives that message id, submit feedback from the WebView, and expose recent feedback details through the existing dashboard report endpoint.

**Tech Stack:** FastAPI, SQLAlchemy, Pydantic, Vue 3, plain HTML/CSS/ES modules, Node test runner, Vitest, pytest.

---

### Task 1: Bind streaming answers to feedback

**Files:**
- Modify: `backend/app/services/chat_service.py`
- Modify: `backend/app/api/routers/tourist_chat.py`
- Modify: `backend/app/schemas/chat.py`
- Test: `backend/tests/test_tourist_flow_api.py`

- [ ] Add a failing API test that submits feedback for a streamed `message_id` and checks `conversation_message.feedback_status`.
- [ ] Run the focused pytest and confirm the missing stream metadata or status update causes failure.
- [ ] Return `message_id` in stream metadata, validate feedback input, and update the bound message.
- [ ] Run the focused pytest and confirm it passes.

### Task 2: Expose feedback details to administrators

**Files:**
- Modify: `backend/app/schemas/dashboard.py`
- Modify: `backend/app/services/dashboard_service.py`
- Test: `backend/tests/test_feedback_report.py`

- [ ] Add a failing report test for recent feedback details.
- [ ] Run the focused pytest and confirm the missing `latest_feedback` field causes failure.
- [ ] Add the feedback detail schema and report mapping.
- [ ] Run the focused pytest and confirm it passes.

### Task 3: Add DH_live feedback transport

**Files:**
- Modify: `prototypes/dh-live-guide/src/backendClient.mjs`
- Test: `prototypes/dh-live-guide/tests/backendClient.test.mjs`

- [ ] Add failing Node tests for stream metadata callbacks and feedback submission.
- [ ] Run the prototype test suite and confirm the new tests fail.
- [ ] Parse `__meta__` frames and add `submitFeedback`.
- [ ] Run the prototype test suite and confirm the transport tests pass.

### Task 4: Rebuild the dynamic guide page

**Files:**
- Modify: `prototypes/dh-live-guide/shell/index.html`
- Modify: `prototypes/dh-live-guide/runtime/index.html`
- Modify: `prototypes/dh-live-guide/src/styles.css`
- Modify: `prototypes/dh-live-guide/src/app.mjs`
- Modify: `prototypes/dh-live-guide/tests/stageFirstLayout.test.mjs`
- Modify: `prototypes/dh-live-guide/tests/mobileLayoutContract.test.mjs`

- [ ] Add failing layout assertions for the stage controls, top-right status, answer feedback actions, and half-sheet modal.
- [ ] Run the prototype test suite and confirm layout tests fail.
- [ ] Implement the approved stage-first layout, feedback actions, modal, and submission states.
- [ ] Copy the shell HTML into runtime HTML.
- [ ] Run the prototype test suite and confirm all tests pass.

### Task 5: Show detailed feedback in the admin report

**Files:**
- Modify: `admin-web/src/views/FeedbackReportView.vue`
- Modify: `admin-web/src/tests/FeedbackReportView.test.ts`

- [ ] Add a failing component test for the detailed feedback table.
- [ ] Run the focused Vitest and confirm it fails.
- [ ] Render the latest feedback list with sentiment, score, comment, question, and answer excerpt.
- [ ] Run the admin test suite and confirm it passes.

### Task 6: Verify the integrated experience

**Files:**
- Verify: `backend/tests`
- Verify: `prototypes/dh-live-guide`
- Verify: `admin-web`
- Verify: `miniprogram`

- [ ] Run focused backend tests and then the backend suite.
- [ ] Run DH_live Node tests.
- [ ] Run admin Vitest and admin production build.
- [ ] Run the miniprogram WeChat build.
- [ ] Open the local DH_live page and capture a mobile screenshot for visual review.

