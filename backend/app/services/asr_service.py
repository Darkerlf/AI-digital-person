"""Speech recognition service backed by DashScope Paraformer."""
from __future__ import annotations

import asyncio
import tempfile
from http import HTTPStatus
from pathlib import Path

from app.core.config import settings


class ASRService:
    """Speech recognition service using DashScope local-file recognition."""

    def __init__(self) -> None:
        self.api_key = settings.dashscope_api_key
        self.model = "paraformer-realtime-v2"
        self.sample_rate = 16000

    async def recognize_from_file(self, audio_bytes: bytes, audio_format: str = "mp3") -> str:
        if not audio_bytes or not self.api_key:
            return ""

        suffix = f".{audio_format.lower().lstrip('.') or 'mp3'}"
        tmp_path = ""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name
            return await asyncio.to_thread(self._recognize_local_file, tmp_path, audio_format)
        except Exception:
            return ""
        finally:
            if tmp_path:
                try:
                    Path(tmp_path).unlink(missing_ok=True)
                except OSError:
                    pass

    def _recognize_local_file(self, file_path: str, audio_format: str) -> str:
        import dashscope
        from dashscope.audio.asr import Recognition

        dashscope.api_key = self.api_key
        recognition = Recognition(
            model=self.model,
            format=audio_format,
            sample_rate=self.sample_rate,
            language_hints=["zh", "en"],
            callback=None,
        )
        result = recognition.call(file_path)
        status_code = getattr(result, "status_code", None)
        if status_code != HTTPStatus.OK and status_code != 200:
            return ""
        return self.extract_text(result)

    @staticmethod
    def extract_text(result) -> str:
        if hasattr(result, "get_sentence"):
            sentence = result.get_sentence()
            if isinstance(sentence, list):
                return "".join(str(item.get("text", "")) for item in sentence if isinstance(item, dict)).strip()
            if isinstance(sentence, dict):
                return str(sentence.get("text", "")).strip()

        output = getattr(result, "output", None)
        if output is None and isinstance(result, dict):
            output = result.get("output")

        if isinstance(output, dict):
            if isinstance(output.get("text"), str):
                return output["text"].strip()
            sentence = output.get("sentence") or output.get("sentences")
            if isinstance(sentence, list):
                return "".join(str(item.get("text", "")) for item in sentence if isinstance(item, dict)).strip()
            if isinstance(sentence, dict):
                return str(sentence.get("text", "")).strip()

        return ""

    async def recognize_simple(self, audio_path: str) -> str:
        path = Path(audio_path)
        if not path.exists():
            return ""
        return await self.recognize_from_file(path.read_bytes(), path.suffix.lstrip(".") or "mp3")
