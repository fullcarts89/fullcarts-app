-- ============================================================
-- Migration 002: Add change_events table + detection function
-- Stores computed deltas between consecutive product versions.
-- ============================================================

BEGIN;

CREATE TABLE IF NOT EXISTS change_events (
  id                      uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  product_upc             text NOT NULL REFERENCES products(upc) ON DELETE CASCADE,

  -- Links to the two versions being compared
  version_before_id       uuid REFERENCES product_versions(id),
  version_after_id        uuid REFERENCES product_versions(id),

  -- When the change was detected / occurred
  detected_date           date NOT NULL,

  -- ── Size delta ────────────────────────────────────────────
  old_size                numeric NOT NULL,
  new_size                numeric NOT NULL,
  unit                    text    NOT NULL,
  size_delta_pct          numeric NOT NULL,  -- negative = shrunk

  -- ── Price delta ───────────────────────────────────────────
  old_price               numeric,
  new_price               numeric,
  old_price_per_unit      numeric,
  new_price_per_unit      numeric,
  price_per_unit_delta_pct numeric,          -- positive = more expensive per unit

  -- ── Classification ────────────────────────────────────────
  change_type             text NOT NULL CHECK (change_type IN (
    'shrinkflation',    -- size ↓, price same or ↑ (the classic)
    'downsizing',       -- size ↓, price ↓ (but ppu may still ↑)
    'upsizing',         -- size ↑
    'price_hike',       -- size same, price ↑
    'skimpflation',     -- same size/price, lower quality (manual)
    'restoration'       -- size returned toward previous level
  )),
  is_shrinkflation        boolean NOT NULL DEFAULT false,
  severity                text CHECK (severity IN ('minor', 'moderate', 'major')),

  -- ── Verification ──────────────────────────────────────────
  verified                boolean DEFAULT false,
  verified_by             text,
  verified_at             timestamptz,
  notes                   text,

  -- Audit
  created_at              timestamptz DEFAULT now(),

  -- Prevent duplicate events for same version pair
  UNIQUE(version_before_id, version_after_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_ce_product_upc    ON change_events(product_upc);
CREATE INDEX IF NOT EXISTS idx_ce_detected_date  ON change_events(detected_date DESC);
CREATE INDEX IF NOT EXISTS idx_ce_change_type    ON change_events(change_type);
CREATE INDEX IF NOT EXISTS idx_ce_shrinkflation  ON change_events(is_shrinkflation) WHERE is_shrinkflation = true;
CREATE INDEX IF NOT EXISTS idx_ce_severity       ON change_events(severity);
CREATE INDEX IF NOT EXISTS idx_ce_verified       ON change_events(verified);

-- RLS
ALTER TABLE change_events ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read change_events"
  ON change_events FOR SELECT USING (true);
CREATE POLICY "Service role manages change_events"
  ON change_events FOR ALL USING (auth.role() = 'service_role');


-- ============================================================
-- Function: classify a size change
-- ============================================================
CREATE OR REPLACE FUNCTION classify_change(
  p_old_size numeric,
  p_new_size numeric,
  p_old_price numeric DEFAULT NULL,
  p_new_price numeric DEFAULT NULL
) RETURNS jsonb
LANGUAGE plpgsql IMMUTABLE AS $$
DECLARE
  size_delta_pct    numeric;
  old_ppu           numeric;
  new_ppu           numeric;
  ppu_delta_pct     numeric;
  change_type       text;
  is_shrinkflation  boolean := false;
  severity          text;
BEGIN
  -- Size delta (negative = smaller)
  IF p_old_size > 0 THEN
    size_delta_pct := round(((p_new_size - p_old_size) / p_old_size) * 100, 2);
  ELSE
    size_delta_pct := 0;
  END IF;

  -- Price per unit
  IF p_old_size > 0 AND p_old_price IS NOT NULL THEN
    old_ppu := round(p_old_price / p_old_size, 4);
  END IF;
  IF p_new_size > 0 AND p_new_price IS NOT NULL THEN
    new_ppu := round(p_new_price / p_new_size, 4);
  END IF;

  -- PPU delta
  IF old_ppu IS NOT NULL AND old_ppu > 0 AND new_ppu IS NOT NULL THEN
    ppu_delta_pct := round(((new_ppu - old_ppu) / old_ppu) * 100, 2);
  END IF;

  -- Classification logic
  IF p_new_size > p_old_size THEN
    change_type := 'upsizing';
  ELSIF p_new_size < p_old_size THEN
    IF p_new_price IS NOT NULL AND p_old_price IS NOT NULL AND p_new_price < p_old_price THEN
      change_type := 'downsizing';
    ELSE
      change_type := 'shrinkflation';
      is_shrinkflation := true;
    END IF;
  ELSE
    -- Same size
    IF p_new_price IS NOT NULL AND p_old_price IS NOT NULL AND p_new_price > p_old_price THEN
      change_type := 'price_hike';
    ELSE
      change_type := 'downsizing';  -- fallback
    END IF;
  END IF;

  -- Severity (based on absolute size reduction %)
  IF size_delta_pct < 0 THEN
    IF abs(size_delta_pct) >= 15 THEN
      severity := 'major';
    ELSIF abs(size_delta_pct) >= 5 THEN
      severity := 'moderate';
    ELSE
      severity := 'minor';
    END IF;
  END IF;

  RETURN jsonb_build_object(
    'size_delta_pct',          size_delta_pct,
    'old_price_per_unit',      old_ppu,
    'new_price_per_unit',      new_ppu,
    'price_per_unit_delta_pct', ppu_delta_pct,
    'change_type',             change_type,
    'is_shrinkflation',        is_shrinkflation,
    'severity',                severity
  );
END;
$$;


-- ============================================================
-- Function: detect changes for a single product
-- Finds consecutive version pairs without a change_event and creates one.
-- Returns number of new events created.
-- ============================================================
CREATE OR REPLACE FUNCTION detect_changes_for_product(p_upc text)
RETURNS integer
LANGUAGE plpgsql AS $$
DECLARE
  v_cur    record;
  v_prev   record;
  v_class  jsonb;
  created  integer := 0;
  is_first boolean := true;
BEGIN
  FOR v_cur IN
    SELECT id, observed_date, size, unit, price, price_per_unit
    FROM product_versions
    WHERE product_upc = p_upc
    ORDER BY observed_date ASC
  LOOP
    IF NOT is_first AND v_prev.size IS DISTINCT FROM v_cur.size THEN
      -- Check if we already have a change_event for this pair
      IF NOT EXISTS (
        SELECT 1 FROM change_events
        WHERE version_before_id = v_prev.id AND version_after_id = v_cur.id
      ) THEN
        v_class := classify_change(v_prev.size, v_cur.size, v_prev.price, v_cur.price);

        INSERT INTO change_events (
          product_upc, version_before_id, version_after_id, detected_date,
          old_size, new_size, unit, size_delta_pct,
          old_price, new_price, old_price_per_unit, new_price_per_unit,
          price_per_unit_delta_pct,
          change_type, is_shrinkflation, severity
        ) VALUES (
          p_upc, v_prev.id, v_cur.id, v_cur.observed_date,
          v_prev.size, v_cur.size, v_cur.unit,
          (v_class->>'size_delta_pct')::numeric,
          v_prev.price, v_cur.price,
          (v_class->>'old_price_per_unit')::numeric,
          (v_class->>'new_price_per_unit')::numeric,
          (v_class->>'price_per_unit_delta_pct')::numeric,
          v_class->>'change_type',
          (v_class->>'is_shrinkflation')::boolean,
          v_class->>'severity'
        );
        created := created + 1;
      END IF;
    END IF;
    v_prev := v_cur;
    is_first := false;
  END LOOP;

  -- Update product's current_size to the latest version
  IF NOT is_first THEN
    UPDATE products SET
      current_size = v_prev.size,
      unit         = v_prev.unit,
      updated_at   = now()
    WHERE upc = p_upc;
  END IF;

  RETURN created;
END;
$$;


-- ============================================================
-- Function: detect changes across ALL products
-- ============================================================
CREATE OR REPLACE FUNCTION detect_all_changes()
RETURNS integer
LANGUAGE plpgsql AS $$
DECLARE
  r       record;
  total   integer := 0;
BEGIN
  FOR r IN SELECT DISTINCT product_upc FROM product_versions LOOP
    total := total + detect_changes_for_product(r.product_upc);
  END LOOP;
  RETURN total;
END;
$$;

COMMIT;
