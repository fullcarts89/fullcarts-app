# Plan: Route Discovery Scrapers to Product Catalog + Add Size Variance Analysis

## Problem

Discovery scrapers (`off_discovery`, `kroger_discovery`, `walmart`) currently write to `raw_items`, where the claims extraction pipeline treats them as shrinkflation reports. They should instead feed the product catalog directly. Additionally, we need size variance analysis on the catalog data these scrapers produce.

## Changes

### 1. New migration: `041_discovery_catalog.sql`

Add a `discovery_source` column to `pack_variants` to track which scraper first cataloged the product:

```sql
ALTER TABLE pack_variants ADD COLUMN IF NOT EXISTS discovery_source TEXT;
ALTER TABLE pack_variants ADD COLUMN IF NOT EXISTS discovery_id TEXT;
-- Composite unique: same source shouldn't catalog a product twice
ALTER TABLE pack_variants ADD CONSTRAINT uq_discovery
    UNIQUE NULLS NOT DISTINCT (discovery_source, discovery_id);
```

### 2. New base class: `pipeline/scrapers/catalog_base.py`

A `CatalogScraper` base class that:
- Extends `BaseScraper` for cursor/state management
- Overrides `store()` to upsert into `product_entities` + `pack_variants` (+ optional `variant_observations`) instead of `raw_items`
- Provides `extract_product(item)` abstract method returning a structured dict: `{ brand, name, category, upc, size, size_unit, variant_name, image_url }`
- Finds-or-creates `product_entities` by `(brand, canonical_name)`
- Finds-or-creates `pack_variants` by `upc` (or `discovery_source + discovery_id` if no UPC)
- Optionally creates a `variant_observations` row when size data is present (for variance tracking)

### 3. Refactor discovery scrapers to extend `CatalogScraper`

**`off_discovery.py`**: Change parent from `BaseScraper` → `CatalogScraper`. Implement `extract_product()` to map OFF fields (`product_name`, `brands`, `quantity`, `code`) to catalog fields. Remove from `raw_items` flow.

**`kroger_discovery.py`**: Same refactor. Map Kroger product fields (`_product.description`, `_product.brand`, `_product.upc`, `_product.items[0].size`) to catalog fields.

**`walmart.py`**: Same refactor. Map Walmart fields to catalog fields. (Note: `walmart` was never added to the `raw_items` CHECK constraint, so it wasn't actually storing data — this fixes that gap.)

### 4. New analysis script: `pipeline/scripts/analyze_catalog_variance.py`

A size variance analyzer for catalog-sourced observations, following the pattern of existing analyzers (`analyze_off_changes.py`, `analyze_kroger_changes.py`):

- Queries `variant_observations` for catalog-sourced records (source_type IN `'off_catalog'`, `'kroger_catalog'`, `'walmart_catalog'`)
- Groups by `variant_id`, orders by `observed_date`
- Compares consecutive observations using `convert_to_base()` from `pipeline/lib/units.py`
- Flags size decreases ≥ 2% (matching existing threshold)
- Outputs detected changes to `raw_items` with a new source_type `'catalog_size_change'` so they enter the claims pipeline as legitimate shrinkflation signals
- Requires adding `'catalog_size_change'` to the `raw_items` CHECK constraint (in the same migration)

### 5. Migration addition to `041_discovery_catalog.sql`

```sql
-- Allow catalog variance analyzer to write detected changes
ALTER TABLE raw_items DROP CONSTRAINT IF EXISTS raw_items_source_type_check;
ALTER TABLE raw_items ADD CONSTRAINT raw_items_source_type_check
    CHECK (source_type IN (
        'reddit', 'news', 'openfoodfacts', 'kroger_api',
        'usda', 'usda_size_change', 'usda_turnover_change',
        'usda_nutrition', 'community_tip', 'receipt', 'gdelt',
        'kroger_change', 'off_change', 'open_prices',
        'catalog_size_change'
    ));
```

### 6. Tests

- `pipeline/tests/test_catalog_base.py` — Unit tests for `CatalogScraper.store()` upsert logic
- `pipeline/tests/test_analyze_catalog_variance.py` — Unit tests for variance detection (matching the pattern of `test_usda_variance.py`)

## File Summary

| File | Action |
|------|--------|
| `db/migrations/041_discovery_catalog.sql` | New migration |
| `pipeline/scrapers/catalog_base.py` | New base class |
| `pipeline/scrapers/off_discovery.py` | Refactor to extend CatalogScraper |
| `pipeline/scrapers/kroger_discovery.py` | Refactor to extend CatalogScraper |
| `pipeline/scrapers/walmart.py` | Refactor to extend CatalogScraper |
| `pipeline/scripts/analyze_catalog_variance.py` | New variance analyzer |
| `pipeline/tests/test_catalog_base.py` | New tests |
| `pipeline/tests/test_analyze_catalog_variance.py` | New tests |

## Data Flow (After)

```
Discovery scrapers (off_discovery, kroger_discovery, walmart)
    │
    ▼
product_entities + pack_variants + variant_observations
    │
    ▼ (analyze_catalog_variance.py detects size changes)
    │
    ▼
raw_items (source_type='catalog_size_change')
    │
    ▼ (claims extraction pipeline)
    │
    ▼
claims → promote_claims.py → published_changes
```

Discovery data builds the catalog. Only **actual size changes** detected over time enter the claims pipeline.
