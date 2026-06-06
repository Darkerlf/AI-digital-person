-- Scenic spot coordinate calibration metadata.
-- Target database: MySQL 8.x.

ALTER TABLE scenic_spot
    ADD COLUMN IF NOT EXISTS coordinate_source VARCHAR(50) NULL,
    ADD COLUMN IF NOT EXISTS coordinate_confidence INT NULL,
    ADD COLUMN IF NOT EXISTS coordinate_verified TINYINT(1) NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS tencent_poi_id VARCHAR(120) NULL,
    ADD COLUMN IF NOT EXISTS coordinate_address VARCHAR(500) NULL,
    ADD COLUMN IF NOT EXISTS coordinate_raw_json TEXT NULL;
