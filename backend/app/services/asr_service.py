"""语音识别服务 — 使用 DashScope Paraformer 模型"""
import httpx
import json

from app.core.config import settings


class ASRService:
    """语音识别服务，使用阿里云 DashScope Paraformer 实时语音识别"""

    def __init__(self) -> None:
        self.api_key = settings.dashscope_api_key
        self.model = "paraformer-realtime-v2"

    async def recognize_from_file(self, audio_bytes: bytes, audio_format: str = "mp3") -> str:
        """从音频文件识别文字（非实时）"""
        if not audio_bytes:
            return ""

        try:
            return await self._recognize_with_dashscope(audio_bytes, audio_format)
        except Exception:
            return ""

    async def _recognize_with_dashscope(self, audio_bytes: bytes, audio_format: str) -> str:
        """调用 DashScope 语音识别"""
        # 预留接口 — 实际项目中应接入 DashScope Paraformer 文件转写 API
        # https://dashscope.aliyuncs.com/api/v1/services/audio/asr/transcription
        # 当前为骨架实现，返回空字符串
        return ""

    async def recognize_simple(self, audio_path: str) -> str:
        """简化版识别 — 预留接口"""
        return ""
