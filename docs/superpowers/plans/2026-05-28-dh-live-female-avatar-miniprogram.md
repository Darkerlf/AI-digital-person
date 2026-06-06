# DH_live Female Guide Avatar Mini-Program Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate the female DH_live character package from the new neutral guide video, wire it into the local H5 prototype, and add a mini-program web-view entry for the high-realism AI guide.

**Architecture:** Keep the native mini-program AI guide as a fallback. Use the existing H5 DH_live prototype as the runtime host, replace its local character assets with the generated female guide package, and expose it from the mini-program through a configurable `web-view` page.

**Tech Stack:** DH_live preprocessing scripts, Python model checkpoints, FastAPI avatar TTS endpoint, vanilla H5 prototype, UniApp/Vue 3 mini-program, WeChat `web-view`.

---

### Task 1: Generate Female DH_live Assets

**Files:**
- Source: `digital_human_new/万相 2.7_1779867680842.mp4`
- Source: `DH_live/checkpoint/`
- Output: `prototypes/dh-live-guide/runtime/assets/01.mp4`
- Output: `prototypes/dh-live-guide/runtime/assets/combined_data.json.gz`

- [ ] Ensure the DH_live preprocessing repo is available in a temp tool directory.
- [ ] Install only missing Python dependencies into the configured development environment.
- [ ] Copy the project checkpoint directory into the tool repo.
- [ ] Run `data_preparation_mini.py` against the neutral source video.
- [ ] Run `data_preparation_web.py` against the generated intermediate directory.
- [ ] Copy generated assets into the ignored H5 prototype runtime.
- [ ] Verify generated files exist and are non-empty.

### Task 2: Update Local H5 Prototype Runtime

**Files:**
- Modify: `prototypes/dh-live-guide/README.md`
- Runtime output: `prototypes/dh-live-guide/runtime/assets/*`

- [ ] Document the female asset generation command.
- [ ] Serve the prototype locally.
- [ ] Open the prototype in a browser and verify the visible character is the female guide.
- [ ] Send a short question and verify avatar speech still uses `/api/tourist/voice/avatar-tts`.

### Task 3: Add Mini-Program Web-View Entry

**Files:**
- Modify: `miniprogram/src/pages.json`
- Create: `miniprogram/src/pages/avatar/avatar.vue`
- Modify: `miniprogram/src/config/assets.ts`
- Modify: `miniprogram/src/pages/guide/guide.vue`

- [ ] Add a configurable `dhLiveGuideUrl` value for local and future HTTPS deployment.
- [ ] Register a new `pages/avatar/avatar` route.
- [ ] Implement a `web-view` page that loads the configured H5 URL.
- [ ] Add a visible entry button from the AI guide page to the high-realism guide page.
- [ ] Keep the existing native guide page usable if the H5 page is unavailable.

### Task 4: Verification

**Commands:**
- `npm.cmd test` from `prototypes/dh-live-guide`
- `npm.cmd run build:mp-weixin` from `miniprogram`

- [ ] Run H5 unit tests.
- [ ] Run mini-program build.
- [ ] Browser-check the local H5 page.
- [ ] Report any production-only requirements such as HTTPS domain and WeChat business-domain setup.

