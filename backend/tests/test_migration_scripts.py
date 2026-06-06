from pathlib import Path


def test_admin_backend_gap_migration_script_covers_new_tables_and_columns() -> None:
    migration_path = Path("scripts/migrations/2026_06_04_admin_backend_gap_closure.sql")

    assert migration_path.exists()
    migration_sql = migration_path.read_text(encoding="utf-8").lower()
    assert "create table if not exists route_recommendation_record" in migration_sql
    assert "alter table scenic_spot" in migration_sql
    assert "cover_image_url" in migration_sql
    assert "guide_text" in migration_sql
    assert "target_audience" in migration_sql
    assert "extra_config_json" in migration_sql


def test_coordinate_calibration_migration_script_covers_scenic_spot_metadata() -> None:
    migration_path = Path("scripts/migrations/2026_06_05_scenic_spot_coordinate_calibration.sql")

    assert migration_path.exists()
    migration_sql = migration_path.read_text(encoding="utf-8").lower()
    assert "alter table scenic_spot" in migration_sql
    assert "coordinate_source" in migration_sql
    assert "coordinate_confidence" in migration_sql
    assert "coordinate_verified" in migration_sql
    assert "tencent_poi_id" in migration_sql
    assert "coordinate_raw_json" in migration_sql
