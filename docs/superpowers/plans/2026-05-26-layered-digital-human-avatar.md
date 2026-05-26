# Layered Digital Human Avatar Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace full-image expression switching with a stable layered avatar that synchronizes speech, facial expression, blinking, and mouth shapes in the WeChat mini program.

**Architecture:** Keep `base_halfbody.png` fixed and render transparent eye, brow, and mouth layers in one shared `455 x 700` coordinate system. Keep the current `/api/tourist/voice/tts-sync` contract and CosyVoice cue generation; a frontend expression controller maps existing five mouth enums and guide state to refined visual layers.

**Tech Stack:** uni-app Vue 3, TypeScript, WeChat `InnerAudioContext`, CSS animation, transparent PNG assets served from OSS, Node assertion scripts, pytest.

---

## File Responsibilities

- `miniprogram/src/config/avatarAssets.ts`: versioned asset manifest and exact local-patch boxes; it is the only file that knows OSS asset URLs and canvas coordinates.
- `miniprogram/src/utils/avatarExpression.ts`: pure state logic for emotion, blink scheduling, and detailed mouth-frame selection.
- `miniprogram/src/components/DigitalHuman.vue`: renderer only; composes fixed base plus transparent layers and applies small motion transforms.
- `miniprogram/src/pages/guide/guide.vue`: supplies existing `mouth`, `isSpeaking`, and `isThinking` values and chooses high-level guide emotion.
- `miniprogram/tests/avatarExpression.test.mjs`: state and layer-selection regression coverage.

### Task 1: Visual Prototype Approval Gate

**Files:**
- Create outside production source: `.superpowers/brainstorm/<session>/content/layered-avatar-prototype.html`

- [ ] **Step 1: Build a no-API dynamic prototype**

Create a browser-only preview using the current fixed base image, current mouth PNG layers and blink layer, with buttons for `待机`, `思考`, and `讲解`. Use local browser speech synthesis only for the demo narration, and run a sample visual cue sequence while it speaks so no DashScope request or storage charge is incurred.

- [ ] **Step 2: Review the prototype with the user**

Acceptance checks:

```text
1. 待机状态仅自然眨眼和微弱呼吸，不挑眉。
2. 思考状态动作克制，不出现脸部替换闪动。
3. 讲解状态能看到闭口、窄口、中开、大开、圆口的明显差异。
4. 角色五官位置在所有状态中保持固定。
```

- [ ] **Step 3: Stop before production integration until approved**

Expected result: the user explicitly accepts the motion/style direction or requests a revised prototype. No mini program production code or final OSS asset is changed in this task.

### Task 2: Produce Stable Versioned Layer Assets

**Files:**
- Create: `miniprogram/src/static/digital-human-v2/base_halfbody.png`
- Create: `miniprogram/src/static/digital-human-v2/eyes_open.png`
- Create: `miniprogram/src/static/digital-human-v2/eyes_half.png`
- Create: `miniprogram/src/static/digital-human-v2/eyes_closed.png`
- Create: `miniprogram/src/static/digital-human-v2/brows_neutral.png`
- Create: `miniprogram/src/static/digital-human-v2/brows_focus.png`
- Create: `miniprogram/src/static/digital-human-v2/brows_warm.png`
- Create: `miniprogram/src/static/digital-human-v2/mouth_closed.png`
- Create: `miniprogram/src/static/digital-human-v2/mouth_bilabial.png`
- Create: `miniprogram/src/static/digital-human-v2/mouth_narrow.png`
- Create: `miniprogram/src/static/digital-human-v2/mouth_mid.png`
- Create: `miniprogram/src/static/digital-human-v2/mouth_big.png`
- Create: `miniprogram/src/static/digital-human-v2/mouth_round.png`
- Create: `miniprogram/src/config/avatarAssets.ts`

- [ ] **Step 1: Export the asset manifest before component changes**

Create the coordinate and resource contract:

```ts
export type VisualMouth =
  | 'closed'
  | 'bilabial'
  | 'narrow'
  | 'mid'
  | 'big'
  | 'round'

export const avatarCanvas = { width: 455, height: 700 }
export const avatarBoxes = {
  eyes: { x: 105, y: 110, width: 244, height: 140 },
  brows: { x: 105, y: 90, width: 244, height: 95 },
  mouth: { x: 172, y: 266, width: 110, height: 57 },
}
```

Use new versioned filenames so the current production avatar remains available for rollback.

- [ ] **Step 2: Produce and visually align the layers**

Use the current base portrait as the identity reference and prepare feather-edged local PNG patches in the exact `eyes`, `brows`, and `mouth` box dimensions from the manifest. A patch may contain the surrounding skin required to cover the neutral feature underneath, but its outer edge must blend into the fixed base without a white halo. Reject any frame with jaw jump, eye drift, or hair/skin mismatch.

- [ ] **Step 3: Upload accepted assets to versioned OSS prefix**

Use `scenic-guide/digital-human-v2/` and verify every URL returns HTTP `200` before changing frontend asset configuration.

### Task 3: Expression State Mapping

**Files:**
- Create: `miniprogram/src/utils/avatarExpression.ts`
- Create: `miniprogram/tests/avatarExpression.test.mjs`

