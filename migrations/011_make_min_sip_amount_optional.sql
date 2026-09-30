-- Task 12
-- AMFI master data does not reliably provide a minimum SIP amount.
-- Keep the column for downstream use, but allow the source value to be NULL.

ALTER TABLE mf_schemes
ALTER COLUMN min_sip_amount DROP NOT NULL;