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
    }

    assert expected_tables.issubset(set(Base.metadata.tables))
