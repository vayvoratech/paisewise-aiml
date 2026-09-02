

CREATE TABLE IF NOT EXISTS recommendation_runs (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    experiment_name VARCHAR(100) NOT NULL,
    variant VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS recommendation_clicks (
    id BIGSERIAL PRIMARY KEY,
    recommendation_run_id BIGINT NOT NULL REFERENCES recommendation_runs(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    scheme_code VARCHAR(20) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_recommendation_runs_user_created
    ON recommendation_runs(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_recommendation_clicks_run
    ON recommendation_clicks(recommendation_run_id, created_at DESC);
