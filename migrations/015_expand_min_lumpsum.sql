-- Task 12
-- AMFI contains legitimate minimum lump-sum values above
-- the original numeric(10,2) capacity.
-- Preserve the source value without truncation.

ALTER TABLE mf_schemes
ALTER COLUMN min_lumpsum TYPE NUMERIC(14,2);