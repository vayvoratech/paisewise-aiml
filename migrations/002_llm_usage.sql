CREATE TABLE llm_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    model VARCHAR(255) NOT NULL,

    prompt_tokens INTEGER NOT NULL,
    completion_tokens INTEGER NOT NULL,
    thoughts_tokens INTEGER NOT NULL DEFAULT 0,
    tool_use_prompt_tokens INTEGER NOT NULL DEFAULT 0,
    total_tokens INTEGER NOT NULL,

    cost NUMERIC(12, 8) NOT NULL DEFAULT 0,

    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_llm_usage_recorded_at
ON llm_usage(recorded_at DESC);

CREATE INDEX idx_llm_usage_model_recorded_at
ON llm_usage(model, recorded_at DESC);