-- Task 12
-- Riskometer is no longer used by the recommendation engine.
-- Keep the legacy column for compatibility, but allow it to be empty.

ALTER TABLE mf_schemes
ALTER COLUMN risk_level DROP NOT NULL;