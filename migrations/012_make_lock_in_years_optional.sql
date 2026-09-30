-- Task 12
-- AMFI master data does not reliably provide lock-in years.
-- Keep the column for downstream use, but allow the source value to be NULL.

ALTER TABLE mf_schemes
ALTER COLUMN lock_in_years DROP NOT NULL;