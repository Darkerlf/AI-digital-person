from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.services.tts_service import MouthCue, TTSSyncResult


class FakeTTSService:
    supports_remote_audio_url = False

    async def synthesize_sync(self, text: str, audio_dir: str, voice: str | None = None) -> TTSSyncResult:
        output_path = Path(audio_dir) / "tts_fake.mp3"
        output_path.write_bytes(b"fake-mp3")
        return TTSSyncResult(
            audio_path=str(output_path),
            duration_ms=600,
            mouth_cues=[
                MouthCue(start_ms=0, end_ms=120, mouth="closed"),
                MouthCue(start_ms=120, end_ms=240, mouth="mid"),
                MouthCue(start_ms=240, end_ms=600, mouth="closed"),
            ],
        )


class FakeFastTTSService:
    supports_remote_audio_url = True

    async def synthesize_sync_url(self, text: str, voice: str | None = None) -> TTSSyncResult:
        return TTSSyncResult(
            audio_path="https://dashscope-result.example/tts.mp3",
            duration_ms=600,
            mouth_cues=[
                MouthCue(start_ms=0, end_ms=120, mouth="closed"),
                MouthCue(start_ms=120, end_ms=240, mouth="mid"),
                MouthCue(start_ms=240, end_ms=600, mouth="closed"),
            ],
        )

    async def download_audio(self, audio_url: str) -> bytes:
        assert audio_url == "https://dashscope-result.example/tts.mp3"
        return b"remote-mp3"


class FakeASRService:
    async def recognize_from_file(self, audio_bytes: bytes, audio_format: str = "mp3") -> str:
        assert audio_bytes == b"fake-audio"
        assert audio_format == "mp3"
        return "灵山大佛在哪里"


class EmptyASRService:
    async def recognize_from_file(self, audio_bytes: bytes, audio_format: str = "mp3") -> str:
        return ""


class DisabledStorage:
    is_enabled = False


class FakeAvatarTTSService:
    async def synthesize_avatar_wav(self, text: str, voice: str | None = None) -> bytes:
        assert text == "欢迎来到灵山胜境"
        assert voice == "loongbella_v3"
        return b"RIFF-fake-avatar-wav"


