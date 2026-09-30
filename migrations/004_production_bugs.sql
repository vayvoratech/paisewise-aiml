CREATE TABLE production_bugs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bug_id VARCHAR(255) NOT NULL UNIQUE,
    service_name VARCHAR(255) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    detected_at TIMESTAMPTZ NOT NULL,
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_production_bugs_detected_at
    ON production_bugs(detected_at DESC);

CREATE INDEX idx_production_bugs_service_name
    ON production_bugs(service_name);