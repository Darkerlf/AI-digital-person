# Visitor Avatar OSS Upload Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Persist mini-program visitor avatars as stable OSS URLs instead of expired WeChat temporary paths.

**Architecture:** Add one authenticated multipart avatar endpoint to the visitor router and reuse the existing `ObjectStorage.upload_bytes` OSS abstraction. The mini-program keeps a selected temporary path only for preview, uploads it before profile submission, and stores only the returned OSS URL.

**Tech Stack:** FastAPI, SQLAlchemy, Aliyun OSS `oss2`, uni-app Vue 3, Node contract tests, pytest.

---

### Task 1: Add Avatar Upload API Tests

**Files:**
- Modify: `backend/tests/test_visitor_auth.py`

- [ ] Add tests for authenticated OSS upload, invalid MIME type, oversize payload, disabled OSS and missing authentication.
- [ ] Run `python -m pytest tests/test_visitor_auth.py -q` and verify the new tests fail because the route is missing.

### Task 2: Implement Strict OSS Avatar Upload

**Files:**
- Modify: `backend/app/api/routers/visitor_auth.py`
- Modify: `backend/app/services/visitor_service.py`

- [ ] Add `POST /api/tourist/profile/avatar`.
- [ ] Validate MIME type and a 2 MiB limit before uploading.
- [ ] Upload with `get_object_storage().upload_bytes(..., prefix="visitor-avatars")`.
- [ ] Persist only the returned OSS URL through `VisitorService.update_profile`.
- [ ] Convert unavailable OSS and upload exceptions into HTTP `503`.
- [ ] Run `python -m pytest tests/test_visitor_auth.py -q`.

### Task 3: Add Mini-Program Avatar Upload Contract

**Files:**
- Create: `miniprogram/tests/avatarUpload.test.mjs`
- Modify: `miniprogram/src/api/tourist.ts`
- Modify: `miniprogram/src/stores/auth.ts`
- Modify: `miniprogram/src/pages/my/my.vue`

- [ ] Add a contract test requiring `uni.uploadFile`, `/tourist/profile/avatar`, a Bearer token and selected-avatar upload before profile save.
- [ ] Run `node tests/avatarUpload.test.mjs` and verify it fails.
- [ ] Implement `uploadAvatar`, store integration and page preview state.
- [ ] Run the mini-program script tests.

### Task 4: Clean Historical Temporary Avatar URLs

**Files:**
- Create: `backend/scripts/clear_temporary_visitor_avatars.py`

- [ ] Add a narrowly scoped cleanup script.
- [ ] Run the script against the configured database.
- [ ] Verify no matching temporary avatar URL remains.

### Task 5: Verify the Integrated Change

- [ ] Run `python -m pytest tests/test_visitor_auth.py tests/test_object_storage.py -q`.
- [ ] Run all mini-program Node script checks.
- [ ] Run `npm.cmd run build:mp-weixin`.
- [ ] Verify backend health and document the required OSS environment variables.
