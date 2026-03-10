"""USDA FoodData Central variance analyzer.

Reads USDA raw_items from Supabase, groups by UPC across release dates,
and detects significant size changes between consecutive releases.
Writes detected changes back to raw_items with source_type='usda_size_change'.

This is a post-processing job, not a real-time scraper.  It reads FROM
raw_items (source_type='usda') and writes BACK to raw_items
(source_type='usda_size_change').
"""
from typing import Any, Dict, List, Optional, Tuple

from pipeline.lib.logging_setup import get_logger
from pipeline.lib.supabase_client import get_client
from pipeline.lib.units import convert_to_base, parse_package_weight
from pipeline.scrapers.base import BaseScraper

_UPC_BATCH_SIZE = 1000
_CHANGE_THRESHOLD_PCT = 2.0  # Only flag changes > 2%


def detect_changes(
    observations: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Given USDA records for a single UPC sorted by date, detect size changes.

    Each observation must have keys: gtin_upc, brand_owner, description,
    _size (float), _size_unit (str), source_date (str).

    Returns a list of change dicts for consecutive pairs with >2% size change.
    """
    changes: List[Dict[str, Any]] = []

    for i in range(1, len(observations)):
        old = observations[i - 1]
        new = observations[i]

        old_size = old.get("_size")
        old_unit = old.get("_size_unit", "")
        new_size = new.get("_size")
        new_unit = new.get("_size_unit", "")

        if old_size is None or new_size is None:
            continue
        if old_size == 0:
            continue

        # Normalize to base units for comparison
        old_base, old_base_unit = convert_to_base(old_size, old_unit)
        new_base, new_base_unit = convert_to_base(new_size, new_unit)

        # Can only compare same-unit observations
        if old_base_unit != new_base_unit:
            continue

        pct_change = ((new_base - old_base) / old_base) * 100.0

        # Only flag significant changes
        if abs(pct_change) <= _CHANGE_THRESHOLD_PCT:
            continue

        direction = "decrease" if pct_change < 0 else "increase"
        changes.append({
            "gtin_upc": old["gtin_upc"],
            "brand_owner": new.get("brand_owner", ""),
            "description": new.get("description", ""),
            "old_size": old_size,
            "old_unit": old_unit,
            "new_size": new_size,
            "new_unit": new_unit,
            "old_date": old["source_date"],
            "new_date": new["source_date"],
            "pct_change": round(pct_change, 2),
            "direction": direction,
        })

    return changes


class UsdaVarianceAnalyzer(BaseScraper):
    """Detects size changes across USDA FoodData Central releases."""

    scraper_name = "usda_variance"
    source_type = "usda_size_change"

    def __init__(self) -> None:
        super().__init__()

    # ── BaseScraper interface ──────────────────────────────────────────────

    def fetch(
        self, cursor: Dict[str, Any], dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        """Read USDA raw_items, group by UPC, detect size changes.

        Paginates through UPCs in batches.  Returns detected change items.
        """
        last_upc = cursor.get("last_upc", "")
        total_changes_prev = int(cursor.get("total_changes", 0))

        client = get_client()
        all_changes: List[Dict[str, Any]] = []
        upcs_processed = 0

        while True:
            # Get next batch of distinct UPCs
            upcs = self._fetch_upc_batch(client, last_upc)
            if not upcs:
                break

            self.log.info(
                "Processing UPC batch: %d UPCs (after '%s')",
                len(upcs), last_upc[:20] if last_upc else "start",
            )

            # For each UPC, get all USDA records and compare
            for upc in upcs:
                observations = self._fetch_observations_for_upc(client, upc)
                if len(observations) < 2:
                    continue
                changes = detect_changes(observations)
                all_changes.extend(changes)

            upcs_processed += len(upcs)
            last_upc = upcs[-1]

            if len(upcs) < _UPC_BATCH_SIZE:
                break  # Last batch

        self.log.info(
            "USDA variance: processed %d UPCs, found %d size changes",
            upcs_processed, len(all_changes),
        )
        return all_changes

    def source_id_for(self, item: Dict[str, Any]) -> str:
        return "usda_var_{}_{}_{}" .format(
            item["gtin_upc"], item["old_date"], item["new_date"],
        )

    def source_url_for(self, item: Dict[str, Any]) -> Optional[str]:
        return None

    def source_date_for(self, item: Dict[str, Any]) -> Optional[str]:
        return item.get("new_date")

    def next_cursor(
        self, items: List[Dict[str, Any]], prev_cursor: Dict[str, Any]
    ) -> Dict[str, Any]:
        prev_total = int(prev_cursor.get("total_changes", 0))
        return {
            "last_upc": "",  # Reset for next full run
            "total_changes": prev_total + len(items),
        }

    # ── Private helpers ────────────────────────────────────────────────────

    def _fetch_upc_batch(
        self, client: Any, after_upc: str
    ) -> List[str]:
        """Get the next batch of distinct UPCs from USDA raw_items.

        Supabase PostgREST caps responses at ~1000 rows regardless of
        the limit parameter, so we paginate internally using range()
        offsets until we collect _UPC_BATCH_SIZE distinct UPCs.
        """
        _PAGE_SIZE = 1000  # Supabase PostgREST max rows per request
        _MAX_PAGES = 50    # Safety cap: 50 pages × 1000 = 50K rows scanned

        seen: List[str] = []
        seen_set: set = set()
        offset = 0

        for _ in range(_MAX_PAGES):
            query = (
                client.table("raw_items")
                .select("raw_payload->gtin_upc")
                .eq("source_type", "usda")
            )
            if after_upc:
                query = query.gt("raw_payload->>gtin_upc", after_upc)

            resp = (
                query
                .order("raw_payload->>gtin_upc")
                .range(offset, offset + _PAGE_SIZE - 1)
                .execute()
            )

            rows = resp.data or []
            if not rows:
                break  # No more data

            for row in rows:
                upc = row.get("gtin_upc", "")
                if upc and upc not in seen_set:
                    seen_set.add(upc)
                    seen.append(upc)
                    if len(seen) >= _UPC_BATCH_SIZE:
                        return seen

            offset += _PAGE_SIZE

            if len(rows) < _PAGE_SIZE:
                break  # Last page

        return seen

    def _fetch_observations_for_upc(
        self, client: Any, upc: str
    ) -> List[Dict[str, Any]]:
        """Get all USDA raw_items for a specific UPC, sorted by source_date."""
        resp = (
            client.table("raw_items")
            .select("source_date,raw_payload")
            .eq("source_type", "usda")
            .eq("raw_payload->>gtin_upc", upc)
            .order("source_date")
            .execute()
        )

        observations: List[Dict[str, Any]] = []
        for row in (resp.data or []):
            payload = row.get("raw_payload", {})
            observations.append({
                "gtin_upc": payload.get("gtin_upc", upc),
                "brand_owner": payload.get("brand_owner", ""),
                "description": payload.get("description", ""),
                "_size": payload.get("_size"),
                "_size_unit": payload.get("_size_unit", ""),
                "source_date": (row.get("source_date") or "")[:10],
            })

        return observations
