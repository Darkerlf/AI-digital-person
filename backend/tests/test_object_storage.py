from pathlib import Path

from app.utils.file_storage import store_upload
from app.utils.object_storage import ObjectStorage


def test_object_storage_builds_public_oss_url() -> None:
    storage = ObjectStorage(
        backend="oss",
        access_key_id="id",
        access_key_secret="secret",
        bucket_name="digital-person-ai",
        endpoint="oss-cn-beijing.aliyuncs.com",
        key_prefix="scenic-guide",
    )

    url = storage.build_public_url("scenic-guide/tts/audio/tts.mp3")

    assert url == "https://digital-person-ai.oss-cn-beijing.aliyuncs.com/scenic-guide/tts/audio/tts.mp3"


def test_object_storage_reads_environment_when_settings_are_empty(monkeypatch) -> None:
    monkeypatch.setenv("ALIYUN_OSS_ACCESS_KEY_ID", "id")
    monkeypatch.setenv("ALIYUN_OSS_ACCESS_KEY_SECRET", "secret")
    monkeypatch.setenv("ALIYUN_OSS_BUCKET", "digital-person-ai")
    monkeypatch.setenv("ALIYUN_OSS_ENDPOINT", "oss-cn-beijing.aliyuncs.com")

    storage = ObjectStorage(backend="oss")

    assert storage.is_enabled is True
    assert storage.build_public_url("sample.txt") == "https://digital-person-ai.oss-cn-beijing.aliyuncs.com/sample.txt"


def test_store_upload_falls_back_to_local_when_oss_is_disabled(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "guide.docx"
    source.write_bytes(b"docx")

    class DisabledStorage:
        is_enabled = False

    from app.utils import file_storage

    monkeypatch.setattr(file_storage, "UPLOAD_DIR", tmp_path / "uploads")
    monkeypatch.setattr(file_storage, "get_object_storage", lambda: DisabledStorage())

    stored = store_upload(source)

    assert stored.startswith(str(tmp_path / "uploads"))
    assert Path(stored).read_bytes() == b"docx"


def test_store_upload_uses_oss_when_configured(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "guide.docx"
    source.write_bytes(b"docx")
    calls = []

    class EnabledStorage:
        is_enabled = True

        def upload_file(self, source_path: Path, *, prefix: str, content_type: str | None = None):
            calls.append((source_path, prefix, content_type))
            return type("Stored", (), {"url": "https://digital-person-ai.oss-cn-beijing.aliyuncs.com/object.docx"})()

    from app.utils import file_storage

    monkeypatch.setattr(file_storage, "get_object_storage", lambda: EnabledStorage())

    stored = store_upload(source, prefix="imports/knowledge_document")

    assert stored == "https://digital-person-ai.oss-cn-beijing.aliyuncs.com/object.docx"
    assert calls == [(source, "imports/knowledge_document", None)]


def test_upload_file_to_key_uses_stable_object_key(tmp_path: Path) -> None:
    source = tmp_path / "base_halfbody.png"
    source.write_bytes(b"png")
    uploaded = []

    class FakeBucket:
        def put_object_from_file(self, key: str, filename: str, headers: dict[str, str]):
            uploaded.append((key, filename, headers))

    storage = ObjectStorage(
        backend="oss",
        access_key_id="id",
        access_key_secret="secret",
        bucket_name="digital-person-ai",
        endpoint="oss-cn-beijing.aliyuncs.com",
    )
    storage.bucket = lambda: FakeBucket()  # type: ignore[method-assign]

    result = storage.upload_file_to_key(source, key="scenic-guide/digital-human/base_halfbody.png")

    assert result.url == "https://digital-person-ai.oss-cn-beijing.aliyuncs.com/scenic-guide/digital-human/base_halfbody.png"
    assert uploaded == [
        (
            "scenic-guide/digital-human/base_halfbody.png",
            str(source),
            {"Content-Type": "image/png"},
        )
    ]
