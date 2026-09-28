-- Task 5 official mutual-fund schema
-- Used by Task 12 recommendation engine.

CREATE TYPE mf_transaction_type AS ENUM (
    'PURCHASE',
    'REDEMPTION',
    'SIP',
    'SWITCH_IN',
    'SWITCH_OUT',
    'DIVIDEND'
);

CREATE TYPE mf_transaction_status AS ENUM (
    'PENDING',
    'SUBMITTED',
    'ALLOTTED',
    'REJECTED',
    'CANCELLED'
);

CREATE TYPE sip_status AS ENUM (
    'ACTIVE',
    'PAUSED',
    'CANCELLED',
    'COMPLETED'
);

CREATE TYPE sip_frequency AS ENUM (
    'MONTHLY',
    'WEEKLY',
    'QUARTERLY'
);


CREATE TABLE mf_schemes (
    scheme_code VARCHAR(20) PRIMARY KEY,
    isin VARCHAR(12) UNIQUE,
    scheme_name VARCHAR(300) NOT NULL,
    amc_name VARCHAR(100) NOT NULL,
    amc_code VARCHAR(20),

    category VARCHAR(50) NOT NULL,
    sub_category VARCHAR(50),

    scheme_type VARCHAR(20) NOT NULL
        CHECK (scheme_type IN ('Open Ended', 'Close Ended', 'Interval')),

    risk_level VARCHAR(20) NOT NULL
        CHECK (
            risk_level IN (
                'Low',
                'Low to Moderate',
                'Moderate',
                'Moderately High',
                'High',
                'Very High'
            )
        ),

    nav NUMERIC(12,4),
    nav_date DATE,

    min_sip_amount NUMERIC(10,2) NOT NULL DEFAULT 100,
    min_lumpsum NUMERIC(10,2) NOT NULL DEFAULT 1000,
    sip_multiplier NUMERIC(10,2) NOT NULL DEFAULT 1,

    returns_1y NUMERIC(8,4),
    returns_3y NUMERIC(8,4),
    returns_5y NUMERIC(8,4),
    returns_since_launch NUMERIC(8,4),

    benchmark_name VARCHAR(100),
    benchmark_returns_1y NUMERIC(8,4),

    expense_ratio NUMERIC(5,4),
    fund_manager VARCHAR(200),
    fund_size_cr NUMERIC(14,2),
    launch_date DATE,

    is_active BOOLEAN NOT NULL DEFAULT true,
    is_tax_saver BOOLEAN NOT NULL DEFAULT false,
    lock_in_years INTEGER NOT NULL DEFAULT 0,

    dividend_option BOOLEAN NOT NULL DEFAULT false,
    growth_option BOOLEAN NOT NULL DEFAULT true,

    bse_scheme_code VARCHAR(20),
    nse_symbol VARCHAR(20),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE mf_investments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL REFERENCES auth.users(id),
    scheme_code VARCHAR(20) NOT NULL
        REFERENCES mf_schemes(scheme_code),

    sip_id UUID,

    transaction_type mf_transaction_type NOT NULL,

    status mf_transaction_status NOT NULL DEFAULT 'PENDING',

    amount NUMERIC(12,2) NOT NULL
        CHECK (amount >= 100),

    nav_applied NUMERIC(12,4),
    units_allotted NUMERIC(14,4),

    folio_number VARCHAR(50),
    bse_order_id VARCHAR(50),
    bse_remarks TEXT,

    transaction_date DATE NOT NULL DEFAULT CURRENT_DATE,
    allotment_date DATE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE sips (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL REFERENCES auth.users(id),
    scheme_code VARCHAR(20) NOT NULL
        REFERENCES mf_schemes(scheme_code),

    goal_id UUID,

    frequency sip_frequency NOT NULL DEFAULT 'MONTHLY',

    amount NUMERIC(12,2) NOT NULL
        CHECK (amount >= 100),

    debit_day INTEGER NOT NULL
        CHECK (debit_day BETWEEN 1 AND 28),

    status sip_status NOT NULL DEFAULT 'ACTIVE',

    upi_mandate_id VARCHAR(100),
    upi_mandate_status VARCHAR(30),
    razorpay_subscription_id VARCHAR(100),

    start_date DATE NOT NULL,
    end_date DATE,
    next_debit_date DATE,

    installments_planned INTEGER,
    installments_done INTEGER NOT NULL DEFAULT 0,
    installments_failed INTEGER NOT NULL DEFAULT 0,

    total_invested NUMERIC(14,2) NOT NULL DEFAULT 0,
    total_units NUMERIC(14,4) NOT NULL DEFAULT 0,

    paused_at TIMESTAMPTZ,
    paused_reason TEXT,

    cancelled_at TIMESTAMPTZ,
    cancelled_reason TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- Link SIP-generated investments to their SIP mandate.
ALTER TABLE mf_investments
ADD CONSTRAINT fk_mf_investments_sips
FOREIGN KEY (sip_id)
REFERENCES sips(id)
ON DELETE SET NULL;


-- mf_schemes indexes

CREATE INDEX idx_mf_schemes_name
ON mf_schemes
USING gin (
    to_tsvector('english', scheme_name || ' ' || amc_name)
);

CREATE INDEX idx_mf_schemes_category
ON mf_schemes(category, risk_level)
WHERE is_active = true;

CREATE INDEX idx_mf_schemes_returns
ON mf_schemes(returns_1y DESC, returns_3y DESC)
WHERE is_active = true;

CREATE INDEX idx_mf_schemes_elss
ON mf_schemes(is_tax_saver)
WHERE is_tax_saver = true
AND is_active = true;


-- sips indexes

CREATE INDEX idx_sips_user_id
ON sips(user_id, status);

CREATE INDEX idx_sips_next_debit
ON sips(next_debit_date, status)
WHERE status = 'ACTIVE';

CREATE INDEX idx_sips_failed
ON sips(installments_failed)
WHERE status = 'ACTIVE'
AND installments_failed > 0;