- [ ] **Step 1: Write failing state-mapping tests**

```ts
assert.equal(selectBrow('thinking'), 'focus')
assert.equal(selectBrow('speaking'), 'warm')
assert.equal(selectMouth('closed', { speaking: false }), 'closed')
assert.equal(selectMouth('closed', { speaking: true }), 'bilabial')
assert.equal(selectMouth('mid', { speaking: true }), 'mid')
assert.equal(selectMouth('big', { speaking: true }), 'big')
assert.equal(canBlink({ mouth: 'big', speaking: true }), false)
assert.equal(canBlink({ mouth: 'small', speaking: true }), true)
```

- [ ] **Step 2: Run tests to observe failure**

Run:

```powershell
cd "D:\AI digital person\.worktrees\admin-backend-phase1\miniprogram"
node tests\avatarExpression.test.mjs
```

Expected: failure because `src/utils/avatarExpression.ts` does not exist.

- [ ] **Step 3: Implement pure selection functions**

Provide exports with no Vue or `uni` dependency:

```ts
export type GuideEmotion = 'idle' | 'thinking' | 'speaking' | 'enthusiastic'
export function selectBrow(emotion: GuideEmotion): 'neutral' | 'focus' | 'warm'
export function selectMouth(mouth: MouthShape, context: MouthContext): VisualMouth
export function canBlink(context: { mouth: MouthShape; speaking: boolean }): boolean
```

Map the backend enum without changing its API: `small -> narrow`, `mid -> mid`, `big -> big`, `round -> round`, and `closed -> bilabial` only while speaking; idle `closed` remains the natural closed mouth. Preserve the existing `75ms` smoothing window in `mouthSmoothing.ts`.

- [ ] **Step 4: Run the new frontend test**

Run:

```powershell
node tests\avatarExpression.test.mjs
```

Expected: `avatar expression behavior ok`.

### Task 4: Layered Avatar Renderer

**Files:**
- Modify: `miniprogram/src/components/DigitalHuman.vue`
- Modify: `miniprogram/src/pages/guide/guide.vue`
- Test: `miniprogram/tests/uiPolish.test.mjs`

- [ ] **Step 1: Extend the renderer regression test**

Add assertions that the component imports the versioned asset manifest and renders independent `brow-layer`, `eye-layer`, and `mouth-layer` elements, while no longer rendering an `expr_*` full-image replacement during speech.

- [ ] **Step 2: Run the UI regression to observe failure**

Run:

```powershell
node tests\uiPolish.test.mjs
```

Expected: failure because the component does not contain the new layered renderer elements.

- [ ] **Step 3: Replace expression switching with transparent layers**

Keep existing props compatible:

```ts
isSpeaking: boolean
isThinking: boolean
mouth?: 'closed' | 'small' | 'mid' | 'big' | 'round'
emotion?: 'neutral' | 'smile' | 'enthusiastic' | 'thinking'
```

Render `base -> brows -> eyes -> mouth` in fixed boxes derived from `avatarAssets.ts`. Idle uses neutral brows, thinking uses focus brows, speaking uses warm brows; speaking continues to accept `displayMouth` from `guide.vue`.

- [ ] **Step 4: Implement restrained motion**

Use CSS only:

```css
/* idle: <= 2rpx vertical breath; thinking: one slow nod loop; speaking: <= 3rpx breath */
/* mouth transition: 70-90ms transform/opacity; no face-scale animation */
```

Blink interval is randomized between `3200ms` and `6200ms`, includes an optional half-blink frame, and is skipped while visual mouth is `big`.

- [ ] **Step 5: Run renderer tests and build**

Run:

```powershell
node tests\avatarExpression.test.mjs
node tests\mouthSmoothing.test.mjs
node tests\uiPolish.test.mjs
npm.cmd run build:mp-weixin
```

Expected: tests print their passing confirmation and uni-app build reports `Build complete`.

### Task 5: End-to-End Playback Validation And Rollback

**Files:**
- Modify: `miniprogram/src/config/avatarAssets.ts`

- [ ] **Step 1: Verify existing API compatibility**

Run:

```powershell
cd "D:\AI digital person\.worktrees\admin-backend-phase1\backend"
$env:PYTHONPATH='.'
& "D:\ProgramData\condaData\envs_dirs\dev_envs_1\python.exe" -m pytest tests\test_tts_service.py tests\test_tourist_voice_api.py -q
```

Expected: the existing `audio_url / duration_ms / mouth_cues` contract tests pass without schema edits.

- [ ] **Step 2: Verify three user scenarios in WeChat Developer Tools**

```text
待机：保持端庄，观察至少两次自然眨眼。
思考：发送“灵山胜境适合半天游览吗”，文字生成前为专注表情且无五官错位。
讲解：播放“我在灵山大佛前，带您往前看九龙灌浴。”，观察圆口、大口、窄口切换与语音同步。
```

- [ ] **Step 3: Keep rollback immediate**

`avatarAssets.ts` retains a `v1` asset base constant until acceptance. If v2 assets exhibit white halo or drift on device, switch the selected base back to `scenic-guide/digital-human/` without altering TTS or chat behavior.
