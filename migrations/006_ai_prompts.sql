CREATE TABLE ai_prompts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    prompt_key VARCHAR(255) NOT NULL,
    version INTEGER NOT NULL,
    prompt_text TEXT NOT NULL,

    is_active BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_ai_prompts_key_version
        UNIQUE (prompt_key, version)
);

CREATE UNIQUE INDEX uq_ai_prompts_active_key
    ON ai_prompts(prompt_key)
    WHERE is_active = TRUE;

CREATE INDEX idx_ai_prompts_key
    ON ai_prompts(prompt_key);

CREATE INDEX idx_ai_prompts_active
    ON ai_prompts(prompt_key, is_active);