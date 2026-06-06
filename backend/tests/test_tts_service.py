from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import anyio
import pytest

from app.services.tts_service import MouthCue, TTSService
from app.services import tts_service as tts_module


class TestTTSService:
    def test_generate_mouth_cues_covers_duration_and_known_shapes(self):
        service = TTSService()

        cues = service.generate_mouth_cues("我在灵山大佛等你。", duration_ms=1200)

        assert cues[0].mouth == "closed"
        assert cues[-1].end_ms == 1200
        assert cues[-1].mouth == "closed"
        assert {cue.mouth for cue in cues} >= {"closed", "round", "big", "mid"}
        assert all(cue.start_ms < cue.end_ms for cue in cues)

    def test_generate_mouth_cues_returns_closed_for_empty_text(self):
        service = TTSService()

        cues = service.generate_mouth_cues("", duration_ms=800)

        assert cues == [MouthCue(start_ms=0, end_ms=800, mouth="closed")]

    def test_default_tts_model_uses_cosyvoice_builtin_voice(self):
        service = TTSService()

        assert service.model == "cosyvoice-v3-flash"
        assert service.default_voice == "loongbella_v3"
        assert service.uses_cosyvoice_http is True
        assert service.supports_remote_audio_url is True

    def test_dashscope_tts_does_not_fall_back_to_openai_api_key(self, monkeypatch):
        monkeypatch.delenv("DASHSCOPE_API_KEY", raising=False)
        monkeypatch.delenv("DASHCOPE_API_KEY", raising=False)
        monkeypatch.setenv("OPENAI_API_KEY", "old-openai-key")
        monkeypatch.setattr(tts_module.settings, "dashscope_api_key", "")
        service = TTSService()

        with pytest.raises(RuntimeError, match="DASHSCOPE_API_KEY"):
            _ = service.api_key

    def test_cosyvoice_payload_uses_http_tts_synthesizer_fields(self):
        service = TTSService()

        payload = service.build_cosyvoice_payload("欢迎来到灵山胜境", voice=None)

        assert payload["model"] == "cosyvoice-v3-flash"
        assert payload["input"]["text"] == "欢迎来到灵山胜境"
        assert payload["input"]["voice"] == "loongbella_v3"
        assert payload["input"]["format"] == "mp3"
        assert payload["input"]["sample_rate"] == 24000
        assert payload["input"]["language_hints"] == ["zh"]
        assert payload["input"]["word_timestamp_enabled"] is True
        assert "language_type" not in payload["input"]

    def test_avatar_payload_requests_dh_live_compatible_wav_audio(self):
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

    def test_avatar_audio_rejects_models_that_cannot_request_wav_16khz(self):
        service = TTSService()
        service.model = "qwen3-tts-instruct-flash"

        async def run_test():
            with pytest.raises(RuntimeError, match="CosyVoice"):
                await service.synthesize_avatar_wav("欢迎来到灵山胜境")

        anyio.run(run_test)

    def test_avatar_audio_uses_realtime_wav_synthesis_instead_of_url_download(self, monkeypatch):
        service = TTSService()
        called: dict[str, str | None] = {}

        def fake_realtime_synthesis(text: str, voice: str | None = None) -> bytes:
            called["text"] = text
            called["voice"] = voice
            return b"RIFF-realtime-wav"

        async def fail_non_realtime_path(*args, **kwargs):
            raise AssertionError("avatar speech must not use the non-realtime URL path")

        monkeypatch.setattr(service, "_synthesize_avatar_wav_realtime", fake_realtime_synthesis, raising=False)
        monkeypatch.setattr(service, "create_dashscope_audio_url", fail_non_realtime_path)

        async def run_test():
            audio = await service.synthesize_avatar_wav("欢迎来到灵山胜境", voice="loongbella_v3")
            assert audio == b"RIFF-realtime-wav"

        anyio.run(run_test)
        assert called == {"text": "欢迎来到灵山胜境", "voice": "loongbella_v3"}

    def test_extract_cosyvoice_result_from_sse_payload(self):
        service = TTSService()
        sse_text = "\n".join(
            [
                'data: {"output":{"sentence":{"words":[{"text":"欢","begin_time":0,"end_time":160}]}}}',
                "",
                'data: {"output":{"audio":{"url":"https://dashscope-result.example/tts.mp3"},"sentence":{"words":[{"text":"迎","begin_time":160,"end_time":320}]}}}',
                "",
            ]
        )

        audio_url, words = service.extract_cosyvoice_result(sse_text)

        assert audio_url == "https://dashscope-result.example/tts.mp3"
        assert words == [
            {"text": "欢", "begin_time": 0, "end_time": 160},
            {"text": "迎", "begin_time": 160, "end_time": 320},
        ]

    def test_generate_phoneme_mouth_cues_uses_word_timestamps(self):
        service = TTSService()
        words = [
            {"text": "我", "begin_time": 0, "end_time": 220},
            {"text": "佛", "begin_time": 220, "end_time": 460},
            {"text": "山", "begin_time": 460, "end_time": 700},
            {"text": "灵", "begin_time": 700, "end_time": 940},
        ]

        cues = service.generate_phoneme_mouth_cues(words, duration_ms=1000)

        assert cues[0] == MouthCue(start_ms=0, end_ms=1, mouth="closed")
        assert cues[-1].end_ms == 1000
        assert cues[-1].mouth == "closed"
        assert "round" in {cue.mouth for cue in cues}
        assert "big" in {cue.mouth for cue in cues}
        assert "small" in {cue.mouth for cue in cues}
        assert all(cues[index].end_ms <= cues[index + 1].start_ms for index in range(len(cues) - 1))

    def test_generate_phoneme_mouth_cues_falls_back_without_timestamps(self):
        service = TTSService()

        cues = service.generate_phoneme_mouth_cues([], duration_ms=800, fallback_text="灵山")

        assert cues == service.generate_mouth_cues("灵山", 800)

    def test_generate_phoneme_mouth_cues_splits_multi_character_timestamp_words(self):
        service = TTSService()
        words = [
            {"text": "灵山大佛", "begin_time": 0, "end_time": 800},
        ]

        cues = service.generate_phoneme_mouth_cues(words, duration_ms=920)

        non_closed = [cue for cue in cues if cue.mouth != "closed"]
        mouths = [cue.mouth for cue in non_closed]
        assert "small" in mouths
        assert "big" in mouths
        assert "round" in mouths
        assert mouths.index("small") < mouths.index("round")
        assert any(cue.mouth == "round" and cue.start_ms >= 560 for cue in non_closed)
        assert cues[-1].mouth == "closed"
        assert cues[-1].start_ms <= 840
        assert cues[-1].end_ms == 920

    def test_cosyvoice_audio_filename_includes_model_and_voice(self):
        service = TTSService()

        default_name = service.build_audio_filename("欢迎来到灵山胜境")
        other_voice_name = service.build_audio_filename("欢迎来到灵山胜境", voice="longanhuan")

        assert default_name.startswith("tts_")
        assert default_name.endswith(".mp3")
        assert default_name != other_voice_name

    def test_qwen_generation_payload_keeps_language_type_for_legacy_model(self):
        service = TTSService()
        service.model = "qwen3-tts-instruct-flash"

        payload = service.build_dashscope_generation_payload("欢迎来到灵山胜境", voice="Cherry")

        assert payload["model"] == "qwen3-tts-instruct-flash"
        assert payload["input"] == {
            "text": "欢迎来到灵山胜境",
            "voice": "Cherry",
            "language_type": "Chinese",
        }

    def test_synthesize_to_file_uses_dashscope_qwen_tts_http_api(self, tmp_path: Path):
        output_path = tmp_path / "tts.mp3"
        create_response = MagicMock()
        create_response.json.return_value = {
            "output": {
                "audio": {
                    "url": "https://dashscope-result.example/audio.wav",
                },
            },
        }
        create_response.raise_for_status.return_value = None
        audio_response = MagicMock()
        audio_response.content = b"mp3-bytes"
        audio_response.raise_for_status.return_value = None

        async def run_test():
            with patch("app.services.tts_service.httpx.AsyncClient") as MockClient:
                mock_client = MagicMock()
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=None)
                mock_client.post = AsyncMock(return_value=create_response)
                mock_client.get = AsyncMock(return_value=audio_response)
                MockClient.return_value = mock_client
                service = TTSService()
                service.model = "qwen3-tts-instruct-flash"

                result = await service.synthesize_to_file("欢迎来到灵山胜境", str(output_path), voice="Cherry")
                return result, service, mock_client

        result, service, mock_client = anyio.run(run_test)

        assert result == str(output_path)
        assert output_path.read_bytes() == b"mp3-bytes"
        mock_client.post.assert_awaited_once()
        post_kwargs = mock_client.post.await_args.kwargs
        assert post_kwargs["json"]["model"] == service.model
        assert post_kwargs["json"]["input"]["text"] == "欢迎来到灵山胜境"
        assert post_kwargs["json"]["input"]["voice"] == "Cherry"
        assert post_kwargs["json"]["input"]["language_type"] == "Chinese"
        mock_client.get.assert_awaited_once_with("https://dashscope-result.example/audio.wav")

    def test_synthesize_sync_url_skips_backend_audio_download(self):
        create_response = MagicMock()
        create_response.json.return_value = {
            "output": {
                "audio": {
                    "url": "https://dashscope-result.example/audio.wav",
                },
            },
        }
        create_response.raise_for_status.return_value = None

        async def run_test():
            with patch("app.services.tts_service.httpx.AsyncClient") as MockClient:
                mock_client = MagicMock()
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=None)
                mock_client.post = AsyncMock(return_value=create_response)
                mock_client.get = AsyncMock()
                MockClient.return_value = mock_client
                service = TTSService()
                service.model = "qwen3-tts-instruct-flash"

                result = await service.synthesize_sync_url("欢迎来到灵山胜境", voice="Cherry")
                return result, mock_client

        result, mock_client = anyio.run(run_test)

        assert result.audio_path == "https://dashscope-result.example/audio.wav"
        assert result.duration_ms > 0
        assert result.mouth_cues
        mock_client.post.assert_awaited_once()
        mock_client.get.assert_not_called()

    def test_synthesize_sync_url_uses_cosyvoice_sse_word_timestamps(self):
        create_response = MagicMock()
        create_response.text = "\n".join(
            [
                'data: {"output":{"sentence":{"words":[{"text":"佛","begin_time":0,"end_time":240}]}}}',
                "",
                'data: {"output":{"audio":{"url":"https://dashscope-result.example/cosy.mp3"},"sentence":{"words":[{"text":"山","begin_time":240,"end_time":480}]}}}',
                "",
            ]
        )
        create_response.raise_for_status.return_value = None

        async def run_test():
            with patch("app.services.tts_service.httpx.AsyncClient") as MockClient:
                mock_client = MagicMock()
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=None)
                mock_client.post = AsyncMock(return_value=create_response)
                mock_client.get = AsyncMock()
                MockClient.return_value = mock_client
                service = TTSService()

                result = await service.synthesize_sync_url("佛山")
                return result, mock_client

        result, mock_client = anyio.run(run_test)

        assert result.audio_path == "https://dashscope-result.example/cosy.mp3"
        assert result.duration_ms == 600
        assert {"round", "big"} <= {cue.mouth for cue in result.mouth_cues}
        post_kwargs = mock_client.post.await_args.kwargs
        assert post_kwargs["headers"]["X-DashScope-SSE"] == "enable"
        assert post_kwargs["json"]["input"]["word_timestamp_enabled"] is True
        mock_client.get.assert_not_called()
