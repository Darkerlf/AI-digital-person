from pathlib import Path
import shutil
from uuid import uuid4

from app.utils.object_storage import get_object_storage


UPLOAD_DIR = Path(__file__).resolve().parents[3] / "uploads"


def save_upload(source_path: Path) -> Path:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    target_path = UPLOAD_DIR / f"{uuid4()}-{source_path.name}"
    shutil.copy2(source_path, target_path)
    return target_path


def store_upload(source_path: Path, *, prefix: str = "uploads") -> str:
    storage = get_object_storage()
    if storage.is_enabled:
        return storage.upload_file(source_path, prefix=prefix).url
    return str(save_upload(source_path))
