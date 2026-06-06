from __future__ import annotations

import mimetypes
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from app.core.config import settings


@dataclass(frozen=True)
class StoredObject:
    key: str
    url: str


class ObjectStorage:
    def __init__(
        self,
        *,
        backend: str | None = None,
        access_key_id: str | None = None,
        access_key_secret: str | None = None,
        bucket_name: str | None = None,
        endpoint: str | None = None,
        public_base_url: str | None = None,
        key_prefix: str | None = None,
    ) -> None:
        self.backend = (backend if backend is not None else settings.storage_backend).lower()
        self.access_key_id = access_key_id if access_key_id is not None else self.setting_value(
            settings.aliyun_oss_access_key_id,
            "ALIYUN_OSS_ACCESS_KEY_ID",
        )
        self.access_key_secret = access_key_secret if access_key_secret is not None else self.setting_value(
            settings.aliyun_oss_access_key_secret,
            "ALIYUN_OSS_ACCESS_KEY_SECRET",
        )
        self.bucket_name = bucket_name if bucket_name is not None else self.setting_value(
            settings.aliyun_oss_bucket,
            "ALIYUN_OSS_BUCKET",
        )
        self.endpoint = endpoint if endpoint is not None else self.setting_value(
            settings.aliyun_oss_endpoint,
            "ALIYUN_OSS_ENDPOINT",
        )
        self.public_base_url = public_base_url if public_base_url is not None else self.setting_value(
            settings.aliyun_oss_public_base_url,
            "ALIYUN_OSS_PUBLIC_BASE_URL",
        )
        raw_key_prefix = key_prefix if key_prefix is not None else self.setting_value(
            settings.aliyun_oss_key_prefix,
            "ALIYUN_OSS_KEY_PREFIX",
        )
        self.key_prefix = raw_key_prefix.strip("/")

    @staticmethod
    def setting_value(current_value: str, env_name: str) -> str:
        return current_value or os.getenv(env_name, "") or read_windows_user_env(env_name)

    @property
    def is_enabled(self) -> bool:
        if self.backend == "local":
            return False
        if self.backend not in {"auto", "oss"}:
            return False
        return all([self.access_key_id, self.access_key_secret, self.bucket_name, self.endpoint])

    def upload_file(self, source_path: Path, *, prefix: str = "uploads", content_type: str | None = None) -> StoredObject:
        key = self.build_key(source_path.name, prefix=prefix)
        return self.upload_file_to_key(source_path, key=key, content_type=content_type)

    def upload_file_to_key(self, source_path: Path, *, key: str, content_type: str | None = None) -> StoredObject:
        headers = self.build_headers(source_path.name, content_type)
        self.bucket().put_object_from_file(key, str(source_path), headers=headers)
        return StoredObject(key=key, url=self.build_public_url(key))

    def upload_bytes(
        self,
        data: bytes,
        *,
        filename: str,
        prefix: str = "uploads",
        content_type: str | None = None,
    ) -> StoredObject:
        key = self.build_key(filename, prefix=prefix)
        return self.upload_bytes_to_key(data, key=key, filename=filename, content_type=content_type)

    def upload_bytes_to_key(
        self,
        data: bytes,
        *,
        key: str,
        filename: str,
        content_type: str | None = None,
    ) -> StoredObject:
        headers = self.build_headers(filename, content_type)
        self.bucket().put_object(key, data, headers=headers)
        return StoredObject(key=key, url=self.build_public_url(key))

    def build_key(self, filename: str, *, prefix: str) -> str:
        suffix = Path(filename).suffix
        stem = Path(filename).stem or "file"
        today = datetime.now().strftime("%Y/%m/%d")
        parts = [self.key_prefix, prefix.strip("/"), today, f"{uuid4().hex}-{stem}{suffix}"]
        return "/".join(part for part in parts if part)

    def build_public_url(self, key: str) -> str:
        if self.public_base_url:
            base_url = self.public_base_url.rstrip("/")
        else:
            endpoint = self.endpoint.replace("https://", "").replace("http://", "").rstrip("/")
            base_url = f"https://{self.bucket_name}.{endpoint}"
        return f"{base_url}/{key.lstrip('/')}"

    def build_headers(self, filename: str, content_type: str | None = None) -> dict[str, str]:
        guessed = content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
        return {"Content-Type": guessed}

    def bucket(self):
        if not self.is_enabled:
            raise RuntimeError("Aliyun OSS storage is not configured")
        try:
            import oss2
        except ImportError as exc:
            raise RuntimeError("oss2 is required when Aliyun OSS storage is enabled") from exc

        auth = oss2.Auth(self.access_key_id, self.access_key_secret)
        return oss2.Bucket(auth, self.endpoint, self.bucket_name)


def get_object_storage() -> ObjectStorage:
    return ObjectStorage()


def read_windows_user_env(name: str) -> str:
    if os.name != "nt":
        return ""
    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            value, _ = winreg.QueryValueEx(key, name)
            return str(value)
    except OSError:
        return ""
