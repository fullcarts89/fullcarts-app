-- Add evidence_tags column for evidence wall categorization
ALTER TABLE claims ADD COLUMN IF NOT EXISTS evidence_tags text[] DEFAULT '{}';

-- Index for filtering by evidence tag
CREATE INDEX IF NOT EXISTS idx_claims_evidence_tags ON claims USING GIN (evidence_tags);
