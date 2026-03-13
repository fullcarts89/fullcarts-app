"""USDA FoodData Central variance analyzer.

Reads USDA raw_items from Supabase, groups by UPC across release dates,
and detects significant size changes between consecutive releases.
Writes detected changes back to raw_items with source_type='usda_size_change'.

This is a post-processing job, not a real-time scraper.  It reads FROM
raw_items (source_type='usda') and writes BACK to raw_items
(source_type='usda_size_change').

Strategy: streams all USDA records paginated by primary key (id), groups
by UPC in memory, then runs change detection.  This avoids unindexed
JSONB ORDER BY queries and N+1 per-UPC lookups.
"""
from typing import Any, Dict, List, Optional

from pipeline.lib.supabase_client import get_client
from pipeline.lib.units import convert_to_base
from pipeline.scrapers.base import BaseScraper

_PAGE_SIZE = 1000   # Supabase PostgREST max rows per request
_LOG_EVERY = 100000  # Log progress every N rows
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
        """Stream all USDA raw_items by id, group by UPC, detect size changes.

        Paginates by primary key (always fast) and accumulates a lightweight
        dict of {upc: observations} in memory.  After streaming all data,
        runs detect_changes() on each UPC with 2+ observations.
        """
        client = get_client()
        last_id = cursor.get("last_id", "")

        # {upc: {"brand": str, "desc": str, "obs": {date: (size, unit)}}}
        upc_data = {}  # type: Dict[str, Dict[str, Any]]
        total_rows = 0

        self.log.info("Streaming USDA records%s ...",
                       " from id > %s" % last_id if last_id else "")

        while True:
            query = (
                client.table("raw_items")
                .select("id,source_date,raw_payload")
                .eq("source_type", "usda")
            )
            if last_id:
                query = query.gt("id", last_id)

            resp = (
                query
                .order("id")
                .range(0, _PAGE_SIZE - 1)
                .execute()
            )

            rows = resp.data or []
            if not rows:
                break

            for row in rows:
                payload = row.get("raw_payload") or {}
                upc = payload.get("gtin_upc", "")
                size = payload.get("_size")
                size_unit = payload.get("_size_unit", "")
                date = (row.get("source_date") or "")[:10]

                if not upc or size is None or not date:
                    continue

                if upc not in upc_data:
                    upc_data[upc] = {
                        "brand": payload.get("brand_owner", ""),
                        "desc": payload.get("description", ""),
                        "obs": {},
                    }

                # Deduplicate: keep first observation per (UPC, date)
                if date not in upc_data[upc]["obs"]:
                    upc_data[upc]["obs"][date] = (size, size_unit)

            total_rows += len(rows)
            last_id = rows[-1]["id"]

            if total_rows % _LOG_EVERY == 0:
                self.log.info(
                    "Streamed %d rows, %d UPCs so far...",
                    total_rows, len(upc_data),
                )

            if len(rows) < _PAGE_SIZE:
                break

        self.log.info(
            "Streamed %d total rows, %d unique UPCs. Detecting changes...",
            total_rows, len(upc_data),
        )

        # Detect changes for each UPC with 2+ observations
        all_changes = []  # type: List[Dict[str, Any]]
        for upc, data in upc_data.items():
            obs_dict = data["obs"]
            if len(obs_dict) < 2:
                continue

            # Build sorted observation list for detect_changes()
            observations = []
            for date in sorted(obs_dict.keys()):
                size, unit = obs_dict[date]
                observations.append({
                    "gtin_upc": upc,
                    "brand_owner": data["brand"],
                    "description": data["desc"],
                    "_size": size,
                    "_size_unit": unit,
                    "source_date": date,
                })

            changes = detect_changes(observations)
            all_changes.extend(changes)

        self.log.info(
            "USDA variance: %d UPCs analyzed, %d size changes found",
            len(upc_data), len(all_changes),
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
            "last_id": "",  # Reset for next full run
            "total_changes": prev_total + len(items),
        }
