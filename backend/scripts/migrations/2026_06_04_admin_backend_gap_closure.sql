-- Admin backend gap-closure migration.
-- Target database: MySQL 8.x.
-- Run this after the initial schema exists. Review column existence first on older MySQL versions
-- because ADD COLUMN IF NOT EXISTS is not available in all 8.x deployments.

ALTER TABLE scenic_spot
    ADD COLUMN IF NOT EXISTS latitude DOUBLE NULL,
    ADD COLUMN IF NOT EXISTS longitude DOUBLE NULL,
    ADD COLUMN IF NOT EXISTS cover_image_url VARCHAR(500) NULL,
    ADD COLUMN IF NOT EXISTS guide_text TEXT NULL,
    ADD COLUMN IF NOT EXISTS target_audience VARCHAR(255) NULL,
    ADD COLUMN IF NOT EXISTS suggested_duration_minutes INT NULL;

ALTER TABLE ai_provider_config
    ADD COLUMN IF NOT EXISTS extra_config_json JSON NULL;

ALTER TABLE knowledge_document
    ADD COLUMN IF NOT EXISTS status VARCHAR(20) NOT NULL DEFAULT 'active',
    ADD COLUMN IF NOT EXISTS version INT NOT NULL DEFAULT 1;

CREATE TABLE IF NOT EXISTS route_recommendation_record (
    id INT AUTO_INCREMENT PRIMARY KEY,
    scenic_area_id INT NULL,
    visitor_id VARCHAR(100) NULL,
    session_id VARCHAR(100) NULL,
    source VARCHAR(50) NOT NULL DEFAULT 'route_template',
    duration_minutes INT NULL,
    matched_template_id INT NULL,
    matched_template_name VARCHAR(255) NULL,
    fallback_used TINYINT(1) NOT NULL DEFAULT 0,
    request_json JSON NOT NULL,
    response_json JSON NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_route_recommendation_record_scenic_area
        FOREIGN KEY (scenic_area_id) REFERENCES scenic_area(id)
);

CREATE INDEX IF NOT EXISTS ix_route_recommendation_record_scenic_area_id
    ON route_recommendation_record (scenic_area_id);
CREATE INDEX IF NOT EXISTS ix_route_recommendation_record_visitor_id
    ON route_recommendation_record (visitor_id);
CREATE INDEX IF NOT EXISTS ix_route_recommendation_record_session_id
    ON route_recommendation_record (session_id);
CREATE INDEX IF NOT EXISTS ix_route_recommendation_record_matched_template_id
    ON route_recommendation_record (matched_template_id);

CREATE TABLE IF NOT EXISTS feedback_record (
    id INT AUTO_INCREMENT PRIMARY KEY,
    scenic_area_id INT NULL,
    source_type VARCHAR(50) NULL,
    source_id INT NULL,
    sentiment VARCHAR(20) NULL,
    score DOUBLE NULL,
    content TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_feedback_record_scenic_area
        FOREIGN KEY (scenic_area_id) REFERENCES scenic_area(id)
);

CREATE INDEX IF NOT EXISTS ix_feedback_record_scenic_area_id ON feedback_record (scenic_area_id);
