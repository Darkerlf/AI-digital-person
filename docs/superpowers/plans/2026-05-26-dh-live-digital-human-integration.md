# DH_live Audio-Driven Digital Human Prototype Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standalone H5 guide prototype that uses the existing RAG/chat backend and CosyVoice speech to drive the `DH_live` audio-reactive digital-human renderer.

**Architecture:** Keep the released mini-program AI guide untouched while adding a parallel browser sample under `prototypes/dh-live-guide/`. Add a narrowly scoped FastAPI endpoint that requests the mono-compatible `wav`/16 kHz output needed by `DH_live`; the prototype streams current chat text, creates short speech requests early, and feeds ordered audio segments into the renderer's existing `Module._setAudioBuffer` path. Stage DH_live third-party runtime and branded character assets locally through a copy script and ignore them in Git.

**Tech Stack:** FastAPI, pytest, DashScope CosyVoice HTTP API, vanilla ES modules, Node.js built-in test runner, DH_live WebAssembly/WebGL2 browser renderer, PowerShell staging script, Codex in-app browser verification.

---

## File Responsibilities

- `backend/app/services/tts_service.py`: exposes an avatar-specific CosyVoice synthesis method while preserving the native mini-program MP3/timestamp path.
- `backend/app/api/routers/tourist_voice.py`: publishes `POST /api/tourist/voice/avatar-tts`, returning `audio/wav` bytes only for audio-driven avatar clients.
- `backend/tests/test_tts_service.py`: verifies the avatar request selects `wav` at 16 kHz without changing ordinary TTS payload defaults.
- `backend/tests/test_tourist_voice_api.py`: verifies the new binary response contract and validates empty input.
- `prototypes/dh-live-guide/.gitignore`: keeps staged upstream JavaScript, WASM, sample video and feature data out of version control.
- `prototypes/dh-live-guide/scripts/stage-dh-live-runtime.ps1`: copies the locally evaluated DH_live web runtime into `runtime/` and overlays the project's prototype HTML.
- `prototypes/dh-live-guide/shell/index.html`: the tracked H5 guide surface, canvas mounts and script entry points; copied into the locally staged runtime so upstream relative asset URLs continue to work.
- `prototypes/dh-live-guide/src/phraseChunker.mjs`: pure early-phrase extraction for low-latency narration.
- `prototypes/dh-live-guide/src/speechPipeline.mjs`: schedules asynchronous TTS segments while enforcing playback order.
- `prototypes/dh-live-guide/src/backendClient.mjs`: parses existing SSE chat responses and retrieves avatar WAV bytes.
- `prototypes/dh-live-guide/src/dhLiveAudioBridge.mjs`: transfers audio bytes to DH_live WASM and uses browser playback as the audible clock.
- `prototypes/dh-live-guide/src/app.mjs`: DOM state, form handling, transcript rendering and diagnostics.
- `prototypes/dh-live-guide/src/styles.css`: restrained scenic-guide prototype layout.
- `prototypes/dh-live-guide/tests/*.test.mjs`: Node tests for phrase release, ordered audio and WASM bridge behavior.
- `prototypes/dh-live-guide/package.json`: local test command for ES-module tests.
- `prototypes/dh-live-guide/README.md`: setup, runtime-staging, launch, validation and licensing notes.

## Technical Constraint Confirmed Before Implementation

The DH_live repository specifies that audio supplied to its avatar pipeline must be a
single-channel 16 kHz WAV file. The current native mini-program TTS path uses MP3 output
and must not be changed because it already serves playback and `mouth_cues`.

The official CosyVoice non-real-time API documentation states that `format` supports `wav`
and that `sample_rate` supports `16000`. Therefore the prototype adds a separate avatar
speech endpoint rather than transcoding audio or modifying the released endpoint:

- CosyVoice API reference: <https://help.aliyun.com/zh/model-studio/non-realtime-cosyvoice-api/>
- DH_live repository: <https://github.com/kleinlee/DH_live/tree/main>

### Task 1: Add the DH_live-Compatible WAV Speech Endpoint

**Files:**
- Modify: `backend/app/services/tts_service.py`
- Modify: `backend/app/api/routers/tourist_voice.py`
- Test: `backend/tests/test_tts_service.py`
- Test: `backend/tests/test_tourist_voice_api.py`

- [ ] **Step 1: Write failing service tests for an avatar-specific CosyVoice payload**

Append focused tests to `backend/tests/test_tts_service.py`:

```python
def test_avatar_payload_requests_dh_live_compatible_wav_audio() -> None:
    service = TTSService()

    payload = service.build_cosyvoice_payload(
        "欢迎来到灵山胜境",
        voice="loongbella_v3",
        audio_format="wav",
        sample_rate=16000,
        word_timestamp_enabled=False,
    )

    assert payload["input"]["format"] == "wav"
    assert payload["input"]["sample_rate"] == 16000
    assert payload["input"]["word_timestamp_enabled"] is False


def test_default_cosyvoice_payload_keeps_timestamp_enabled() -> None:
    service = TTSService()

    payload = service.build_cosyvoice_payload("欢迎来到灵山胜境")

    assert payload["input"]["format"] == service.default_format
    assert payload["input"]["sample_rate"] == 24000
    assert payload["input"]["word_timestamp_enabled"] is True


def test_avatar_audio_rejects_models_that_cannot_request_wav_16khz(monkeypatch) -> None:
    service = TTSService()
    monkeypatch.setattr(service, "model", "qwen3-tts-instruct-flash")

    with pytest.raises(RuntimeError, match="CosyVoice"):
        asyncio.run(service.synthesize_avatar_wav("欢迎来到灵山胜境"))
```

