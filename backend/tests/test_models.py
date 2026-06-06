import subprocess
import sys

from app.core.database import Base
from app.models import load_all_models


def test_metadata_contains_phase1_tables() -> None:
    load_all_models()

    expected_tables = {
        "admin_user",
        "operation_log",
        "scenic_area",
        "scenic_spot",
        "scenic_spot_tag",
        "knowledge_document",
        "knowledge_chunk",
        "faq_item",
        "import_job",
        "import_job_item",
        "visitor_behavior_event",
        "dashboard_stat_daily",
        "feedback_record",
        "digital_human_config",
        "ai_provider_config",
        "visitor",
    }

    assert expected_tables.issubset(set(Base.metadata.tables))


def test_load_all_models_registers_visitor_without_app_import_side_effects() -> None:
    code = (
        "from app.core.database import Base; "
        "from app.models import load_all_models; "
        "load_all_models(); "
        "raise SystemExit(0 if 'visitor' in Base.metadata.tables else 1)"
    )

    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)

    assert result.returncode == 0, result.stderr
