from __future__ import annotations

import io
import tempfile
from dataclasses import asdict
from pathlib import Path
from urllib.parse import urlparse

from fastapi import APIRouter, File as FastAPIFile, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from app.services.asr_service import ASRService
from app.services.tts_service import TTSService
from app.utils.object_storage import get_object_storage

router = APIRouter(prefix="/tourist/voice", tags=["tourist-voice"])

TTS_AUDIO_DIR = Path(tempfile.gettempdir()) / "scenic_tts_audio"


class TTSRequest(BaseModel):
    text: str
    voice: str | None = None


class MouthCueResponse(BaseModel):
    start_ms: int
    end_ms: int
    mouth: str


class TTSSyncResponse(BaseModel):
    audio_url: str
    duration_ms: int
    mouth_cues: list[MouthCueResponse]


@router.post("/tts")
async def text_to_speech(payload: TTSRequest):
    """Return an MP3 audio stream."""
    tts = TTSService()
    audio_bytes = await tts.synthesize(payload.text, voice=payload.voice)

    if not audio_bytes:
        return {"error": "Empty text"}

    return StreamingResponse(
        io.BytesIO(audio_bytes),
        media_type="audio/mpeg",
        headers={"Content-Disposition": "inline; filename=tts.mp3"},
    )


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


@router.post("/tts-sync", response_model=TTSSyncResponse)
async def text_to_speech_sync(payload: TTSRequest, request: Request):
    """Return synthesized audio URL plus a mouth-cue timeline for mini program lip sync."""
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")

    TTS_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    tts = TTSService()
    if tts.supports_remote_audio_url:
        result = await tts.synthesize_sync_url(payload.text, voice=payload.voice)
    else:
        result = await tts.synthesize_sync(payload.text, str(TTS_AUDIO_DIR), voice=payload.voice)

    audio_url = await publish_tts_audio(result.audio_path, request=request, tts=tts)

    return TTSSyncResponse(
        audio_url=audio_url,
        duration_ms=result.duration_ms,
        mouth_cues=[MouthCueResponse(**asdict(cue)) for cue in result.mouth_cues],
    )


async def publish_tts_audio(audio_path: str, *, request: Request, tts: TTSService) -> str:
    storage = get_object_storage()
    parsed = urlparse(audio_path)

    if storage.is_enabled:
        if parsed.scheme in {"http", "https"}:
            audio_bytes = await tts.download_audio(audio_path)
            filename = Path(parsed.path).name or "tts.mp3"
            return storage.upload_bytes(
                audio_bytes,
                filename=filename,
                prefix="tts/audio",
                content_type="audio/mpeg",
            ).url

        return storage.upload_file(
            Path(audio_path),
            prefix="tts/audio",
            content_type="audio/mpeg",
        ).url

    if parsed.scheme in {"http", "https"}:
        return audio_path

    filename = Path(audio_path).name
    return str(request.url_for("get_tts_audio_file", filename=filename))


@router.get("/tts/audio/{filename}", name="get_tts_audio_file")
def get_tts_audio_file(filename: str):
    safe_filename = Path(filename).name
    if safe_filename != filename or not safe_filename.startswith("tts_"):
        raise HTTPException(status_code=404, detail="Audio file not found")

    audio_path = TTS_AUDIO_DIR / safe_filename
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")

    return FileResponse(audio_path, media_type="audio/mpeg", filename=safe_filename)


@router.get("/tts/voices")
def list_voices():
    """Return available voices."""
    tts = TTSService()
    return {"voices": tts.list_voices()}


@router.post("/tts/file")
async def text_to_speech_file(payload: TTSRequest):
    """Return an MP3 file response for compatibility with older mini program clients."""
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")

    TTS_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    tts = TTSService()
    result = await tts.synthesize_sync(payload.text, str(TTS_AUDIO_DIR), voice=payload.voice)
    return FileResponse(result.audio_path, media_type="audio/mpeg", filename=Path(result.audio_path).name)


@router.post("/asr")
async def speech_to_text(audio: UploadFile = FastAPIFile(...)):
    """Receive an audio file and return recognized text."""
    audio_bytes = await audio.read()
    suffix = Path(audio.filename or "voice.mp3").suffix.lstrip(".") or "mp3"

    asr = ASRService()
    text = await asr.recognize_from_file(audio_bytes, suffix)

    return {"text": text}
