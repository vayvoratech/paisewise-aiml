CREATE TABLE fraud_cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    order_id UUID NOT NULL,

    fraud_score DOUBLE PRECISION,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING_REVIEW',

    reviewer_decision VARCHAR(50),

    reviewed_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_fraud_cases_order
        FOREIGN KEY (order_id)
        REFERENCES practice.orders(id),

    CONSTRAINT chk_fraud_cases_status
        CHECK (
            status IN (
                'PENDING_REVIEW',
                'TRUE_FRAUD',
                'FALSE_POSITIVE'
            )
        ),

    CONSTRAINT chk_fraud_cases_reviewer_decision
        CHECK (
            reviewer_decision IS NULL
            OR reviewer_decision IN (
                'TRUE_FRAUD',
                'FALSE_POSITIVE'
            )
        ),

    CONSTRAINT chk_fraud_cases_score
        CHECK (
            fraud_score IS NULL
            OR (
                fraud_score >= 0
                AND fraud_score <= 1
            )
        )
);

CREATE UNIQUE INDEX idx_fraud_cases_order_id
ON fraud_cases(order_id);


CREATE INDEX idx_fraud_cases_status
ON fraud_cases(status);

CREATE INDEX idx_fraud_cases_created_at
ON fraud_cases(created_at DESC);

CREATE INDEX idx_fraud_cases_pending_review
ON fraud_cases(created_at DESC)
WHERE status = 'PENDING_REVIEW';