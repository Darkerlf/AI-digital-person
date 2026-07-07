from __future__ import annotations

import asyncio
import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path

import httpx
from pypinyin import Style, lazy_pinyin

from app.core.config import settings


MouthShape = str


@dataclass(frozen=True)
class MouthCue:
    start_ms: int
    end_ms: int
    mouth: MouthShape


@dataclass(frozen=True)
class TTSSyncResult:
    audio_path: str
    duration_ms: int
    mouth_cues: list[MouthCue]


VOICES = [
    {"short_name": "loongbella_v3", "label": "Bella v3 (female, precise guide)", "locale": "zh-CN", "gender": "Female"},
    {"short_name": "longanhuan", "label": "Longanhuan (female, warm energetic)", "locale": "zh-CN", "gender": "Female"},
    {"short_name": "longshuo_v3", "label": "Longshuo v3 (male, concise broadcast)", "locale": "zh-CN", "gender": "Male"},
    {"short_name": "longshu_v3", "label": "Longshu v3 (male, steady narration)", "locale": "zh-CN", "gender": "Male"},
    {"short_name": "Cherry", "label": "Cherry (female, warm)", "locale": "zh-CN", "gender": "Female"},
    {"short_name": "Serena", "label": "Serena (female, natural)", "locale": "zh-CN", "gender": "Female"},
    {"short_name": "Ethan", "label": "Ethan (male, natural)", "locale": "zh-CN", "gender": "Male"},
    {"short_name": "Chelsie", "label": "Chelsie (legacy OpenAI-compatible voice)", "locale": "multi", "gender": "Female"},
]

ROUND_CHARS = set("我哦喔窝握沃佛福无吴五乌湖呼护路入如圆游")
BIG_CHARS = set("啊呀哈大山胜景讲想强广高")
SMALL_CHARS = set("一衣以已的地得你里灵")
PAUSE_CHARS = set("，。！？；：,.!?;:、 \n\t")
BILABIAL_INITIALS = {"b", "p", "m"}
ROUND_FINAL_PREFIXES = ("u", "o", "uo", "ou", "ong", "iong", "ü", "v")
BIG_FINAL_PREFIXES = ("a", "ai", "an", "ang", "ao", "ia", "ian", "iang", "iao", "ua", "uan", "uang")
SMALL_FINAL_PREFIXES = ("i", "e", "ei", "en", "eng", "ie", "in", "ing", "ue", "ve")
PINYIN_INITIALS = (
    "zh",
    "ch",
    "sh",
    "b",
    "p",
    "m",
    "f",
    "d",
    "t",
    "n",
    "l",
    "g",
    "k",
    "h",
    "j",
    "q",
    "x",
    "r",
    "z",
    "c",
    "s",
    "y",
    "w",
)