Use the existing imports in this test module; if `asyncio` or `pytest` is not yet imported,
add `import asyncio` and `import pytest` with the other test imports.

- [ ] **Step 2: Write failing API tests for `avatar-tts`**

Append to `backend/tests/test_tourist_voice_api.py`:

```python
class FakeAvatarTTSService:
    async def synthesize_avatar_wav(self, text: str, voice: str | None = None) -> bytes:
        assert text == "欢迎来到灵山胜境"
        assert voice == "loongbella_v3"
        return b"RIFF-fake-avatar-wav"


def test_avatar_tts_returns_wav_bytes_for_dh_live(monkeypatch):
    from app.api.routers import tourist_voice

    monkeypatch.setattr(tourist_voice, "TTSService", FakeAvatarTTSService)
    client = TestClient(app)

    response = client.post(
        "/api/tourist/voice/avatar-tts",
        json={"text": "欢迎来到灵山胜境", "voice": "loongbella_v3"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("audio/wav")
    assert response.content == b"RIFF-fake-avatar-wav"


def test_avatar_tts_rejects_empty_text():
    client = TestClient(app)

    response = client.post("/api/tourist/voice/avatar-tts", json={"text": "  "})

    assert response.status_code == 400
```

- [ ] **Step 3: Run the new tests to confirm the endpoint and optional parameters do not exist**

Run:

```powershell
& 'D:\ProgramData\condaData\envs_dirs\dev_envs_1\python.exe' -m pytest backend\tests\test_tts_service.py backend\tests\test_tourist_voice_api.py -q
```

Working directory: `D:\AI digital person\.worktrees\admin-backend-phase1`

Expected: FAIL because `build_cosyvoice_payload` does not accept the new keyword
arguments and `/api/tourist/voice/avatar-tts` returns `404`.

- [ ] **Step 4: Parameterize CosyVoice generation without changing current defaults**

In `backend/app/services/tts_service.py`, expand the payload builder and request pipeline:

```python
    async def synthesize_avatar_wav(self, text: str, voice: str | None = None) -> bytes:
        if not text or not text.strip():
            return b""
        if not self.uses_cosyvoice_http:
            raise RuntimeError("DH_live avatar speech requires a CosyVoice model")

        audio_url = await self.create_dashscope_audio_url(
            text,
            voice=voice,
            audio_format="wav",
            sample_rate=16000,
            word_timestamp_enabled=False,
        )
        return await self.download_audio(audio_url)

    async def create_dashscope_audio_url(
        self,
        text: str,
        voice: str | None = None,
        *,
        audio_format: str | None = None,
        sample_rate: int = 24000,
        word_timestamp_enabled: bool = True,
    ) -> str:
        audio_url, _ = await self.create_dashscope_tts_result(
            text,
            voice=voice,
            audio_format=audio_format,
            sample_rate=sample_rate,
            word_timestamp_enabled=word_timestamp_enabled,
        )
        return audio_url

    async def create_dashscope_tts_result(
        self,
        text: str,
        voice: str | None = None,
        *,
        audio_format: str | None = None,
        sample_rate: int = 24000,
        word_timestamp_enabled: bool = True,
    ) -> tuple[str, list[dict]]:
        endpoint = self.cosyvoice_endpoint if self.uses_cosyvoice_http else self.generation_endpoint
        payload = (
            self.build_cosyvoice_payload(
                text,
                voice=voice,
                audio_format=audio_format,
                sample_rate=sample_rate,
                word_timestamp_enabled=word_timestamp_enabled,
            )
            if self.uses_cosyvoice_http
            else self.build_dashscope_generation_payload(text, voice=voice)
        )
        # Keep the existing request and result-extraction body below this block unchanged.

    def build_cosyvoice_payload(
        self,
        text: str,
        voice: str | None = None,
        *,
        audio_format: str | None = None,
        sample_rate: int = 24000,
        word_timestamp_enabled: bool = True,
    ) -> dict:
        return {
            "model": self.model,
            "input": {
                "text": text,
                "voice": voice or self.default_voice,
                "format": audio_format or self.default_format,
                "sample_rate": sample_rate,
                "volume": 50,
                "rate": 1.0,
                "pitch": 1.0,
                "language_hints": ["zh"],
                "word_timestamp_enabled": word_timestamp_enabled,
            },
        }
```

Keep `synthesize_sync_url()` calling `create_dashscope_tts_result(normalized, voice=voice)`
without overrides so the native mini-program still receives timestamp-driven mouth cues.

- [ ] **Step 5: Publish the avatar-only binary endpoint**

Add this route to `backend/app/api/routers/tourist_voice.py` after `text_to_speech`:

```python
@router.post("/avatar-tts")
async def text_to_avatar_speech(payload: TTSRequest):
    """Return DH_live-compatible 16 kHz WAV speech without mouth cue generation."""
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")

    tts = TTSService()
    audio_bytes = await tts.synthesize_avatar_wav(payload.text, voice=payload.voice)
    if not audio_bytes:
        raise HTTPException(status_code=502, detail="TTS returned empty audio")

    return StreamingResponse(
        io.BytesIO(audio_bytes),
        media_type="audio/wav",
        headers={"Content-Disposition": "inline; filename=avatar-tts.wav"},
    )
```

- [ ] **Step 6: Run backend tests for the new contract and existing lip-sync regression**

Run:

```powershell
& 'D:\ProgramData\condaData\envs_dirs\dev_envs_1\python.exe' -m pytest backend\tests\test_tts_service.py backend\tests\test_tourist_voice_api.py -q
```

