-- Update claims status CHECK constraint to include approved + evidence statuses
-- Original constraint from 001_foundation.sql: ('pending', 'matched', 'unmatched', 'discarded')
-- Adding: 'approved', 'evidence' for the review workflow

ALTER TABLE claims DROP CONSTRAINT IF EXISTS claims_status_check;
ALTER TABLE claims ADD CONSTRAINT claims_status_check
    CHECK (status IN ('pending', 'matched', 'unmatched', 'discarded', 'approved', 'evidence'));
