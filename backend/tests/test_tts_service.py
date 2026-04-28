from unittest.mock import AsyncMock, patch, MagicMock
import pytest

from app.services.tts_service import TTSService


@pytest.fixture
def tts_service():
    return TTSService()


class TestTTSService:
    @pytest.mark.asyncio
    async def test_synthesize_returns_audio_bytes(self, tts_service):
        mock_audio = b'\x00' * 100

        with patch("edge_tts.Communicate") as MockCommunicate:
            mock_instance = MagicMock()
            MockCommunicate.return_value = mock_instance

            async def fake_stream():
                chunk = MagicMock()
                chunk.type = "audio"
                chunk.data = mock_audio
                yield chunk
            mock_instance.stream.return_value = fake_stream()

            result = await tts_service.synthesize("你好")
        assert isinstance(result, bytes)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_synthesize_empty_text_returns_empty(self, tts_service):
        result = await tts_service.synthesize("")
        assert result == b""

    @pytest.mark.asyncio
    async def test_synthesize_uses_correct_voice(self, tts_service):
        with patch("edge_tts.Communicate") as MockCommunicate:
            mock_instance = MagicMock()
            MockCommunicate.return_value = mock_instance

            async def fake_stream():
                return
                yield
            mock_instance.stream.return_value = fake_stream()

            await tts_service.synthesize("测试", voice="zh-CN-YunxiNeural")
            MockCommunicate.assert_called_once()
            call_kwargs = MockCommunicate.call_args
            assert call_kwargs[0][1] == "zh-CN-YunxiNeural" or call_kwargs[1].get("voice") == "zh-CN-YunxiNeural"

    def test_default_voice_is_xiaoxiao(self, tts_service):
        assert tts_service.default_voice == "zh-CN-XiaoxiaoNeural"

    def test_list_voices_returns_chinese_voices(self, tts_service):
        voices = tts_service.list_voices()
        assert len(voices) > 0
        assert all(v["locale"].startswith("zh-") for v in voices)
        assert any(v["short_name"] == "zh-CN-XiaoxiaoNeural" for v in voices)
