# WeChat Mini Program Digital Human Lip Sync Design

## Goal

Deploy the existing split PNG digital human assets into the tourist WeChat mini program and synchronize generated TTS audio with mouth shapes.

## Scope

- Use `digital_human_split_assets` as the visual source for the mini program.
- Keep Alibaba Cloud DashScope credentials on the FastAPI backend only.
- Add a backend TTS sync endpoint that returns playable audio plus a mouth cue timeline.
- Drive the mini program avatar by image layers: base/expression, blink overlay, and mouth overlay.
- Support both local WeChat Developer Tools testing and production HTTPS deployment.

## Architecture

The backend calls DashScope through the OpenAI-compatible client with `qwen3-tts-instruct-flash`. It stores generated MP3 files under the OS temp directory and exposes a public URL from the same API host. After synthesis, it estimates audio duration and builds a simple viseme timeline from answer text. This is intentionally heuristic for MVP quality and can later be replaced by phoneme or audio-energy analysis without changing the mini program API contract.

The mini program requests `/api/tourist/voice/tts-sync` after receiving an assistant answer. It plays the returned audio with `InnerAudioContext` and updates `DigitalHuman.vue` on a timer by comparing elapsed playback time with `mouth_cues`.

## API

`POST /api/tourist/voice/tts-sync`

Request:

```json
{
  "text": "欢迎来到灵山胜境",
  "voice": "Chelsie"
}
```

Response:

```json
{
  "audio_url": "http://127.0.0.1:8000/api/tourist/voice/tts/audio/tts_x.mp3",
  "duration_ms": 1800,
  "mouth_cues": [
    { "start_ms": 0, "end_ms": 120, "mouth": "closed" },
    { "start_ms": 120, "end_ms": 240, "mouth": "mid" }
  ]
}
```

## Security

The API key is read from `DASHSCOPE_API_KEY` or the existing `dashscope_api_key` setting. The key must not be committed to code, `.env.example`, or mini program files. The currently exposed key should be rotated in Alibaba Cloud.

## Local And Production Deployment

Local development uses a LAN backend URL for WeChat Developer Tools. Production requires an HTTPS API domain configured in WeChat public platform request/download legal domains. The mini program API base URL remains centralized in utility files so it can be swapped for production builds.
