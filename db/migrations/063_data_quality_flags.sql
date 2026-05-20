-- Migration 063: data quality flags (quarantine queue)
--
-- Soft-flag table for pipeline detectors. The pattern: when a script
-- notices a suspect row (short brand name, stuck approved claim, fuzzy
-- brand collision, etc.) it writes a flag pointing at the offending
-- claim / entity / event rather than mutating the underlying row.
-- An admin reviews the flag and either fixes the data (via the existing
-- retract / edit / merge tools) or marks the flag resolved.
--
-- Why a soft-flag queue instead of in-line mutation:
--   - Detectors stay read-only against the data they're auditing.
--   - Mistaken auto-fixes don't corrupt the catalog.
--   - The admin gets a single review surface for everything the
--     pipeline thinks is wrong, with reason + severity + detail.
--   - History is preserved (`detected_at` / `resolved_at` form an
--     audit trail per flag).
--
-- A row points at exactly ONE of claim_id / entity_id / event_id.
-- Idempotency: re-running a detector against the same data must not
-- create a duplicate flag while the original is still open. The
-- partial unique index enforces that — only un-resolved flags count
-- for collision detection.

BEGIN;

CREATE TABLE data_quality_flags (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,

    -- Exactly one of these three is non-null. The CHECK below enforces it.
    claim_id        UUID REFERENCES claims(id) ON DELETE CASCADE,
    entity_id       UUID REFERENCES product_entities(id) ON DELETE CASCADE,
    event_id        UUID REFERENCES published_changes(id) ON DELETE CASCADE,

    -- Free-form label per detector. Examples in this migration:
    --   'short_brand'           — brand name suspiciously short / placeholder
    --   'stuck_approved_claim'  — claim has been matched without entity link too long
    --   'fuzzy_brand_collision' — same product under multiple brand strings
    flag_kind       TEXT NOT NULL,

    severity        TEXT NOT NULL CHECK (severity IN ('low', 'med', 'high')),

    -- Detector-specific payload. The pipeline writes whatever helps the
    -- admin decide what to do (e.g. {"brand": "Poor", "claim_count": 1}).
    detail          JSONB NOT NULL DEFAULT '{}'::jsonb,

    detected_by     TEXT NOT NULL,  -- script / module name
    detected_at     TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- Set when an admin decides this flag is handled (data fixed, false
    -- positive accepted, etc.). resolved_at IS NULL means "open".
    resolved_at     TIMESTAMPTZ,
    resolved_by     TEXT,
    resolution_note TEXT,

    CHECK (
        (claim_id IS NOT NULL)::int
      + (entity_id IS NOT NULL)::int
      + (event_id IS NOT NULL)::int = 1
    )
);

COMMENT ON TABLE data_quality_flags IS
    'Soft-flag quarantine queue. Pipeline detectors write here instead of '
    'mutating suspect rows. Admin reviews the flag and either fixes the '
    'underlying data via the retract / edit / merge tools, then marks the '
    'flag resolved.';

-- Open-flag lookup (admin UI: "what needs my attention right now?").
CREATE INDEX idx_dqflags_open
    ON data_quality_flags (detected_at DESC)
    WHERE resolved_at IS NULL;

-- Per-target lookup (admin clicks an entity, sees all open flags for it).
CREATE INDEX idx_dqflags_claim ON data_quality_flags (claim_id)
    WHERE claim_id IS NOT NULL;
CREATE INDEX idx_dqflags_entity ON data_quality_flags (entity_id)
    WHERE entity_id IS NOT NULL;
CREATE INDEX idx_dqflags_event ON data_quality_flags (event_id)
    WHERE event_id IS NOT NULL;

-- Idempotency: don't let detectors re-create an open flag they already
-- raised. Resolved flags don't conflict — once the admin closes one, the
-- next detector run is allowed to re-open if the issue resurfaces.
-- COALESCE with the zero UUID lets the unique index span the three nullable
-- columns without violating PostgreSQL's "NULL is distinct from NULL" rule.
CREATE UNIQUE INDEX idx_dqflags_unique_open
    ON data_quality_flags (
        flag_kind,
        COALESCE(claim_id,  '00000000-0000-0000-0000-000000000000'::uuid),
        COALESCE(entity_id, '00000000-0000-0000-0000-000000000000'::uuid),
        COALESCE(event_id,  '00000000-0000-0000-0000-000000000000'::uuid)
    )
    WHERE resolved_at IS NULL;

COMMIT;

-- Verification queries:
--   SELECT COUNT(*) FROM data_quality_flags;
--     Expected after migration: 0 (table is empty until detectors run).
--
--   \d data_quality_flags
--     Should show: 3 nullable target FKs + flag_kind + severity check
--     + detected/resolved fields + CHECK enforcing exactly-one target.