Expected: PASS, including existing `/tts-sync` tests.

- [ ] **Step 7: Commit the isolated backend API change**

```powershell
git add backend/app/services/tts_service.py backend/app/api/routers/tourist_voice.py backend/tests/test_tts_service.py backend/tests/test_tourist_voice_api.py
git commit -m "feat: add avatar wav speech endpoint"
```

### Task 2: Scaffold a Trackable Prototype and an Ignored DH_live Runtime

**Files:**
- Create: `prototypes/dh-live-guide/.gitignore`
- Create: `prototypes/dh-live-guide/package.json`
- Create: `prototypes/dh-live-guide/scripts/stage-dh-live-runtime.ps1`
- Create: `prototypes/dh-live-guide/shell/index.html`
- Create: `prototypes/dh-live-guide/src/styles.css`

- [ ] **Step 1: Add the prototype package and asset-ignore boundary**

Create `prototypes/dh-live-guide/.gitignore`:

```gitignore
runtime/
```

Create `prototypes/dh-live-guide/package.json`:

```json
{
  "name": "dh-live-guide-prototype",
  "private": true,
  "type": "module",
  "scripts": {
    "test": "node --test tests/*.test.mjs"
  }
}
```

- [ ] **Step 2: Add a deterministic runtime staging script**

Create `prototypes/dh-live-guide/scripts/stage-dh-live-runtime.ps1`:

```powershell
param(
    [Parameter(Mandatory = $true)]
    [string] $SourceStaticDir
)

$ErrorActionPreference = 'Stop'
$prototypeRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
$source = Resolve-Path $SourceStaticDir
$runtime = Join-Path $prototypeRoot 'runtime'
$required = @(
    'js\DHLiveMini.js',
    'js\MiniMateLoader.js',
    'js\MiniLive2.js',
    'js\pako.min.js',
    'assets\01.mp4',
    'assets\combined_data.json.gz',
    'background\bg.mp4'
)

foreach ($relativePath in $required) {
    if (-not (Test-Path (Join-Path $source $relativePath))) {
        throw "DH_live runtime file missing: $relativePath"
    }
}

if (Test-Path $runtime) {
    Remove-Item -LiteralPath $runtime -Recurse -Force
}
New-Item -ItemType Directory -Path $runtime | Out-Null
foreach ($directory in @('js', 'assets', 'background', 'common')) {
    $candidate = Join-Path $source $directory
    if (Test-Path $candidate) {
        Copy-Item -LiteralPath $candidate -Destination $runtime -Recurse
    }
}
Copy-Item -LiteralPath (Join-Path $prototypeRoot 'shell\index.html') -Destination (Join-Path $runtime 'index.html')
Write-Output "DH_live runtime staged at $runtime"
```

This script must be run only against a resolved local clone of DH_live. It deliberately
places the upstream branded resources below ignored `runtime/`.

- [ ] **Step 3: Build the HTML shell around the exact IDs required by `MiniLive2.js`**

Create `prototypes/dh-live-guide/shell/index.html`:

```html
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>灵山胜境 AI 导游 - DH_live 动态样片</title>
    <link rel="stylesheet" href="../src/styles.css">
  </head>
  <body>
    <main class="guide-layout">
      <section class="avatar-surface" aria-label="动态数字人">
        <header>灵山胜境 AI 导游 · DH_live 动态样片</header>
        <div class="avatar-stage">
          <figure id="loadingSpinner"><strong>动态人物加载中...</strong></figure>
          <video id="background_video" src="background/bg.mp4" autoplay loop muted playsinline></video>
          <canvas id="canvas_video"></canvas>
          <canvas id="canvas_gl" width="184" height="184"></canvas>
          <canvas id="canvasEl"></canvas>
          <div id="screen2" aria-hidden="true"></div>
        </div>
        <span id="avatar-status" class="status-pill">加载中</span>
      </section>
      <section class="conversation-surface">
        <p class="eyebrow">音频驱动验证</p>
        <h1>真人感讲解样片</h1>
        <p class="hint">当前使用 DH_live 自带演示人物，仅用于测试口型与语音连贯性。</p>
        <div id="messages" class="messages" aria-live="polite"></div>
        <form id="guide-form" class="prompt-bar">
          <input id="question" value="请介绍一下灵山大佛，并推荐接下来游览的方向。" aria-label="请输入问题">
          <button id="send" type="submit">开始讲解</button>
        </form>
        <dl class="metrics">
          <div><dt>状态</dt><dd id="metric-state">等待加载</dd></div>
          <div><dt>首段开口延迟</dt><dd id="metric-latency">--</dd></div>
        </dl>
      </section>
    </main>
    <script src="js/pako.min.js"></script>
    <script src="js/DHLiveMini.js"></script>
    <script src="js/MiniMateLoader.js"></script>
    <script src="js/MiniLive2.js"></script>
    <script type="module" src="../src/app.mjs"></script>
  </body>
</html>
```

The page is served from `runtime/index.html`, so DH_live's original relative `assets/` and
`background/` URLs continue to resolve without patching vendor JavaScript.

- [ ] **Step 4: Add the visual shell stylesheet**

Create `prototypes/dh-live-guide/src/styles.css` with the full shell rules:

