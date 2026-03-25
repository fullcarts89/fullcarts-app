-- Migration 048: Add "not-as-advertised" as an evidence wall tag
-- Not as Advertised: product claims a certain weight on the label but weighs less

COMMENT ON COLUMN evidence_wall.tag IS
    'Evidence category tag: slack-fill, paper-thin, spot-the-difference, phantom-shrink, the-audacity, caught-in-4k, stretchflation, not-as-advertised';
