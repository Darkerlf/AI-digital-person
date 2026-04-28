import io

import edge_tts


VOICES = [
    {"short_name": "zh-CN-XiaoxiaoNeural", "label": "晓晓（女，温柔）", "locale": "zh-CN", "gender": "Female"},
    {"short_name": "zh-CN-YunxiNeural", "label": "云希（男，阳光）", "locale": "zh-CN", "gender": "Male"},
    {"short_name": "zh-CN-YunjianNeural", "label": "云健（男，沉稳）", "locale": "zh-CN", "gender": "Male"},
    {"short_name": "zh-CN-XiaoyiNeural", "label": "晓艺（女，活泼）", "locale": "zh-CN", "gender": "Female"},
    {"short_name": "zh-TW-HsiaoChenNeural", "label": "晓晨（台湾女声）", "locale": "zh-TW", "gender": "Female"},
    {"short_name": "zh-HK-HiuGaaiNeural", "label": "晓佳（粤语女声）", "locale": "zh-HK", "gender": "Female"},
]


class TTSService:
    def __init__(self, default_voice: str = "zh-CN-XiaoxiaoNeural") -> None:
        self.default_voice = default_voice

    async def synthesize(self, text: str, voice: str | None = None) -> bytes:
        if not text or not text.strip():
            return b""

        voice = voice or self.default_voice
        communicate = edge_tts.Communicate(text, voice)

        audio_buffer = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk.type == "audio":
                audio_buffer.write(chunk.data)

        return audio_buffer.getvalue()

    async def synthesize_to_file(self, text: str, output_path: str, voice: str | None = None) -> str:
        if not text or not text.strip():
            return output_path

        voice = voice or self.default_voice
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
        return output_path

    def list_voices(self) -> list[dict]:
        return VOICES
