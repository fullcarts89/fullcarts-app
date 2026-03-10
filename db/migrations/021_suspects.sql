-- FullCarts: Suspect Practices table
-- For deceptive packaging, labeling tricks, and sketchy brand behavior
-- that doesn't meet strict shrinkflation criteria but deserves public attention.

CREATE TABLE suspects (
    id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    brand               TEXT NOT NULL,
    product_name        TEXT,
    description         TEXT NOT NULL,
    suspect_type        TEXT NOT NULL
        CHECK (suspect_type IN (
            'deceptive_labeling', 'packaging_tricks',
            'ingredient_swap', 'other'
        )),
    evidence_summary    JSONB NOT NULL DEFAULT '{}',
    evidence_urls       TEXT[] DEFAULT '{}',
    severity            TEXT NOT NULL DEFAULT 'moderate'
        CHECK (severity IN ('minor', 'moderate', 'major')),
    status              TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'published', 'retracted')),
    source_raw_item_id  UUID REFERENCES raw_items(id),
    source_candidate_id UUID REFERENCES change_candidates(id),
    flagged_by          UUID REFERENCES auth.users(id),
    flagged_at          TIMESTAMPTZ DEFAULT now() NOT NULL,
    published_at        TIMESTAMPTZ,
    published_by        UUID REFERENCES auth.users(id),
    retracted_at        TIMESTAMPTZ,
    retracted_by        UUID REFERENCES auth.users(id),
    retraction_reason   TEXT,
    created_at          TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at          TIMESTAMPTZ DEFAULT now() NOT NULL
);

CREATE INDEX idx_suspects_brand ON suspects (lower(brand));
CREATE INDEX idx_suspects_status ON suspects (status);
CREATE INDEX idx_suspects_type ON suspects (suspect_type);
CREATE INDEX idx_suspects_flagged_at ON suspects (flagged_at DESC);
