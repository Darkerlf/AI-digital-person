# DH_live Voice Input Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the conflicting scenic stage backdrop with a pale jade stage and add WeChat-style press-to-talk voice input that fills the text field after ASR.

**Architecture:** Add a focused browser WAV recorder module and extend the existing backend client with multipart ASR upload. Keep gesture state in `app.mjs`, preserve the existing answer submission flow, and reuse the existing FastAPI `/tourist/voice/asr` endpoint.

**Tech Stack:** Browser Web Audio API, ES modules, Node test runner, FastAPI, DashScope Paraformer.

---

### Task 1: Lock The Visual And Upload Contracts

**Files:**
- Modify: `prototypes/dh-live-guide/tests/mobileLayoutContract.test.mjs`
- Modify: `prototypes/dh-live-guide/tests/stageFirstLayout.test.mjs`
- Create: `prototypes/dh-live-guide/tests/voiceRecorder.test.mjs`
- Modify: `prototypes/dh-live-guide/tests/backendClient.test.mjs`

- [ ] Add assertions for the pale jade stage, microphone controls, WAV encoding and multipart ASR upload.
- [ ] Run `npm.cmd test` and confirm the new assertions fail for the missing implementation.

### Task 2: Implement WAV Recording And ASR Upload

**Files:**
- Create: `prototypes/dh-live-guide/src/voiceRecorder.mjs`
- Modify: `prototypes/dh-live-guide/src/backendClient.mjs`

- [ ] Encode captured PCM as 16 kHz mono 16-bit WAV.
- [ ] Add `recognizeAudio(blob, signal)` and upload `voice.wav` with `FormData`.
- [ ] Run `npm.cmd test` and confirm WAV and client tests pass.

### Task 3: Implement WeChat-Style Voice Interaction

**Files:**
- Modify: `prototypes/dh-live-guide/runtime/index.html`
- Modify: `prototypes/dh-live-guide/shell/index.html`
- Modify: `prototypes/dh-live-guide/src/app.mjs`
- Modify: `prototypes/dh-live-guide/src/styles.css`

- [ ] Remove the scenic stage background image.
- [ ] Add microphone, keyboard and hold-to-talk controls.
- [ ] Add press, release and upward-cancel gesture handling.
- [ ] Fill recognized text into the text input without submitting.
- [ ] Change the right submit label to “输入”.

### Task 4: Verify

**Files:**
- Verify: `prototypes/dh-live-guide`
- Verify: `backend/tests/test_tourist_voice_api.py`

- [ ] Run `npm.cmd test`.
- [ ] Run the focused backend ASR API tests.
- [ ] Capture a 390x844 Playwright screenshot and inspect the stage and input layout.
