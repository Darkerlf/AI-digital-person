import io
import tempfile
import os

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.tts_service import TTSService

router = APIRouter(prefix="/tourist/voice", tags=["tourist-voice"])


class TTSRequest(BaseModel):
    text: str
    voice: str | None = None


@router.post("/tts")
async def text_to_speech(payload: TTSRequest):
    """返回 MP3 音频流"""
    tts = TTSService()
    audio_bytes = await tts.synthesize(payload.text, voice=payload.voice)

    if not audio_bytes:
        return {"error": "Empty text"}

    return StreamingResponse(
        io.BytesIO(audio_bytes),
        media_type="audio/mpeg",
        headers={"Content-Disposition": "inline; filename=tts.mp3"},
    )


@router.get("/tts/voices")
def list_voices():
    """返回可用音色列表"""
    tts = TTSService()
    return {"voices": tts.list_voices()}


@router.post("/tts/file")
async def text_to_speech_file(payload: TTSRequest):
    """返回音频文件路径（用于小程序播放）"""
    tts = TTSService()

    tmp_dir = tempfile.gettempdir()
    filename = f"tts_{hash(payload.text) & 0xFFFFFFFF:08x}.mp3"
    output_path = os.path.join(tmp_dir, filename)

    if not os.path.exists(output_path):
        await tts.synthesize_to_file(payload.text, output_path, voice=payload.voice)

    return FileResponse(output_path, media_type="audio/mpeg", filename=filename)
