CREATE TABLE recommendation_exposures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL
        REFERENCES auth.users(id)
        ON DELETE CASCADE,

    scheme_code VARCHAR(20) NOT NULL
        REFERENCES mf_schemes(scheme_code),

    amc_name VARCHAR(100) NOT NULL,

    recommendation_rank INTEGER NOT NULL
        CHECK (recommendation_rank > 0),

    recommendation_source VARCHAR(50) NOT NULL,

    recommended_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_recommendation_exposures_user_date
    ON recommendation_exposures(user_id, recommended_at DESC);

CREATE INDEX idx_recommendation_exposures_user_scheme_date
    ON recommendation_exposures(
        user_id,
        scheme_code,
        recommended_at DESC
    );

CREATE INDEX idx_recommendation_exposures_amc_date
    ON recommendation_exposures(
        amc_name,
        recommended_at DESC
    );