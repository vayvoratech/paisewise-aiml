CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    age SMALLINT NOT NULL,
    annual_income NUMERIC(15,2) NOT NULL,
    monthly_investment NUMERIC(15,2) NOT NULL,
    portfolio_value NUMERIC(15,2) NOT NULL,
    risk_profile VARCHAR(20) NOT NULL,
    investment_experience_years SMALLINT,
    sip_count INTEGER DEFAULT 0,
    kyc_completed BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS portfolio_holdings (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    company_name VARCHAR(150),
    quantity NUMERIC(18,4) NOT NULL,
    average_price NUMERIC(14,4) NOT NULL
);
