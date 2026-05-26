# Live2D Digital Human H5 Prototype Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local browser-based Live2D guide prototype that renders the official Haru evaluation model and demonstrates natural idle, thinking, and speaking behavior driven by the project's existing five mouth cue types.

**Architecture:** Keep this proof of concept outside production source under `.superpowers/brainstorm/live2d-prototype-20260526/`. Extract the user-provided Cubism SDK as one matching release, customize its official TypeScript Web Demo with a small guide-control layer, and leave the mini program and backend untouched until the animation direction is accepted. A pure cue mapper turns the existing `closed/small/mid/big/round` vocabulary into smoothed `ParamMouthOpenY` and `ParamMouthForm` targets.

**Tech Stack:** Live2D Cubism SDK for Web 5-r.5, official TypeScript/Vite Demo, TypeScript, JavaScript module tests with Node.js, browser Canvas/WebGL, Codex in-app browser validation.

---

## File Responsibilities

- `.superpowers/brainstorm/live2d-prototype-20260526/sdk/CubismSdkForWeb-5-r.5/`: local extracted official SDK, Core, Framework, and Sample Resources; evaluation-only and not committed as production assets.
- `.superpowers/brainstorm/live2d-prototype-20260526/sdk/CubismSdkForWeb-5-r.5/Samples/TypeScript/Demo/index.html`: guide-themed prototype shell and controls around the official canvas.
- `.superpowers/brainstorm/live2d-prototype-20260526/sdk/CubismSdkForWeb-5-r.5/Samples/TypeScript/Demo/src/guidetimeline.mjs`: pure cue mapping, state transitions, and interpolation logic.
- `.superpowers/brainstorm/live2d-prototype-20260526/sdk/CubismSdkForWeb-5-r.5/Samples/TypeScript/Demo/src/guidetimeline.d.mts`: TypeScript contract for the pure JavaScript module.
- `.superpowers/brainstorm/live2d-prototype-20260526/sdk/CubismSdkForWeb-5-r.5/Samples/TypeScript/Demo/src/guideui.ts`: prototype UI, demo timeline clock, status buttons, and renderer bridge calls.
- `.superpowers/brainstorm/live2d-prototype-20260526/sdk/CubismSdkForWeb-5-r.5/Samples/TypeScript/Demo/src/lappmodel.ts`: apply guide mouth and posture parameter overrides after standard Live2D updates.
- `.superpowers/brainstorm/live2d-prototype-20260526/sdk/CubismSdkForWeb-5-r.5/Samples/TypeScript/Demo/src/lapplive2dmanager.ts`: expose guide commands to the page controller.
- `.superpowers/brainstorm/live2d-prototype-20260526/sdk/CubismSdkForWeb-5-r.5/Samples/TypeScript/Demo/src/lappsubdelegate.ts`: existing manager access point used by the guide UI.
- `.superpowers/brainstorm/live2d-prototype-20260526/sdk/CubismSdkForWeb-5-r.5/Samples/TypeScript/Demo/src/lappdelegate.ts`: expose the initialized subdelegate to the guide UI.
- `.superpowers/brainstorm/live2d-prototype-20260526/sdk/CubismSdkForWeb-5-r.5/Samples/TypeScript/Demo/src/lappdefine.ts`: load only the Haru sample model for deterministic preview.
- `.superpowers/brainstorm/live2d-prototype-20260526/tests/guidetimeline.test.mjs`: cue-to-parameter and smoothing behavior checks.

### Task 1: Stage the Matching Official SDK and Model for Local Evaluation

**Files:**
- Source: `D:\AI digital person\.worktrees\CubismSdkForWeb-5-r.5.zip`
- Verify only: `D:\AI digital person\.worktrees\live2dcubismcore.min.js`
- Create locally: `.superpowers/brainstorm/live2d-prototype-20260526/sdk/CubismSdkForWeb-5-r.5/**`

- [ ] **Step 1: Verify that the archive contains a complete matching Web sample**

Run:

