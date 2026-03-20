-- Migration 044: Add "stretchflation" as an evidence wall tag
-- Stretchflation: same size package but less product inside (more air, filler, etc.)

-- Update the evidence_wall tag column's default comment to include the new tag
COMMENT ON COLUMN evidence_wall.tag IS
    'Evidence category tag: slack-fill, paper-thin, spot-the-difference, phantom-shrink, the-audacity, caught-in-4k, stretchflation';

-- No constraint change needed — the tag column is free-text (no CHECK constraint)
-- The frontend and admin UI just need to know the new tag name exists