class TTSService:
    def __init__(self) -> None:
        self.model = settings.tts_model
        self.default_voice = settings.tts_voice
        self.default_format = settings.tts_response_format
        self.generation_endpoint = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
        self.cosyvoice_endpoint = "https://dashscope.aliyuncs.com/api/v1/services/audio/tts/SpeechSynthesizer"

    @property
    def api_key(self) -> str:
        api_key = (
            os.getenv("DASHSCOPE_API_KEY")
            or os.getenv("DASHCOPE_API_KEY")
            or settings.dashscope_api_key
        )
        if not api_key:
            raise RuntimeError("DASHSCOPE_API_KEY is required for TTS synthesis")
        return api_key

    async def synthesize(self, text: str, voice: str | None = None) -> bytes:
        if not text or not text.strip():
            return b""

        audio_url = await self.create_dashscope_audio_url(text, voice=voice)
        return await self.download_audio(audio_url)

    async def synthesize_avatar_wav(self, text: str, voice: str | None = None) -> bytes:
        if not text or not text.strip():
            return b""
        if not self.uses_cosyvoice_http:
            raise RuntimeError("DH_live avatar speech requires a CosyVoice model")

        return await asyncio.to_thread(self._synthesize_avatar_wav_realtime, text, voice)

    def _synthesize_avatar_wav_realtime(self, text: str, voice: str | None = None) -> bytes:
        import dashscope
        from dashscope.audio.tts_v2 import AudioFormat, ResultCallback, SpeechSynthesizer

        class AudioCollector(ResultCallback):
            def __init__(self) -> None:
                self.chunks: list[bytes] = []
                self.error: object | None = None

            def on_data(self, data: bytes) -> None:
                self.chunks.append(data)

            def on_error(self, message: object) -> None:
                self.error = message

        dashscope.api_key = self.api_key
        collector = AudioCollector()
        synthesizer = SpeechSynthesizer(
            model=self.model,
            voice=voice or self.default_voice,
            format=AudioFormat.WAV_16000HZ_MONO_16BIT,
            language_hints=["zh"],
            callback=collector,
        )
        synthesizer.streaming_call(text)
        synthesizer.streaming_complete()

        if collector.error is not None:
            raise RuntimeError(f"DashScope realtime TTS request failed: {collector.error}")
        audio_bytes = b"".join(collector.chunks)
        if not audio_bytes:
            raise RuntimeError("DashScope realtime TTS returned empty audio")
        return self.normalize_wav_header(audio_bytes)

    def normalize_wav_header(self, audio_bytes: bytes) -> bytes:
        if len(audio_bytes) < 44 or audio_bytes[:4] != b"RIFF" or audio_bytes[8:12] != b"WAVE":
            return audio_bytes

        normalized = bytearray(audio_bytes)
        riff_size = len(normalized) - 8
        normalized[4:8] = riff_size.to_bytes(4, "little", signed=False)

        cursor = 12
        while cursor + 8 <= len(normalized):
            chunk_id = bytes(normalized[cursor:cursor + 4])
            chunk_size = int.from_bytes(normalized[cursor + 4:cursor + 8], "little", signed=False)
            data_start = cursor + 8
            if chunk_id == b"data":
                data_size = max(0, len(normalized) - data_start)
                normalized[cursor + 4:cursor + 8] = data_size.to_bytes(4, "little", signed=False)
                break
            if chunk_size <= 0:
                break
            cursor = data_start + chunk_size + (chunk_size % 2)

        return bytes(normalized)

    async def synthesize_to_file(self, text: str, output_path: str, voice: str | None = None) -> str:
        if not text or not text.strip():
            return output_path

        audio_bytes = await self.synthesize(text, voice=voice)
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(audio_bytes)
        return str(path)

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
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if self.uses_cosyvoice_http:
            headers["X-DashScope-SSE"] = "enable"

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(endpoint, headers=headers, json=payload)
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                raise RuntimeError(f"DashScope TTS request failed: {response.status_code} {response.text[:500]}") from exc

        if self.uses_cosyvoice_http:
            audio_url, words = self.extract_cosyvoice_result(response.text)
            if audio_url:
                return audio_url, words

        data = response.json()
        audio_url = data.get("output", {}).get("audio", {}).get("url")
        if not audio_url:
            raise RuntimeError(f"DashScope TTS response did not include output.audio.url: {data}")
        return audio_url, []

    def build_dashscope_generation_payload(self, text: str, voice: str | None = None) -> dict:
        return {
            "model": self.model,
            "input": {
                "text": text,
                "voice": voice or self.default_voice,
                "language_type": "Chinese",
            },
        }

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

    def extract_cosyvoice_result(self, body: str) -> tuple[str, list[dict]]:
        audio_url = ""
        words: list[dict] = []

        for payload in self.iter_dashscope_payloads(body):
            output = payload.get("output", {})
            audio = output.get("audio", {})
            if audio.get("url"):
                audio_url = audio["url"]
            sentence = output.get("sentence", {})
            for word in sentence.get("words") or []:
                text = word.get("text")
                begin_time = word.get("begin_time")
                end_time = word.get("end_time")
                if text is None or begin_time is None or end_time is None:
                    continue
                words.append(
                    {
                        "text": str(text),
                        "begin_time": int(begin_time),
                        "end_time": int(end_time),
                    }
                )

        if not audio_url:
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                data = {}
            output = data.get("output", {})
            audio_url = output.get("audio", {}).get("url", "")
            sentence = output.get("sentence", {})
            for word in sentence.get("words") or []:
                if {"text", "begin_time", "end_time"} <= set(word):
                    words.append(
                        {
                            "text": str(word["text"]),
                            "begin_time": int(word["begin_time"]),
                            "end_time": int(word["end_time"]),
                        }
                    )

        if not audio_url:
            raise RuntimeError(f"DashScope TTS response did not include output.audio.url: {body[:500]}")
        return audio_url, words

    def iter_dashscope_payloads(self, body: str) -> list[dict]:
        payloads = []
        for line in body.splitlines():
            line = line.strip()
            if not line.startswith("data:"):
                continue
            raw = line.removeprefix("data:").strip()
            if not raw or raw == "[DONE]":
                continue
            try:
                payloads.append(json.loads(raw))
            except json.JSONDecodeError:
                continue
        return payloads

    @property
    def uses_cosyvoice_http(self) -> bool:
        return self.model.lower().startswith("cosyvoice-")

    @property
    def supports_remote_audio_url(self) -> bool:
        return True

    async def download_audio(self, audio_url: str) -> bytes:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.get(audio_url)
            response.raise_for_status()
            return response.content

    async def synthesize_sync(self, text: str, audio_dir: str, voice: str | None = None) -> TTSSyncResult:
        normalized = text.strip()
        duration_ms = self.estimate_duration_ms(normalized)
        audio_dir_path = Path(audio_dir)
        filename = self.build_audio_filename(normalized, voice)
        audio_path = audio_dir_path / filename

        if normalized and not audio_path.exists():
            await self.synthesize_to_file(normalized, str(audio_path), voice=voice)

        return TTSSyncResult(
            audio_path=str(audio_path),
            duration_ms=duration_ms,
            mouth_cues=self.generate_mouth_cues(normalized, duration_ms),
        )

    async def synthesize_sync_url(self, text: str, voice: str | None = None) -> TTSSyncResult:
        normalized = text.strip()
        audio_url, words = await self.create_dashscope_tts_result(normalized, voice=voice)
        duration_ms = self.duration_from_words(words) or self.estimate_duration_ms(normalized)
        return TTSSyncResult(
            audio_path=audio_url,
            duration_ms=duration_ms,
            mouth_cues=self.generate_phoneme_mouth_cues(words, duration_ms, fallback_text=normalized),
        )

    def duration_from_words(self, words: list[dict]) -> int | None:
        end_times = [int(word["end_time"]) for word in words if word.get("end_time") is not None]
        if not end_times:
            return None
        return max(600, max(end_times) + 120)

    def generate_phoneme_mouth_cues(
        self,
        words: list[dict],
        duration_ms: int,
        fallback_text: str = "",
    ) -> list[MouthCue]:
        valid_words = [
            word for word in words
            if word.get("text") and word.get("begin_time") is not None and word.get("end_time") is not None
        ]
        if not valid_words:
            return self.generate_mouth_cues(fallback_text, duration_ms)

        raw_cues: list[MouthCue] = [MouthCue(start_ms=0, end_ms=1, mouth="closed")]
        for word in self.expand_timestamp_words(valid_words):
            text = str(word["text"])
            start_ms = max(0, int(word["begin_time"]))
            end_ms = max(start_ms + 1, int(word["end_time"]))
            if text in PAUSE_CHARS:
                raw_cues.append(MouthCue(start_ms=start_ms, end_ms=end_ms, mouth="closed"))
                continue

            initial, final = self.split_pinyin(text)
            if initial in BILABIAL_INITIALS and end_ms - start_ms >= 80:
                initial_end = min(end_ms - 1, start_ms + max(35, int((end_ms - start_ms) * 0.32)))
                raw_cues.append(MouthCue(start_ms=start_ms, end_ms=initial_end, mouth="closed"))
                raw_cues.append(MouthCue(start_ms=initial_end, end_ms=end_ms, mouth=self.map_final_to_mouth(final, text)))
            else:
                raw_cues.append(MouthCue(start_ms=start_ms, end_ms=end_ms, mouth=self.map_final_to_mouth(final, text)))

        if raw_cues[-1].end_ms < duration_ms:
            raw_cues.append(MouthCue(start_ms=raw_cues[-1].end_ms, end_ms=duration_ms, mouth="closed"))
        elif raw_cues[-1].mouth != "closed":
            previous = raw_cues[-1]
            close_start = max(previous.start_ms + 1, previous.end_ms - min(80, previous.end_ms - previous.start_ms))
            raw_cues[-1] = MouthCue(start_ms=previous.start_ms, end_ms=close_start, mouth=previous.mouth)
            raw_cues.append(MouthCue(start_ms=close_start, end_ms=max(close_start + 1, duration_ms), mouth="closed"))

        return self.merge_mouth_cues(raw_cues, duration_ms)

    def expand_timestamp_words(self, words: list[dict]) -> list[dict]:
        expanded: list[dict] = []
        for word in words:
            text = str(word.get("text") or "")
            begin_time = word.get("begin_time")
            end_time = word.get("end_time")
            if not text or begin_time is None or end_time is None:
                continue

            start_ms = int(begin_time)
            end_ms = max(start_ms + 1, int(end_time))
            chars = list(text)
            if len(chars) <= 1:
                expanded.append({"text": text, "begin_time": start_ms, "end_time": end_ms})
                continue

            span = end_ms - start_ms
            for index, char in enumerate(chars):
                char_start = start_ms + int(span * index / len(chars))
                char_end = start_ms + int(span * (index + 1) / len(chars))
                expanded.append(
                    {
                        "text": char,
                        "begin_time": char_start,
                        "end_time": max(char_start + 1, char_end),
                    }
                )
        return expanded

    def split_pinyin(self, text: str) -> tuple[str, str]:
        syllable = lazy_pinyin(text[:1], style=Style.NORMAL, errors="ignore")
        if not syllable:
            return "", ""
        pinyin = syllable[0].replace("ü", "v")
        for initial in PINYIN_INITIALS:
            if pinyin.startswith(initial) and len(pinyin) > len(initial):
                return initial, pinyin[len(initial):]
        return "", pinyin

    def map_final_to_mouth(self, final: str, char: str) -> MouthShape:
        if char in ROUND_CHARS or final.startswith(ROUND_FINAL_PREFIXES):
            return "round"
        if char in BIG_CHARS or final.startswith(BIG_FINAL_PREFIXES):
            return "big"
        if char in SMALL_CHARS or final.startswith(SMALL_FINAL_PREFIXES):
            return "small"
        return "mid"

    def merge_mouth_cues(self, cues: list[MouthCue], duration_ms: int) -> list[MouthCue]:
        merged: list[MouthCue] = []
        for cue in sorted(cues, key=lambda item: (item.start_ms, item.end_ms)):
            start_ms = max(0, min(cue.start_ms, duration_ms))
            end_ms = max(start_ms + 1, min(cue.end_ms, duration_ms))
            normalized = MouthCue(start_ms=start_ms, end_ms=end_ms, mouth=cue.mouth)
            if merged and merged[-1].mouth == normalized.mouth and normalized.start_ms - merged[-1].end_ms <= 20:
                previous = merged[-1]
                merged[-1] = MouthCue(start_ms=previous.start_ms, end_ms=normalized.end_ms, mouth=previous.mouth)
            else:
                if merged and normalized.start_ms < merged[-1].end_ms:
                    normalized = MouthCue(
                        start_ms=merged[-1].end_ms,
                        end_ms=max(merged[-1].end_ms + 1, normalized.end_ms),
                        mouth=normalized.mouth,
                    )
                if normalized.start_ms < normalized.end_ms:
                    merged.append(normalized)

        filtered: list[MouthCue] = []
        for cue in merged:
            if filtered and cue.end_ms - cue.start_ms < 35:
                previous = filtered[-1]
                filtered[-1] = MouthCue(start_ms=previous.start_ms, end_ms=cue.end_ms, mouth=previous.mouth)
                continue
            filtered.append(cue)

        if not filtered:
            return [MouthCue(start_ms=0, end_ms=max(120, duration_ms), mouth="closed")]
        filtered[0] = MouthCue(start_ms=0, end_ms=filtered[0].end_ms, mouth=filtered[0].mouth)
        if filtered[-1].mouth != "closed":
            previous = filtered[-1]
            close_start = max(previous.start_ms + 1, previous.end_ms - 80)
            filtered[-1] = MouthCue(start_ms=previous.start_ms, end_ms=close_start, mouth=previous.mouth)
            filtered.append(MouthCue(start_ms=close_start, end_ms=duration_ms, mouth="closed"))
        else:
            filtered[-1] = MouthCue(start_ms=filtered[-1].start_ms, end_ms=duration_ms, mouth="closed")
        return [cue for cue in filtered if cue.start_ms < cue.end_ms]

    def generate_mouth_cues(self, text: str, duration_ms: int) -> list[MouthCue]:
        duration_ms = max(120, int(duration_ms))
        speakable_chars = [char for char in text.strip() if char not in PAUSE_CHARS]
        if not speakable_chars:
            return [MouthCue(start_ms=0, end_ms=duration_ms, mouth="closed")]

        frame_count = max(3, min(80, len(speakable_chars) + 2))
        frame_ms = max(80, duration_ms // frame_count)
        cues: list[MouthCue] = [MouthCue(start_ms=0, end_ms=min(frame_ms, duration_ms), mouth="closed")]

        cursor = cues[-1].end_ms
        for index, char in enumerate(speakable_chars):
            if cursor >= duration_ms:
                break
            end_ms = min(duration_ms, cursor + frame_ms)
            mouth = self.map_char_to_mouth(char, index)
            cues.append(MouthCue(start_ms=cursor, end_ms=end_ms, mouth=mouth))
            cursor = end_ms

        if cues[-1].end_ms < duration_ms:
            cues.append(MouthCue(start_ms=cues[-1].end_ms, end_ms=duration_ms, mouth="closed"))
        elif cues[-1].mouth != "closed":
            previous = cues[-1]
            split_ms = max(previous.start_ms + 1, previous.end_ms - min(120, frame_ms))
            cues[-1] = MouthCue(start_ms=previous.start_ms, end_ms=split_ms, mouth=previous.mouth)
            cues.append(MouthCue(start_ms=split_ms, end_ms=duration_ms, mouth="closed"))

        return [cue for cue in cues if cue.start_ms < cue.end_ms]

    def map_char_to_mouth(self, char: str, index: int) -> MouthShape:
        if char in ROUND_CHARS:
            return "round"
        if char in BIG_CHARS:
            return "big"
        if char in SMALL_CHARS:
            return "small"
        return "mid" if index % 3 else "big"

    def estimate_duration_ms(self, text: str) -> int:
        speakable_count = sum(1 for char in text if char not in PAUSE_CHARS)
        pause_count = sum(1 for char in text if char in PAUSE_CHARS)
        return max(600, min(60_000, speakable_count * 180 + pause_count * 120 + 300))

    def build_audio_filename(self, text: str, voice: str | None = None) -> str:
        digest = hashlib.sha256(f"{self.model}|{voice or self.default_voice}|{text}".encode("utf-8")).hexdigest()[:20]
        return f"tts_{digest}.{self.default_format}"

    def list_voices(self) -> list[dict]:
        return VOICES