```powershell
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::OpenRead('D:\AI digital person\.worktrees\CubismSdkForWeb-5-r.5.zip')
$required = @(
  'CubismSdkForWeb-5-r.5/Core/live2dcubismcore.min.js',
  'CubismSdkForWeb-5-r.5/Framework/src/live2dcubismframework.ts',
  'CubismSdkForWeb-5-r.5/Samples/TypeScript/Demo/package.json',
  'CubismSdkForWeb-5-r.5/Samples/Resources/Haru/Haru.model3.json',
  'CubismSdkForWeb-5-r.5/Samples/Resources/Haru/Haru.moc3'
)
$missing = $required | Where-Object { $null -eq $zip.GetEntry($_) }
$zip.Dispose()
if ($missing) { throw "Missing required SDK entries: $missing" }
```

Expected: no output and exit code `0`. The standalone `live2dcubismcore.min.js` is not copied because the ZIP already supplies the Core matching its Framework and models.

- [ ] **Step 2: Extract the official SDK into the isolated prototype workspace**

Run:

```powershell
$root = 'D:\AI digital person\.worktrees\admin-backend-phase1\.superpowers\brainstorm\live2d-prototype-20260526'
$sdkRoot = Join-Path $root 'sdk'
New-Item -ItemType Directory -Force -Path $sdkRoot | Out-Null
Expand-Archive -LiteralPath 'D:\AI digital person\.worktrees\CubismSdkForWeb-5-r.5.zip' -DestinationPath $sdkRoot -Force
Test-Path (Join-Path $sdkRoot 'CubismSdkForWeb-5-r.5\Samples\TypeScript\Demo\package.json')
```

Expected: `True`.

- [ ] **Step 3: Install the official Demo dependencies without modifying application packages**

Run:

```powershell
npm.cmd install
```

Working directory:

```text
D:\AI digital person\.worktrees\admin-backend-phase1\.superpowers\brainstorm\live2d-prototype-20260526\sdk\CubismSdkForWeb-5-r.5\Samples\TypeScript\Demo
```

Expected: dependencies install successfully in the isolated SDK demo directory.

### Task 2: Add a Testable Mouth Cue and State Timeline Controller

**Files:**
- Create: `.superpowers/brainstorm/live2d-prototype-20260526/sdk/CubismSdkForWeb-5-r.5/Samples/TypeScript/Demo/src/guidetimeline.mjs`
- Create: `.superpowers/brainstorm/live2d-prototype-20260526/sdk/CubismSdkForWeb-5-r.5/Samples/TypeScript/Demo/src/guidetimeline.d.mts`
- Test: `.superpowers/brainstorm/live2d-prototype-20260526/tests/guidetimeline.test.mjs`

- [ ] **Step 1: Write the failing Node behavior test**

Create `tests/guidetimeline.test.mjs`:

```js
import assert from 'node:assert/strict'
import {
  cueTarget,
  findCueAt,
  interpolateFrame,
  speakingDemoCues,
} from '../sdk/CubismSdkForWeb-5-r.5/Samples/TypeScript/Demo/src/guidetimeline.mjs'

assert.deepEqual(cueTarget('closed'), { openY: 0, form: 0 })
assert.deepEqual(cueTarget('big'), { openY: 0.92, form: 0.12 })
assert.deepEqual(cueTarget('round'), { openY: 0.5, form: -0.75 })
assert.equal(findCueAt(330, speakingDemoCues).mouth, 'round')

const middle = interpolateFrame(
  { openY: 0, form: 0 },
  { openY: 0.92, form: 0.12 },
  0.5,
)
assert.ok(middle.openY > 0 && middle.openY < 0.92)
assert.ok(middle.form > 0 && middle.form < 0.12)

console.log('Live2D guide timeline behavior ok')
```

- [ ] **Step 2: Run the test to verify it fails before the controller exists**

Run:

```powershell
node .superpowers\brainstorm\live2d-prototype-20260526\tests\guidetimeline.test.mjs
```

Working directory: `D:\AI digital person\.worktrees\admin-backend-phase1`

Expected: FAIL with `ERR_MODULE_NOT_FOUND` for `guidetimeline.mjs`.

- [ ] **Step 3: Implement the pure cue mapping and interpolation module**

Create `src/guidetimeline.mjs`:

```js
export const speakingDemoCues = [
  { startMs: 0, endMs: 100, mouth: 'closed' },
  { startMs: 100, endMs: 250, mouth: 'mid' },
  { startMs: 250, endMs: 410, mouth: 'round' },
  { startMs: 410, endMs: 590, mouth: 'big' },
  { startMs: 590, endMs: 760, mouth: 'small' },
  { startMs: 760, endMs: 960, mouth: 'mid' },
  { startMs: 960, endMs: 1100, mouth: 'closed' },
]

const targets = {
  closed: { openY: 0, form: 0 },
  small: { openY: 0.18, form: 0.1 },
  mid: { openY: 0.48, form: 0 },
  big: { openY: 0.92, form: 0.12 },
  round: { openY: 0.5, form: -0.75 },
}

export function cueTarget(mouth) {
  return targets[mouth] || targets.closed
}

export function findCueAt(elapsedMs, cues) {
  return cues.find((cue) => elapsedMs >= cue.startMs && elapsedMs < cue.endMs)
    || { startMs: elapsedMs, endMs: elapsedMs + 1, mouth: 'closed' }
}

export function interpolateFrame(current, target, blend) {
  const weight = Math.min(1, Math.max(0, blend))
  return {
    openY: current.openY + (target.openY - current.openY) * weight,
    form: current.form + (target.form - current.form) * weight,
  }
}
```

Create `src/guidetimeline.d.mts`:

```ts
export type MouthShape = 'closed' | 'small' | 'mid' | 'big' | 'round'
export type MouthTarget = { openY: number; form: number }
export type MouthCue = { startMs: number; endMs: number; mouth: MouthShape }
export const speakingDemoCues: MouthCue[]
export function cueTarget(mouth: MouthShape): MouthTarget
export function findCueAt(elapsedMs: number, cues: MouthCue[]): MouthCue
export function interpolateFrame(
  current: MouthTarget,
  target: MouthTarget,
  blend: number,
): MouthTarget
```

- [ ] **Step 4: Run the test to verify the mapping and smoothing behavior passes**

Run:

```powershell
node .superpowers\brainstorm\live2d-prototype-20260526\tests\guidetimeline.test.mjs
```

Expected: `Live2D guide timeline behavior ok`.

### Task 3: Expose Safe Guide Controls in the Official Live2D Demo

**Files:**
- Modify: `.superpowers/brainstorm/live2d-prototype-20260526/sdk/CubismSdkForWeb-5-r.5/Samples/TypeScript/Demo/src/lappdefine.ts`
- Modify: `.superpowers/brainstorm/live2d-prototype-20260526/sdk/CubismSdkForWeb-5-r.5/Samples/TypeScript/Demo/src/lappmodel.ts`
- Modify: `.superpowers/brainstorm/live2d-prototype-20260526/sdk/CubismSdkForWeb-5-r.5/Samples/TypeScript/Demo/src/lapplive2dmanager.ts`
- Modify: `.superpowers/brainstorm/live2d-prototype-20260526/sdk/CubismSdkForWeb-5-r.5/Samples/TypeScript/Demo/src/lappdelegate.ts`

- [ ] **Step 1: Limit model loading to the expression-capable Haru evaluation model**

Modify `src/lappdefine.ts`:

```ts
export const ModelDir: string[] = ['Haru'];
export const ModelDirSize: number = ModelDir.length;
export const GuideIdleExpression = 'F01';
export const GuideThinkingExpression = 'F03';
export const GuideSpeakingExpression = 'F05';
```

Expected: the next model button cannot switch the prototype away from the selected evaluation character.

- [ ] **Step 2: Add mouth and posture overrides after the standard model update**

In `src/lappmodel.ts`, add state and methods to `LAppModel`:

```ts
private _guideMouthOpenY = 0.0;
private _guideMouthForm = 0.0;
private _guideAngleY = 0.0;
private _guideBodyAngleX = 0.0;
private _idParamMouthOpenY: CubismIdHandle;
private _idParamMouthForm: CubismIdHandle;
private _idParamBodyAngleX: CubismIdHandle;

public setGuideMouth(openY: number, form: number): void {
  this._guideMouthOpenY = openY;
  this._guideMouthForm = form;
}

public setGuidePosture(angleY: number, bodyAngleX: number): void {
  this._guideAngleY = angleY;
  this._guideBodyAngleX = bodyAngleX;
}
```

Initialize IDs alongside existing default parameter IDs:

```ts
this._idParamMouthOpenY = CubismFramework.getIdManager().getId(
  CubismDefaultParameterId.ParamMouthOpenY
);
this._idParamMouthForm = CubismFramework.getIdManager().getId(
  CubismDefaultParameterId.ParamMouthForm
);
this._idParamBodyAngleX = CubismFramework.getIdManager().getId(
  CubismDefaultParameterId.ParamBodyAngleX
);
```

