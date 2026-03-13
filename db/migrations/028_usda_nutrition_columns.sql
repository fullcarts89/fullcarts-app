-- Migration 028: Add nutrition columns to usda_product_history
-- Stores key macronutrient values per product per release.
-- Enables cross-release nutrition comparison for skimpflation detection.
-- Values are per 100g serving (USDA standard basis).
--
-- Populated by: pipeline/scripts/backfill_nutrition.py

ALTER TABLE usda_product_history
    ADD COLUMN IF NOT EXISTS calories_kcal   NUMERIC,
    ADD COLUMN IF NOT EXISTS protein_g       NUMERIC,
    ADD COLUMN IF NOT EXISTS total_fat_g     NUMERIC,
    ADD COLUMN IF NOT EXISTS saturated_fat_g NUMERIC,
    ADD COLUMN IF NOT EXISTS carbs_g         NUMERIC,
    ADD COLUMN IF NOT EXISTS fiber_g         NUMERIC,
    ADD COLUMN IF NOT EXISTS sugars_g        NUMERIC,
    ADD COLUMN IF NOT EXISTS calcium_mg      NUMERIC,
    ADD COLUMN IF NOT EXISTS sodium_mg       NUMERIC,
    ADD COLUMN IF NOT EXISTS cholesterol_mg  NUMERIC;

-- Partial index for filtering products with nutrition data
-- (needed for skimpflation analysis queries)
CREATE INDEX IF NOT EXISTS idx_usda_history_has_nutrition
    ON usda_product_history (release_date, gtin_upc)
    WHERE protein_g IS NOT NULL;