```css
:root {
  --jade: #238fa3;
  --jade-bright: #2aaec0;
  --mist: #edf9f6;
  --line: #d4eae7;
  --ink: #102e3c;
  --muted: #607b82;
  --accent: #c45d4b;
}
* { box-sizing: border-box; }
html, body { margin: 0; min-height: 100%; font-family: "Microsoft YaHei", Arial, sans-serif; color: var(--ink); }
body { background: linear-gradient(135deg, #f8fefd 0%, var(--mist) 100%); }
.guide-layout { min-height: 100vh; display: grid; grid-template-columns: minmax(350px, 470px) minmax(400px, 550px); align-items: center; justify-content: center; gap: 34px; padding: 28px; }
.avatar-surface, .conversation-surface { background: #fff; border: 1px solid var(--line); border-radius: 18px; box-shadow: 0 16px 40px rgba(20, 88, 96, .1); overflow: hidden; }
.avatar-surface header { padding: 16px; color: #fff; text-align: center; font-weight: 700; background: linear-gradient(90deg, var(--jade), var(--jade-bright)); }
.avatar-stage { height: 660px; position: relative; overflow: hidden; background: #effafa; }
#loadingSpinner { position: absolute; inset: 0; display: grid; place-items: center; margin: 0; color: var(--jade); z-index: 6; }
#background_video, #canvas_video { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: contain; }
#background_video { z-index: 0; }
#canvas_video { z-index: 1; }
#canvas_gl, #canvasEl { position: fixed; left: -9999px; top: -9999px; }
#screen2 { display: none !important; }
.status-pill { display: block; width: fit-content; position: relative; margin: -16px auto 18px; padding: 6px 18px; border-radius: 18px; background: #fff; color: var(--jade); font-weight: 700; z-index: 8; }
.conversation-surface { padding: 34px; min-height: 620px; display: flex; flex-direction: column; }
.eyebrow { margin: 0; color: var(--accent); font-size: 13px; font-weight: 700; }
h1 { margin: 8px 0 8px; font-size: 30px; letter-spacing: 0; }
.hint { margin: 0 0 22px; color: var(--muted); line-height: 1.65; }
.messages { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; padding: 4px 0 18px; }
.message { max-width: 86%; padding: 12px 15px; border-radius: 12px; line-height: 1.65; white-space: pre-wrap; }
.message.user { align-self: flex-end; color: #fff; background: var(--jade); }
.message.assistant { align-self: flex-start; background: #f0f7f6; }
.prompt-bar { display: grid; grid-template-columns: 1fr auto; gap: 10px; padding-top: 16px; border-top: 1px solid var(--line); }
.prompt-bar input { min-width: 0; border: 1px solid var(--line); border-radius: 10px; padding: 13px; font-size: 14px; }
.prompt-bar button { border: 0; border-radius: 10px; padding: 0 20px; color: #fff; font-weight: 700; background: linear-gradient(90deg, var(--jade), var(--jade-bright)); }
.prompt-bar button:disabled { opacity: .5; }
.metrics { display: flex; gap: 12px; margin: 18px 0 0; }
.metrics div { flex: 1; background: #f4faf9; border-radius: 10px; padding: 10px 12px; }
.metrics dt { color: var(--muted); font-size: 12px; }
.metrics dd { margin: 5px 0 0; font-weight: 700; }
@media (max-width: 900px) { .guide-layout { grid-template-columns: 1fr; } .avatar-stage { height: 560px; } }
```

- [ ] **Step 5: Obtain and stage the evaluated DH_live runtime locally**

Run:

```powershell
$sourceRepo = Join-Path $env:TEMP 'codex-dh-live-assessment-20260526'
if (-not (Test-Path (Join-Path $sourceRepo 'web_demo\static\js\DHLiveMini.js'))) {
    git clone --depth 1 https://github.com/kleinlee/DH_live.git $sourceRepo
}
& '.\prototypes\dh-live-guide\scripts\stage-dh-live-runtime.ps1' `
  -SourceStaticDir (Join-Path $sourceRepo 'web_demo\static')
Test-Path '.\prototypes\dh-live-guide\runtime\assets\combined_data.json.gz'
git status --short -- 'prototypes/dh-live-guide/runtime'
```

Expected:

```text
True
```

`git status` must not list `runtime/`, confirming the upstream renderer and branded
character remain local-only.

- [ ] **Step 6: Commit the trackable shell and safe staging boundary**

```powershell
git add prototypes/dh-live-guide/.gitignore prototypes/dh-live-guide/package.json prototypes/dh-live-guide/scripts/stage-dh-live-runtime.ps1 prototypes/dh-live-guide/shell/index.html prototypes/dh-live-guide/src/styles.css
git commit -m "feat: scaffold DH_live guide prototype"
```

### Task 3: Implement Low-Latency Speech Segmentation and Ordered TTS Scheduling

**Files:**
- Create: `prototypes/dh-live-guide/src/phraseChunker.mjs`
- Create: `prototypes/dh-live-guide/src/speechPipeline.mjs`
- Create: `prototypes/dh-live-guide/tests/phraseChunker.test.mjs`
- Create: `prototypes/dh-live-guide/tests/speechPipeline.test.mjs`

- [ ] **Step 1: Write failing phrase extraction tests**

Create `prototypes/dh-live-guide/tests/phraseChunker.test.mjs`:

```js
import test from 'node:test'
import assert from 'node:assert/strict'
import { extractPhrase, flushPhrase } from '../src/phraseChunker.mjs'

test('waits for a useful first phrase instead of speaking a greeting alone', () => {
  assert.equal(extractPhrase('您好。', true), null)
})

test('releases a short natural first narration phrase quickly', () => {
  const result = extractPhrase('您好。现在请随我向前看，灵山大佛庄严矗立。后续仍在生成', true)
  assert.deepEqual(result, {
    phrase: '您好。现在请随我向前看，灵山大佛庄严矗立。',
    rest: '后续仍在生成',
  })
})