After `this._updateScheduler.onLateUpdate(this._model, deltaTimeSeconds);` and before `this._model.update();`, apply the prototype overrides:

```ts
this._model.setParameterValueById(this._idParamMouthOpenY, this._guideMouthOpenY);
this._model.setParameterValueById(this._idParamMouthForm, this._guideMouthForm);
this._model.addParameterValueById(this._idParamAngleY, this._guideAngleY, 0.25);
this._model.addParameterValueById(this._idParamBodyAngleX, this._guideBodyAngleX, 0.18);
```

Expected: guide mouth targets take precedence over any bundled demo sound lip sync while standard breathing and blink effects remain active.

- [ ] **Step 3: Add manager-level commands for the UI adapter**

In `src/lapplive2dmanager.ts`, add:

```ts
public setGuideMouth(openY: number, form: number): void {
  this._models[0]?.setGuideMouth(openY, form);
}

public setGuidePosture(angleY: number, bodyAngleX: number): void {
  this._models[0]?.setGuidePosture(angleY, bodyAngleX);
}

public setGuideExpression(expressionId: string): void {
  this._models[0]?.setExpression(expressionId);
}
```

- [ ] **Step 4: Expose the initialized manager from the application delegate**

In `src/lappdelegate.ts`, add:

```ts
public getGuideManager(): LAppLive2DManager | null {
  return this._subdelegates[0]?.getLive2DManager() || null;
}
```

Import the manager type:

```ts
import { LAppLive2DManager } from './lapplive2dmanager';
```

- [ ] **Step 5: Run TypeScript verification**

Run:

```powershell
npm.cmd run test
```

Working directory: the extracted `Samples\TypeScript\Demo` folder.

Expected: TypeScript compilation completes without errors.

### Task 4: Build the Guide Prototype UI and Demonstration Playback

**Files:**
- Modify: `.superpowers/brainstorm/live2d-prototype-20260526/sdk/CubismSdkForWeb-5-r.5/Samples/TypeScript/Demo/index.html`
- Create: `.superpowers/brainstorm/live2d-prototype-20260526/sdk/CubismSdkForWeb-5-r.5/Samples/TypeScript/Demo/src/guideui.ts`
- Modify: `.superpowers/brainstorm/live2d-prototype-20260526/sdk/CubismSdkForWeb-5-r.5/Samples/TypeScript/Demo/src/main.ts`

- [ ] **Step 1: Replace the generic full-screen page shell with a guide preview layout**

Update `index.html` to include:

```html
<main class="prototype-shell">
  <section class="avatar-panel">
    <header>灵山胜境 AI 导游 · Live2D 动态样片</header>
    <div id="live2d-stage"></div>
    <span id="guide-status" class="status-pill">待机</span>
  </section>
  <aside class="control-panel">
    <p class="eyebrow">动作验证角色</p>
    <h1>真实 Live2D 讲解预览</h1>
    <p>本样片用于验证自然眨眼、表情与语音口型同步，角色外观不是最终景区形象。示范音频来自官方本地样例资源，仅用于动作评估。</p>
    <nav class="mode-tabs" aria-label="状态预览">
      <button data-mode="idle" class="active">待机</button>
      <button data-mode="thinking">思考</button>
      <button data-mode="speaking">讲解</button>
    </nav>
    <button id="play-narration" class="primary">播放示范讲解</button>
    <dl class="metrics">
      <div><dt>嘴型 Cue</dt><dd id="cue-output">closed</dd></div>
      <div><dt>开口参数</dt><dd id="open-output">0.00</dd></div>
      <div><dt>嘴型参数</dt><dd id="form-output">0.00</dd></div>
      <div><dt>模型</dt><dd>Haru / evaluation</dd></div>
    </dl>
  </aside>
</main>
```

Add scoped layout CSS in the same prototype HTML so that the appended Live2D canvas is positioned inside `#live2d-stage`, with a bright jade background consistent with the selected application theme.

