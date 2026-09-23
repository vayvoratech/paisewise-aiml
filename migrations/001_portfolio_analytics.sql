CREATE TABLE portfolio_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL REFERENCES auth.users(id),

    snapshot_date DATE NOT NULL,

    analytics_data JSONB NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_portfolio_analytics_user_date
        UNIQUE (user_id, snapshot_date)
);

CREATE INDEX idx_portfolio_analytics_user_date
    ON portfolio_analytics(user_id, snapshot_date DESC);