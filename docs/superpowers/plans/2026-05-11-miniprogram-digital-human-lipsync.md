# Mini Program Digital Human Lip Sync Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build local and production-ready WeChat mini program digital human lip sync using the existing split PNG avatar assets and Alibaba Cloud qwen3 TTS.

**Architecture:** FastAPI owns TTS synthesis and cue generation. The mini program owns playback and image-layer rendering, using the returned cue timeline to switch mouth PNGs while audio plays.

**Tech Stack:** FastAPI, OpenAI-compatible DashScope client, pytest, uni-app Vue 3, WeChat `InnerAudioContext`, PNG layered assets.

---

### Task 1: Backend TTS Sync Contract

**Files:**
- Modify: `backend/tests/test_tts_service.py`
- Modify: `backend/app/services/tts_service.py`
- Modify: `backend/app/api/routers/tourist_voice.py`

- [x] Add failing tests for mouth cue generation and TTS sync response shape.
- [x] Run `python -m pytest tests/test_tts_service.py tests/test_tourist_voice_api.py -q` and confirm the new tests fail before implementation.
- [x] Implement `MouthCue`, `TTSSyncResult`, duration estimation, and text-to-mouth cue generation.
- [x] Add `/tts-sync` and `/tts/audio/{filename}` endpoints.
- [x] Re-run backend voice tests and confirm they pass.

### Task 2: Mini Program Asset Layer

**Files:**
- Create: `miniprogram/src/static/digital-human/*`
- Modify: `miniprogram/src/components/DigitalHuman.vue`

- [x] Copy split avatar PNG files and `config.json` into mini program static assets.
- [x] Replace the CSS-drawn placeholder avatar with layered PNG rendering.
- [x] Add `mouth` and `expression` props and internal blink animation.

### Task 3: Mini Program Playback Integration

**Files:**
- Modify: `miniprogram/src/utils/sse.ts`
- Modify: `miniprogram/src/utils/player.ts`
- Modify: `miniprogram/src/pages/guide/guide.vue`

- [x] Add `fetchTtsSync` response types and request flow.
- [x] Track playback elapsed time and expose it to `guide.vue`.
- [x] Derive the active mouth frame from `mouth_cues`.
- [x] Stop playback and reset mouth state when sending a new message or leaving the page.

### Task 4: Deployment Notes And Verification

**Files:**
- Modify: `.env.example`
- Create: `docs/miniprogram-digital-human-deployment.md`

- [x] Document required environment variables and WeChat legal domain settings.
- [x] Run backend voice tests.
- [x] Run mini program build verification for `mp-weixin`.