```css
:root {
  --jade: #238fa3;
  --mist: #edf9f6;
  --line: #d7ebe8;
  --ink: #102e3c;
  --accent: #c85d48;
}
* { box-sizing: border-box; }
html, body { margin: 0; min-height: 100%; font-family: "Microsoft YaHei", Arial, sans-serif; color: var(--ink); }
body { background: linear-gradient(135deg, #f7fdfb 0%, var(--mist) 100%); }
.prototype-shell { min-height: 100vh; display: grid; grid-template-columns: minmax(380px, 520px) minmax(360px, 490px); gap: 48px; align-items: center; justify-content: center; padding: 32px; }
.avatar-panel, .control-panel { border-radius: 24px; overflow: hidden; border: 1px solid var(--line); background: #fff; box-shadow: 0 18px 46px rgba(17, 77, 86, .09); }
.avatar-panel header { padding: 18px; text-align: center; background: linear-gradient(90deg, var(--jade), #2aaec0); color: #fff; font-weight: 700; }
#live2d-stage { position: relative; height: 620px; background: linear-gradient(180deg, #f5fffd, #e7f6f3); overflow: hidden; }
#live2d-stage .live2d-canvas { position: absolute; inset: 0; width: 100% !important; height: 100% !important; }
.status-pill { display: block; width: fit-content; margin: -16px auto 20px; position: relative; padding: 6px 18px; border-radius: 18px; background: #fff; color: var(--jade); font-weight: 700; }
.control-panel { padding: 38px 36px; }
.eyebrow { margin: 0; color: var(--jade); font-weight: 700; font-size: 13px; }
h1 { margin: 12px 0 14px; font-size: 32px; letter-spacing: 0; }
.mode-tabs { margin: 30px 0 22px; padding: 6px; display: flex; gap: 6px; border-radius: 14px; background: #eef7f5; }
.mode-tabs button { flex: 1; border: 0; padding: 13px 8px; border-radius: 10px; color: #496971; background: transparent; font-size: 16px; font-weight: 700; }
.mode-tabs button.active { color: var(--jade); background: #fff; }
.primary { width: 100%; height: 54px; border: 0; border-radius: 12px; background: linear-gradient(90deg, var(--jade), #2aaec0); color: #fff; font-size: 16px; font-weight: 700; }
.metrics { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 26px 0 0; }
.metrics div { padding: 14px; border-radius: 12px; background: #f4faf9; }
.metrics dt { color: #59777f; font-size: 12px; }
.metrics dd { margin: 6px 0 0; font-weight: 700; }
```

- [ ] **Step 2: Make the SDK append its canvas into the prototype stage**

In `src/lappdelegate.ts`, replace the body append target inside `initializeSubdelegates()`:

```ts
const stage = document.getElementById('live2d-stage') || document.body;
stage.appendChild(canvas);
canvas.classList.add('live2d-canvas');
```

Expected: Live2D is framed in the avatar preview section rather than covering the controls.

- [ ] **Step 3: Add the state and speaking demonstration controller**

Create `src/guideui.ts`:

```ts
import { LAppDelegate } from './lappdelegate'
import * as LAppDefine from './lappdefine'
import {
  cueTarget,
  findCueAt,
  interpolateFrame,
  speakingDemoCues,
  type MouthTarget,
} from './guidetimeline.mjs'

type Mode = 'idle' | 'thinking' | 'speaking'

let mode: Mode = 'idle'
let frame: MouthTarget = { openY: 0, form: 0 }
let demoTimer = 0
const demoAudio = new Audio('/Resources/Haru/sounds/haru_Info_14.wav')

function manager() {
  return LAppDelegate.getInstance().getGuideManager()
}

function setMode(nextMode: Mode): void {
  mode = nextMode
  const expressions = {
    idle: LAppDefine.GuideIdleExpression,
    thinking: LAppDefine.GuideThinkingExpression,
    speaking: LAppDefine.GuideSpeakingExpression,
  }
  manager()?.setGuideExpression(expressions[nextMode])
  manager()?.setGuidePosture(nextMode === 'thinking' ? -4 : 0, nextMode === 'speaking' ? 1.5 : 0)
  document.getElementById('guide-status')!.textContent =
    nextMode === 'idle' ? '待机' : nextMode === 'thinking' ? '思考中' : '讲解中'
  document.querySelectorAll<HTMLButtonElement>('[data-mode]').forEach((button) => {
    button.classList.toggle('active', button.dataset.mode === nextMode)
  })
}

function drawSpeechFrame(_now: number): void {
  const elapsed = (demoAudio.currentTime * 1000) % 1100
  const cue = findCueAt(elapsed, speakingDemoCues)
  frame = interpolateFrame(frame, cueTarget(cue.mouth), 0.42)
  manager()?.setGuideMouth(frame.openY, frame.form)
  document.getElementById('cue-output')!.textContent = cue.mouth
  document.getElementById('open-output')!.textContent = frame.openY.toFixed(2)
  document.getElementById('form-output')!.textContent = frame.form.toFixed(2)
  demoTimer = window.requestAnimationFrame(drawSpeechFrame)
}

export function mountGuideUi(): void {
  document.querySelectorAll<HTMLButtonElement>('[data-mode]').forEach((button) => {
    button.addEventListener('click', () => {
      window.cancelAnimationFrame(demoTimer)
      demoAudio.pause()
      demoAudio.currentTime = 0
      manager()?.setGuideMouth(0, 0)
      setMode(button.dataset.mode as Mode)
    })
  })
  document.getElementById('play-narration')!.addEventListener('click', () => {
    setMode('speaking')
    window.cancelAnimationFrame(demoTimer)
    demoTimer = window.requestAnimationFrame(drawSpeechFrame)
    demoAudio.currentTime = 0
    void demoAudio.play()
  })
  demoAudio.addEventListener('ended', () => {
    window.cancelAnimationFrame(demoTimer)
    manager()?.setGuideMouth(0, 0)
    setMode('idle')
  })
  setMode('idle')
}
```

