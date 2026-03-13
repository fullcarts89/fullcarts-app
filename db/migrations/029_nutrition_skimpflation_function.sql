-- Migration 029: Database function for nutrition-based skimpflation analysis
-- Compares nutrition values between two USDA releases to find products
-- where the manufacturer resubmitted with worse nutritional profiles.
--
-- Skimpflation signals:
--   - Protein/fiber/calcium DROPPED 5-50% (less quality ingredients)
--   - Sugar/sodium INCREASED 5-50% (more cheap filler)
--
-- Usage:
--   SELECT * FROM nutrition_skimpflation();  -- defaults
--   SELECT * FROM nutrition_skimpflation('2022-10-28', '2025-12-18', 10);

CREATE OR REPLACE FUNCTION nutrition_skimpflation(
  early_date DATE DEFAULT '2022-10-28',
  late_date DATE DEFAULT '2025-12-18',
  min_score NUMERIC DEFAULT 5
)
RETURNS TABLE (
  gtin_upc TEXT,
  brand_name TEXT,
  description TEXT,
  skimp_score NUMERIC,
  protein_drop_pct NUMERIC,
  fiber_drop_pct NUMERIC,
  sugar_rise_pct NUMERIC,
  sodium_rise_pct NUMERIC,
  old_protein NUMERIC, new_protein NUMERIC,
  old_fiber NUMERIC, new_fiber NUMERIC,
  old_sugar NUMERIC, new_sugar NUMERIC,
  old_sodium NUMERIC, new_sodium NUMERIC,
  old_calories NUMERIC, new_calories NUMERIC
) LANGUAGE sql STABLE AS $$
  WITH changes AS (
    SELECT
      e.gtin_upc,
      COALESCE(l.brand_name, e.brand_name) AS brand_name,
      COALESCE(l.description, e.description) AS description,
      e.protein_g, l.protein_g AS new_protein,
      e.fiber_g, l.fiber_g AS new_fiber,
      e.calcium_mg, l.calcium_mg AS new_calcium,
      e.sugars_g, l.sugars_g AS new_sugar,
      e.sodium_mg, l.sodium_mg AS new_sodium,
      e.calories_kcal, l.calories_kcal AS new_cal,
      -- Protein drop (5-50% range)
      CASE WHEN e.protein_g > 1 AND l.protein_g < e.protein_g * 0.95
           AND l.protein_g > e.protein_g * 0.5
        THEN round(((e.protein_g - l.protein_g) / e.protein_g * 100)::numeric, 1) END AS p_drop,
      -- Fiber drop (5-50% range)
      CASE WHEN e.fiber_g > 1 AND l.fiber_g < e.fiber_g * 0.95
           AND l.fiber_g > e.fiber_g * 0.5
        THEN round(((e.fiber_g - l.fiber_g) / e.fiber_g * 100)::numeric, 1) END AS f_drop,
      -- Sugar rise (5-50% range)
      CASE WHEN e.sugars_g > 1 AND l.sugars_g > e.sugars_g * 1.05
           AND l.sugars_g < e.sugars_g * 1.5
        THEN round(((l.sugars_g - e.sugars_g) / e.sugars_g * 100)::numeric, 1) END AS s_rise,
      -- Sodium rise (5-50% range)
      CASE WHEN e.sodium_mg > 10 AND l.sodium_mg > e.sodium_mg * 1.05
           AND l.sodium_mg < e.sodium_mg * 1.5
        THEN round(((l.sodium_mg - e.sodium_mg) / e.sodium_mg * 100)::numeric, 1) END AS na_rise
    FROM usda_product_history e
    JOIN usda_product_history l ON e.gtin_upc = l.gtin_upc
    WHERE e.release_date = early_date
      AND l.release_date = late_date
      AND e.protein_g IS NOT NULL AND l.protein_g IS NOT NULL
      AND e.fdc_id != l.fdc_id
      AND e.calories_kcal > 0 AND l.calories_kcal > 0
  )
  SELECT c.gtin_upc, c.brand_name, c.description,
    round((COALESCE(c.p_drop, 0) + COALESCE(c.f_drop, 0)
      + COALESCE(c.s_rise, 0) + COALESCE(c.na_rise, 0))::numeric, 1) AS skimp_score,
    c.p_drop, c.f_drop, c.s_rise, c.na_rise,
    c.protein_g, c.new_protein,
    c.fiber_g, c.new_fiber,
    c.sugars_g, c.new_sugar,
    c.sodium_mg, c.new_sodium,
    c.calories_kcal, c.new_cal
  FROM changes c
  WHERE COALESCE(c.p_drop, 0) + COALESCE(c.f_drop, 0)
      + COALESCE(c.s_rise, 0) + COALESCE(c.na_rise, 0) >= min_score
  ORDER BY COALESCE(c.p_drop, 0) + COALESCE(c.f_drop, 0)
      + COALESCE(c.s_rise, 0) + COALESCE(c.na_rise, 0) DESC;
$$;