test('flushes the final remaining answer', () => {
  assert.deepEqual(flushPhrase('最后我们前往九龙灌浴。'), {
    phrase: '最后我们前往九龙灌浴。',
    rest: '',
  })
})
```

- [ ] **Step 2: Write failing asynchronous playback-order tests**

Create `prototypes/dh-live-guide/tests/speechPipeline.test.mjs`:

```js
import test from 'node:test'
import assert from 'node:assert/strict'
import { SpeechPipeline } from '../src/speechPipeline.mjs'

test('starts TTS after the first speakable phrase and plays resolved audio in text order', async () => {
  const synthRequests = []
  const resolvers = []
  const played = []
  const pipeline = new SpeechPipeline({
    synthesize: (text) => new Promise((resolve) => {
      synthRequests.push(text)
      resolvers.push(resolve)
    }),
    play: async (segment) => played.push(segment.text),
  })

  pipeline.append('您好。现在请随我向前看，灵山大佛庄严矗立。')
  pipeline.append('随后我们继续前往九龙灌浴，观看动态演出。')
  pipeline.complete()
  assert.equal(synthRequests.length, 2)

  resolvers[1](new Uint8Array([2]))
  await Promise.resolve()
  assert.deepEqual(played, [])

  resolvers[0](new Uint8Array([1]))
  await pipeline.whenIdle()
  assert.deepEqual(played, synthRequests)
})
```

- [ ] **Step 3: Run tests to prove the pure scheduling modules are missing**

Run:

```powershell
npm.cmd test
```

Working directory: `D:\AI digital person\.worktrees\admin-backend-phase1\prototypes\dh-live-guide`

Expected: FAIL with `ERR_MODULE_NOT_FOUND` for `phraseChunker.mjs` or
`speechPipeline.mjs`.

- [ ] **Step 4: Implement the phrase extractor**

Create `prototypes/dh-live-guide/src/phraseChunker.mjs`:

```js
const HARD_BREAK = /[。！？!?；;]/
const SOFT_BREAK = /[，,、：:]/

export function extractPhrase(text, isFirst = false) {
  const source = text.trimStart()
  if (!source) return null
  const min = isFirst ? 14 : 26
  const hardLimit = isFirst ? 42 : 86
  let softCandidate = -1

  for (let index = 0; index < source.length; index += 1) {
    const char = source[index]
    if (SOFT_BREAK.test(char) && index >= min) softCandidate = index
    if (HARD_BREAK.test(char) && index >= min) return take(source, index + 1)
    if (index >= hardLimit) return take(source, (softCandidate > -1 ? softCandidate : index) + 1)
  }
  return null
}

export function flushPhrase(text) {
  const source = text.trim()
  return source ? { phrase: source, rest: '' } : null
}

function take(source, end) {
  return {
    phrase: source.slice(0, end).trim(),
    rest: source.slice(end).trimStart(),
  }
}
```

- [ ] **Step 5: Implement the ordered asynchronous speech pipeline**

Create `prototypes/dh-live-guide/src/speechPipeline.mjs`:

```js
import { extractPhrase, flushPhrase } from './phraseChunker.mjs'

export class SpeechPipeline {
  constructor({ synthesize, play, onSpeakingStart = () => {}, onError = () => {} }) {
    this.synthesize = synthesize
    this.play = play
    this.onSpeakingStart = onSpeakingStart
    this.onError = onError
    this.buffer = ''
    this.requestCount = 0
    this.nextPlayIndex = 0
    this.pending = new Map()
    this.playing = false
    this.first = true
    this.waiters = []
  }

  append(text) {
    this.buffer += text
    let extracted = extractPhrase(this.buffer, this.first)
    while (extracted) {
      this.queue(extracted.phrase)
      this.buffer = extracted.rest
      this.first = false
      extracted = extractPhrase(this.buffer, false)
    }
  }

  complete() {
    const remaining = flushPhrase(this.buffer)
    if (remaining) this.queue(remaining.phrase)
    this.buffer = ''
    this.finishIfIdle()
  }

  queue(text) {
    const index = this.requestCount++
    const state = { text, audio: null, ready: false }
    this.pending.set(index, state)
    Promise.resolve(this.synthesize(text))
      .then((audio) => {
        state.audio = audio
        state.ready = true
        return this.drain()
      })
      .catch((error) => this.onError(error))
  }

  async drain() {
    if (this.playing) return
    const state = this.pending.get(this.nextPlayIndex)
    if (!state || !state.ready) return this.finishIfIdle()
    this.playing = true
    if (this.nextPlayIndex === 0) this.onSpeakingStart()
    try {
      await this.play({ text: state.text, audio: state.audio })
    } finally {
      this.pending.delete(this.nextPlayIndex++)
      this.playing = false
      await this.drain()
    }
  }

  whenIdle() {
    if (!this.playing && this.pending.size === 0) return Promise.resolve()
    return new Promise((resolve) => this.waiters.push(resolve))
  }