- [ ] **Step 4: Mount the guide controls after the Live2D app is initialized**

Modify `src/main.ts`:

```ts
import { mountGuideUi } from './guideui'
```

After `LAppDelegate.getInstance().run();`, add:

```ts
mountGuideUi();
```

- [ ] **Step 5: Build the H5 sample**

Run:

```powershell
npm.cmd run build
```

Working directory: the extracted `Samples\TypeScript\Demo` folder.

Expected: Vite creates `dist/` with no TypeScript or asset-copy failures.

### Task 5: Run and Visually Verify the Live2D Evaluation Sample

**Files:**
- Validate: `.superpowers/brainstorm/live2d-prototype-20260526/sdk/CubismSdkForWeb-5-r.5/Samples/TypeScript/Demo/**`

- [ ] **Step 1: Start the prototype development server**

Run:

```powershell
npm.cmd run start -- --port 58110
```

Working directory: the extracted `Samples\TypeScript\Demo` folder.

Expected: a Vite local URL such as `http://localhost:58110/`.

- [ ] **Step 2: Open the sample in the in-app browser and confirm nonblank WebGL rendering**

Open `http://localhost:58110/` in the in-app browser.

Expected: Haru is visible inside the left preview area; the page shows the control panel and no JavaScript error overlay.

- [ ] **Step 3: Check each state visually**

Verify:

```text
待机: naturally blinking/breathing, with no repeated eyebrow raising.
思考: closed mouth and restrained posture change.
讲解: a gentle expression transition, without replacing the face image.
```

- [ ] **Step 4: Play the speaking demonstration and verify mouth parameters**

Click `播放示范讲解`.

Expected:

```text
The cue display cycles through closed, mid, round, big, and small.
Open/form numerical values change smoothly.
The Live2D mouth visibly changes continuously while blinking and breathing remain natural.
No PNG overlay, white halo, or facial-feature displacement occurs.
```

- [ ] **Step 5: Capture review screenshots and stop before production integration**

Capture screenshots for idle, thinking, and speaking states. Present the local sample URL and screenshots to the user.

Expected: wait for explicit user approval of the Live2D motion result before planning any `web-view`, OSS, or mini-program source integration.

## Verification Commands

Run from `D:\AI digital person\.worktrees\admin-backend-phase1`:

```powershell
node .superpowers\brainstorm\live2d-prototype-20260526\tests\guidetimeline.test.mjs
```

Run from the extracted SDK Demo folder:

```powershell
npm.cmd run test
npm.cmd run build
```

Visual verification:

```text
http://localhost:58110/
```

## Commit Boundary

The official SDK Core, Framework and sample model are local evaluation resources governed by Live2D terms and are not added to production source or committed as application assets. Commit this implementation plan document only. After the user accepts the running sample, create a separate integration design and plan for a licensed final model and the mini-program hosting method.
