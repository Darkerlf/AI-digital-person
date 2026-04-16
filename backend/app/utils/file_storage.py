from pathlib import Path
import shutil
from uuid import uuid4


UPLOAD_DIR = Path(__file__).resolve().parents[3] / "uploads"


def save_upload(source_path: Path) -> Path:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    target_path = UPLOAD_DIR / f"{uuid4()}-{source_path.name}"
    shutil.copy2(source_path, target_path)
    return target_path