  finishIfIdle() {
    if (this.playing || this.pending.size > 0) return
    this.waiters.splice(0).forEach((resolve) => resolve())
  }
}
```

- [ ] **Step 6: Run the pure module tests**

Run:

```powershell
npm.cmd test
```

Expected: PASS for phrase extraction and text-order playback.

- [ ] **Step 7: Commit the scheduling layer**

```powershell
git add prototypes/dh-live-guide/src/phraseChunker.mjs prototypes/dh-live-guide/src/speechPipeline.mjs prototypes/dh-live-guide/tests/phraseChunker.test.mjs prototypes/dh-live-guide/tests/speechPipeline.test.mjs
git commit -m "feat: schedule low latency avatar narration"
```

### Task 4: Connect Existing Chat Streaming and the DH_live WASM Audio Bridge

**Files:**
- Create: `prototypes/dh-live-guide/src/backendClient.mjs`
- Create: `prototypes/dh-live-guide/src/dhLiveAudioBridge.mjs`
- Create: `prototypes/dh-live-guide/tests/backendClient.test.mjs`
- Create: `prototypes/dh-live-guide/tests/dhLiveAudioBridge.test.mjs`

- [ ] **Step 1: Write failing SSE and avatar-audio client tests**

Create `prototypes/dh-live-guide/tests/backendClient.test.mjs`:

```js
import test from 'node:test'
import assert from 'node:assert/strict'
import { createBackendClient } from '../src/backendClient.mjs'

test('parses existing tourist SSE text frames and requests avatar wav audio', async () => {
  const requests = []
  const encoder = new TextEncoder()
  const client = createBackendClient('http://localhost:8000/api', async (url, options) => {
    requests.push({ url, options })
    if (url.endsWith('/tourist/chat/stream')) {
      return new Response(new ReadableStream({
        start(controller) {
          controller.enqueue(encoder.encode('data: {\"text\":\"欢迎\"}\\n\\ndata: {\"text\":\"来到灵山\"}\\n\\ndata: [DONE]\\n\\n'))
          controller.close()
        },
      }))
    }
    return new Response(new Uint8Array([82, 73, 70, 70]), {
      headers: { 'Content-Type': 'audio/wav' },
    })
  })

  const text = []
  for await (const chunk of client.streamAnswer({ message: '介绍灵山大佛' })) text.push(chunk)
  const audio = await client.synthesizeAvatar('欢迎来到灵山')

  assert.deepEqual(text, ['欢迎', '来到灵山'])
  assert.deepEqual([...audio], [82, 73, 70, 70])
  assert.equal(requests[1].url, 'http://localhost:8000/api/tourist/voice/avatar-tts')
})
```

- [ ] **Step 2: Write a failing bridge test for the renderer's supported audio path**

Create `prototypes/dh-live-guide/tests/dhLiveAudioBridge.test.mjs`:

```js
import test from 'node:test'
import assert from 'node:assert/strict'
import { createDhLiveAudioBridge } from '../src/dhLiveAudioBridge.mjs'

test('copies wav bytes into DH_live wasm before audible playback resolves', async () => {
  const written = []
  const module = {
    HEAPU8: { set(bytes, pointer) { written.push({ bytes: [...bytes], pointer }) } },
    _malloc() { return 32 },
    _setAudioBuffer(pointer, length) { written.push({ pointer, length }) },
    _free(pointer) { written.push({ freed: pointer }) },
  }
  class FakeAudioContext {
    decodeAudioData() { return Promise.resolve({ decoded: true }) }
    createBufferSource() {
      return {
        connect() {},
        start() { queueMicrotask(() => this.onended()) },
      }
    }
    get destination() { return {} }
  }

  const bridge = createDhLiveAudioBridge({ module, AudioContextClass: FakeAudioContext })
  await bridge.play(new Uint8Array([82, 73, 70, 70]))

  assert.deepEqual(written[0], { bytes: [82, 73, 70, 70], pointer: 32 })
  assert.deepEqual(written[1], { pointer: 32, length: 4 })
  assert.deepEqual(written[2], { freed: 32 })
})
```

- [ ] **Step 3: Run tests and confirm the client/bridge modules are absent**

Run:

```powershell
npm.cmd test
```

Expected: FAIL with `ERR_MODULE_NOT_FOUND` for `backendClient.mjs` or
`dhLiveAudioBridge.mjs`.

- [ ] **Step 4: Implement the existing-backend client**

Create `prototypes/dh-live-guide/src/backendClient.mjs`:

```js
export function createBackendClient(baseUrl, fetchImpl = fetch) {
  return {
    async *streamAnswer(payload, signal) {
      const response = await fetchImpl(`${baseUrl}/tourist/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal,
      })
      if (!response.ok || !response.body) throw new Error('对话服务暂不可用')
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      while (true) {
        const { value, done } = await reader.read()
        buffer += decoder.decode(value || new Uint8Array(), { stream: !done })
        const frames = buffer.split('\n\n')
        buffer = frames.pop() || ''
        for (const frame of frames) {
          const data = frame.replace(/^data:\s*/, '').trim()
          if (!data || data === '[DONE]') continue
          const parsed = JSON.parse(data)
          if (parsed.text) yield parsed.text
        }
        if (done) return
      }
    },

    async synthesizeAvatar(text, signal) {
      const response = await fetchImpl(`${baseUrl}/tourist/voice/avatar-tts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, voice: 'loongbella_v3' }),
        signal,
      })
      if (!response.ok) throw new Error('语音生成失败')
      return new Uint8Array(await response.arrayBuffer())
    },
  }
}
```

- [ ] **Step 5: Implement the audio-to-WASM bridge**

Create `prototypes/dh-live-guide/src/dhLiveAudioBridge.mjs`:

```js
export function createDhLiveAudioBridge({
  module,
  AudioContextClass = window.AudioContext || window.webkitAudioContext,
}) {
  const audioContext = new AudioContextClass()

  return {
    async play(bytes) {
      const pointer = module._malloc(bytes.byteLength)
      module.HEAPU8.set(bytes, pointer)
      module._setAudioBuffer(pointer, bytes.byteLength)
      module._free(pointer)

      const arrayBuffer = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength)
      const decoded = await audioContext.decodeAudioData(arrayBuffer)
      await new Promise((resolve) => {
        const source = audioContext.createBufferSource()
        source.buffer = decoded
        source.connect(audioContext.destination)
        source.onended = resolve
        source.start(0)
      })
    },
  }
}

