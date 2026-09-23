CREATE TABLE IF NOT EXISTS sip_coach_reports (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    report_text TEXT NOT NULL,
    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sip_coach_reports_user_id
ON sip_coach_reports(user_id, generated_at DESC);

ALTER TABLE user_features ADD COLUMN IF NOT EXISTS feature_version VARCHAR(30) DEFAULT 'v1';