def test_avatar_tts_returns_wav_bytes_for_dh_live(monkeypatch):
    from app.api.routers import tourist_voice

    monkeypatch.setattr(tourist_voice, "TTSService", FakeAvatarTTSService)
    client = TestClient(app)

    response = client.post(
        "/api/tourist/voice/avatar-tts",
        json={"text": "欢迎来到灵山胜境", "voice": "loongbella_v3"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("audio/wav")
    assert response.content == b"RIFF-fake-avatar-wav"


def test_avatar_tts_rejects_empty_text():
    client = TestClient(app)

    response = client.post("/api/tourist/voice/avatar-tts", json={"text": "  "})

    assert response.status_code == 400


def test_asr_endpoint_returns_recognized_text(monkeypatch):
    from app.api.routers import tourist_voice

    monkeypatch.setattr(tourist_voice, "ASRService", FakeASRService)
    client = TestClient(app)

    response = client.post(
        "/api/tourist/voice/asr",
        files={"audio": ("voice.mp3", b"fake-audio", "audio/mpeg")},
    )

    assert response.status_code == 200
    assert response.json() == {"text": "灵山大佛在哪里"}


def test_asr_endpoint_returns_empty_text_when_recognition_fails(monkeypatch):
    from app.api.routers import tourist_voice

    monkeypatch.setattr(tourist_voice, "ASRService", EmptyASRService)
    client = TestClient(app)

    response = client.post(
        "/api/tourist/voice/asr",
        files={"audio": ("voice.mp3", b"fake-audio", "audio/mpeg")},
    )

    assert response.status_code == 200
    assert response.json() == {"text": ""}


def test_asr_service_extracts_text_from_dashscope_sentence_payload():
    from app.services.asr_service import ASRService

    payload = {
        "output": {
            "sentence": [
                {"text": "灵山大佛"},
                {"text": "怎么走"},
            ]
        }
    }

    assert ASRService.extract_text(payload) == "灵山大佛怎么走"


def test_tts_sync_returns_audio_url_and_mouth_cues(monkeypatch):
    from app.api.routers import tourist_voice

    monkeypatch.setattr(tourist_voice, "TTSService", FakeTTSService)
    monkeypatch.setattr(tourist_voice, "get_object_storage", lambda: DisabledStorage())
    client = TestClient(app)

    response = client.post("/api/tourist/voice/tts-sync", json={"text": "欢迎来到灵山胜境"})

    assert response.status_code == 200
    data = response.json()
    assert data["duration_ms"] == 600
    assert data["audio_url"].endswith("/api/tourist/voice/tts/audio/tts_fake.mp3")
    assert data["mouth_cues"][1] == {"start_ms": 120, "end_ms": 240, "mouth": "mid"}
    assert all(cue["start_ms"] >= 0 for cue in data["mouth_cues"])
    assert all(cue["start_ms"] < cue["end_ms"] for cue in data["mouth_cues"])
    assert all(
        data["mouth_cues"][index]["end_ms"] <= data["mouth_cues"][index + 1]["start_ms"]
        for index in range(len(data["mouth_cues"]) - 1)
    )


def test_tts_sync_can_return_remote_audio_url_without_local_download(monkeypatch):
    from app.api.routers import tourist_voice

    monkeypatch.setattr(tourist_voice, "TTSService", FakeFastTTSService)
    monkeypatch.setattr(tourist_voice, "get_object_storage", lambda: DisabledStorage())
    client = TestClient(app)

    response = client.post("/api/tourist/voice/tts-sync", json={"text": "欢迎来到灵山胜境"})

    assert response.status_code == 200
    data = response.json()
    assert data["audio_url"] == "https://dashscope-result.example/tts.mp3"
    assert data["mouth_cues"][1] == {"start_ms": 120, "end_ms": 240, "mouth": "mid"}


def test_tts_sync_uploads_remote_audio_to_oss_when_enabled(monkeypatch):
    from app.api.routers import tourist_voice

    stored = []

    class FakeStorage:
        is_enabled = True

        def upload_bytes(self, data: bytes, *, filename: str, prefix: str, content_type: str | None = None):
            stored.append((data, filename, prefix, content_type))
            return type(
                "Stored",
                (),
                {"url": "https://digital-person-ai.oss-cn-beijing.aliyuncs.com/scenic-guide/tts/audio/tts.mp3"},
            )()

    monkeypatch.setattr(tourist_voice, "TTSService", FakeFastTTSService)
    monkeypatch.setattr(tourist_voice, "get_object_storage", lambda: FakeStorage())
    client = TestClient(app)

    response = client.post("/api/tourist/voice/tts-sync", json={"text": "娆㈣繋鏉ュ埌鐏靛北鑳滃"})

    assert response.status_code == 200
    assert response.json()["audio_url"] == "https://digital-person-ai.oss-cn-beijing.aliyuncs.com/scenic-guide/tts/audio/tts.mp3"
    assert stored == [(b"remote-mp3", "tts.mp3", "tts/audio", "audio/mpeg")]


def test_tts_audio_file_endpoint_returns_mp3(monkeypatch, tmp_path: Path):
    from app.api.routers import tourist_voice

    audio_path = tmp_path / "tts_test.mp3"
    audio_path.write_bytes(b"fake-mp3")
    monkeypatch.setattr(tourist_voice, "TTS_AUDIO_DIR", tmp_path)

    client = TestClient(app)
    response = client.get("/api/tourist/voice/tts/audio/tts_test.mp3")

    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/mpeg"
    assert response.content == b"fake-mp3"