export async function waitForDhLiveModule(scope = window, timeoutMs = 15000) {
  const started = Date.now()
  while (Date.now() - started < timeoutMs) {
    const module = scope.Module
    if (module?._malloc && module?._setAudioBuffer && module?.HEAPU8) return module
    await new Promise((resolve) => setTimeout(resolve, 80))
  }
  throw new Error('动态人物引擎加载超时')
}
```

- [ ] **Step 6: Run the prototype module suite**

Run:

```powershell
npm.cmd test
```

Expected: all four ES-module test files PASS.

- [ ] **Step 7: Commit client and bridge behavior**

```powershell
git add prototypes/dh-live-guide/src/backendClient.mjs prototypes/dh-live-guide/src/dhLiveAudioBridge.mjs prototypes/dh-live-guide/tests/backendClient.test.mjs prototypes/dh-live-guide/tests/dhLiveAudioBridge.test.mjs
git commit -m "feat: connect DH_live audio bridge"
```

### Task 5: Wire the Interactive Guide Sample and Document Local Use

**Files:**
- Create: `prototypes/dh-live-guide/src/app.mjs`
- Create: `prototypes/dh-live-guide/README.md`

- [ ] **Step 1: Implement the page controller over the tested units**

Create `prototypes/dh-live-guide/src/app.mjs`:

```js
import { createBackendClient } from './backendClient.mjs'
import { createDhLiveAudioBridge, waitForDhLiveModule } from './dhLiveAudioBridge.mjs'
import { SpeechPipeline } from './speechPipeline.mjs'

const apiBase = new URLSearchParams(location.search).get('api') || 'http://localhost:8000/api'
const client = createBackendClient(apiBase)
const form = document.getElementById('guide-form')
const input = document.getElementById('question')
const send = document.getElementById('send')
const messages = document.getElementById('messages')
const state = document.getElementById('metric-state')
const avatarStatus = document.getElementById('avatar-status')
const latency = document.getElementById('metric-latency')
let bridge
let activeController

setStatus('加载动态人物')
waitForDhLiveModule()
  .then((module) => {
    bridge = createDhLiveAudioBridge({ module })
    setStatus('待机')
  })
  .catch((error) => setStatus(error.message, true))

form.addEventListener('submit', async (event) => {
  event.preventDefault()
  if (!bridge || !input.value.trim()) return
  activeController?.abort()
  activeController = new AbortController()
  send.disabled = true
  latency.textContent = '--'
  appendMessage(input.value.trim(), 'user')
  const assistant = appendMessage('', 'assistant')
  const firstTextAt = { value: 0 }
  const pipeline = new SpeechPipeline({
    synthesize: (text) => client.synthesizeAvatar(text, activeController.signal),
    play: ({ audio }) => bridge.play(audio),
    onSpeakingStart: () => {
      setStatus('讲解中')
      latency.textContent = `${Date.now() - firstTextAt.value} ms`
    },
    onError: () => setStatus('语音生成失败', true),
  })

  try {
    setStatus('思考中')
    for await (const chunk of client.streamAnswer({ message: input.value.trim() }, activeController.signal)) {
      if (!firstTextAt.value) firstTextAt.value = Date.now()
      assistant.textContent += chunk
      pipeline.append(chunk)
    }
    pipeline.complete()
    await pipeline.whenIdle()
    setStatus('待机')
  } catch (error) {
    if (error.name !== 'AbortError') setStatus(error.message || '讲解失败', true)
  } finally {
    send.disabled = false
  }
})

function setStatus(label, failed = false) {
  state.textContent = label
  avatarStatus.textContent = label
  avatarStatus.classList.toggle('failed', failed)
}

function appendMessage(text, role) {
  const node = document.createElement('div')
  node.className = `message ${role}`
  node.textContent = text
  messages.appendChild(node)
  messages.scrollTop = messages.scrollHeight
  return node
}
```

- [ ] **Step 2: Document setup, licensing boundary and startup commands**

Create `prototypes/dh-live-guide/README.md`:

```markdown
# DH_live Guide Prototype

This local H5 prototype verifies audio-driven digital-human speech against the existing
scenic-guide backend. It does not replace the released mini-program page.

## Local-Only Assets

The `runtime/` directory is ignored by Git because it contains DH_live Web Demo files and a
branded demonstration character. Use it only for technical evaluation. A production release
requires licensed runtime terms and a legally usable female guide video/data package.

## Stage Runtime

```powershell
$sourceRepo = Join-Path $env:TEMP 'codex-dh-live-assessment-20260526'
if (-not (Test-Path (Join-Path $sourceRepo 'web_demo\static\js\DHLiveMini.js'))) {
    git clone --depth 1 https://github.com/kleinlee/DH_live.git $sourceRepo
}
& '.\scripts\stage-dh-live-runtime.ps1' -SourceStaticDir (Join-Path $sourceRepo 'web_demo\static')
```

## Run Tests

```powershell
npm.cmd test
```

## Start Backend

```powershell
cd 'D:\AI digital person\.worktrees\admin-backend-phase1\backend'
& 'D:\ProgramData\condaData\envs_dirs\dev_envs_1\python.exe' -m uvicorn app.main:app --reload --port 8000
```

## Start Prototype

```powershell
cd 'D:\AI digital person\.worktrees\admin-backend-phase1\prototypes\dh-live-guide'
& 'D:\ProgramData\condaData\envs_dirs\dev_envs_1\python.exe' -m http.server 58120
```

