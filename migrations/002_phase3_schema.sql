CREATE TABLE IF NOT EXISTS chat_feedback (
    id BIGSERIAL PRIMARY KEY,
    response_id VARCHAR(100) NOT NULL,
    user_id VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    feedback VARCHAR(10) NOT NULL CHECK (feedback IN ('up', 'down')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chat_feedback_created ON chat_feedback(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_feedback_category ON chat_feedback(category, created_at DESC);

CREATE TABLE IF NOT EXISTS user_churn_scores (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    score NUMERIC(8,6) NOT NULL,
    computed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_churn_scores_user ON user_churn_scores(user_id, computed_at DESC);

CREATE TABLE IF NOT EXISTS model_versions (
    id BIGSERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    version VARCHAR(100) NOT NULL,
    dataset_version VARCHAR(100) NOT NULL,
    metrics JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
