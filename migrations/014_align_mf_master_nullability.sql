-- Task 12
-- Align mf_schemes nullability with the official AMFI master source.
-- These fields are not consistently supplied by AMFI.
-- Do not manufacture business values when the source is NULL.

ALTER TABLE mf_schemes
    ALTER COLUMN min_sip_amount DROP NOT NULL,
    ALTER COLUMN min_lumpsum DROP NOT NULL,
    ALTER COLUMN lock_in_years DROP NOT NULL;