-- Task 12
-- AMFI category names can exceed the original 50-character limit.
-- Preserve the official category value without truncation.

ALTER TABLE mf_schemes
ALTER COLUMN category TYPE VARCHAR(100);