Open <http://localhost:58120/runtime/index.html>.
```

- [ ] **Step 3: Run all prototype tests and stage the local runtime**

Run:

```powershell
cd 'D:\AI digital person\.worktrees\admin-backend-phase1\prototypes\dh-live-guide'
npm.cmd test
$sourceRepo = Join-Path $env:TEMP 'codex-dh-live-assessment-20260526'
& '.\scripts\stage-dh-live-runtime.ps1' -SourceStaticDir (Join-Path $sourceRepo 'web_demo\static')
```

Expected: all tests PASS and `runtime/index.html` exists.

- [ ] **Step 4: Commit the interactive sample**

```powershell
git add prototypes/dh-live-guide/src/app.mjs prototypes/dh-live-guide/README.md
git commit -m "feat: add interactive DH_live guide sample"
```

### Task 6: Run Real Audio and Visual Acceptance Verification

**Files:**
- Verify: `backend/app/api/routers/tourist_voice.py`
- Verify: `prototypes/dh-live-guide/runtime/index.html`
- Verify: `prototypes/dh-live-guide/src/*.mjs`

- [ ] **Step 1: Run the focused automated regression suites**

Run:

```powershell
cd 'D:\AI digital person\.worktrees\admin-backend-phase1'
& 'D:\ProgramData\condaData\envs_dirs\dev_envs_1\python.exe' -m pytest backend\tests\test_tts_service.py backend\tests\test_tourist_voice_api.py -q
cd '.\prototypes\dh-live-guide'
npm.cmd test
```

Expected: both backend and H5 prototype tests PASS.

- [ ] **Step 2: Start backend and prototype static server**

Start backend:

```powershell
cd 'D:\AI digital person\.worktrees\admin-backend-phase1\backend'
& 'D:\ProgramData\condaData\envs_dirs\dev_envs_1\python.exe' -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Start sample in a second terminal:

```powershell
cd 'D:\AI digital person\.worktrees\admin-backend-phase1\prototypes\dh-live-guide'
& 'D:\ProgramData\condaData\envs_dirs\dev_envs_1\python.exe' -m http.server 58120
```

Expected: backend health responds and `http://localhost:58120/runtime/index.html` loads.

- [ ] **Step 3: Verify returned avatar speech is WAV at the required sampling rate**

Run a real short request while the backend is running:

```powershell
$body = @{ text = '欢迎来到灵山胜境，我带您开始游览。'; voice = 'loongbella_v3' } | ConvertTo-Json
Invoke-WebRequest -Uri 'http://127.0.0.1:8000/api/tourist/voice/avatar-tts' -Method Post -ContentType 'application/json' -Body $body -OutFile "$env:TEMP\dh-live-avatar-test.wav"
& 'D:\ProgramData\condaData\envs_dirs\dev_envs_1\python.exe' -c "import wave, os; p=os.path.join(os.environ['TEMP'], 'dh-live-avatar-test.wav'); w=wave.open(p, 'rb'); print(w.getnchannels(), w.getframerate()); assert w.getnchannels()==1 and w.getframerate()==16000"
```

Expected:

```text
1 16000
```

If CosyVoice does not return mono audio despite the requested WAV/16 kHz format, stop this
slice and add a separately approved conversion step; do not pass incompatible bytes into
DH_live.

- [ ] **Step 4: Open the prototype in the in-app browser and perform a real narration**

Open:

```text
http://localhost:58120/runtime/index.html
```

Submit:

```text
请介绍一下灵山大佛，并推荐接下来游览的方向。
```

Expected:

```text
- The demonstration character renders in the avatar panel.
- Text streams into the assistant message area.
- The status changes from 思考中 to 讲解中 to 待机.
- The mouth and facial animation visibly follow actual generated narration.
- The displayed 首段开口延迟 is less than 5000 ms under the local test conditions.
- Audio chunks play in narrative order without a multi-second gap between adjacent phrases.
```

- [ ] **Step 5: Check runtime logs and capture evidence**

Use the in-app browser to inspect page logs and take one screenshot while speaking.

Expected:

```text
- No uncaught error prevents rendering or audio playback.
- A screenshot shows the dynamic character and visible 讲解中 state.
```

Record any upstream non-blocking console warning separately; do not mistake a known demo
warning for a failed audio-to-renderer path if motion and audio function correctly.

- [ ] **Step 6: Run the unchanged mini-program build as a fallback regression check**

Run:

```powershell
cd 'D:\AI digital person\.worktrees\admin-backend-phase1\miniprogram'
npm.cmd run build:mp-weixin
```

Expected: PASS. No production mini-program source is required to change in this prototype
slice.

## Verification Summary

Run from `D:\AI digital person\.worktrees\admin-backend-phase1`:

```powershell
& 'D:\ProgramData\condaData\envs_dirs\dev_envs_1\python.exe' -m pytest backend\tests\test_tts_service.py backend\tests\test_tourist_voice_api.py -q
cd '.\prototypes\dh-live-guide'
npm.cmd test
cd '..\..\miniprogram'
npm.cmd run build:mp-weixin
```

Manual browser URL:

```text
http://localhost:58120/runtime/index.html
```

## Commit Boundary

Commit only the new backend compatibility endpoint, its tests, the prototype's own H5
source/tests/documentation, and the runtime staging script. Never stage
`prototypes/dh-live-guide/runtime/`, DH_live WASM, branded demonstration character media or
generated speech audio. After this sample is approved, create a separate specification for
licensed character preparation, HTTPS deployment, OSS/CDN resources and mini-program
`web-view` ownership.
