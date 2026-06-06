# DH_live Guide Prototype

This local H5 prototype verifies audio-driven digital-human speech against the existing
scenic-guide backend. It does not replace the released mini-program page.

## Speech Path

The prototype uses `POST /api/tourist/voice/avatar-tts`, which calls CosyVoice realtime
speech synthesis and returns mono 16 kHz WAV bytes for the DH_live renderer. The native
mini-program `/tts-sync` path remains unchanged.

Narration releases the first informative clause early, then prefetches at most one
subsequent segment while the current segment plays. This keeps the initial mouth response
quick and avoids opening many simultaneous TTS sessions against the account rate limit.

The demonstration video has only one looping motion track. To avoid a permanently
"speaking" expression while silent, the prototype captures one neutral rendered frame at
startup and displays it during idle/thinking states; it reveals the DH_live motion layer
only while speech audio is playing.

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

## Generate Female Guide Assets

The female guide package is generated from
`digital_human_new/万相 2.7_1779867680842.mp4` and the local checkpoint files under
`DH_live/checkpoint`. The generated runtime files are ignored by Git and copied into
`runtime/assets/`.

DH_live's current preprocessing script still calls the older `mediapipe.solutions` API.
If assets need to be regenerated, use `mediapipe==0.10.21` for the preprocessing run and
then restore the normal app environment afterward.

```powershell
$tool = Join-Path $env:TEMP 'codex-dh-live-tools-20260528'
$outRoot = Join-Path $env:TEMP 'codex-dh-live-female-guide-output'
$env:PATH = (Join-Path $env:TEMP 'codex-ffmpeg-bin') + ';' + $env:PATH

& 'D:\ProgramData\condaData\envs_dirs\dev_envs_1\python.exe' `
  (Join-Path $tool 'data_preparation_mini.py') `
  (Join-Path $env:TEMP 'codex-female-guide-neutral.mp4') `
  $outRoot `
  --resize

& 'D:\ProgramData\condaData\envs_dirs\dev_envs_1\python.exe' `
  (Join-Path $tool 'data_preparation_web.py') `
  $outRoot

Copy-Item (Join-Path $outRoot 'assets\01.mp4') '.\runtime\assets\01.mp4' -Force
Copy-Item (Join-Path $outRoot 'assets\combined_data.json.gz') '.\runtime\assets\combined_data.json.gz' -Force
Copy-Item (Join-Path $outRoot 'assets\thumbnail.jpg') '.\runtime\assets\thumbnail.jpg' -Force
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

For a quick latency check, enter `门票多少钱`: the diagnostics panel shows the interval
from first answer text to the beginning of avatar narration. The validated local run
reported `1096 ms`.
