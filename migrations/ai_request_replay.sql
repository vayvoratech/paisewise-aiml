CREATE TABLE ai_request_replays (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id VARCHAR(255) NOT NULL UNIQUE,
    service_name VARCHAR(255) NOT NULL,
    model VARCHAR(255) NOT NULL,
    inputs JSONB NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_ai_request_replays_recorded_at
    ON ai_request_replays(recorded_at DESC);

CREATE INDEX idx_ai_request_replays_service_name
    ON ai_request_replays(service_name);