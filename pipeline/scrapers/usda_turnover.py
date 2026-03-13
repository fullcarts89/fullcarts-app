"""USDA FoodData Central cross-UPC turnover analyzer.

Detects "product turnover shrinkflation" — when a brand retires one UPC
and launches a replacement with a smaller size.  This is the dominant form
of shrinkflation (UMass study: ~14.6% avg decline via product turnover vs
<0.5% same-UPC shrinkflation).

Strategy:
  1. Load fdc_id → description lookup from USDA food.csv (pre-extracted JSON)
  2. Stream all USDA records paginated by primary key (id)
  3. Normalize brand_owner and product description strings
  4. Group products by (norm_brand, norm_description, category, base_unit)
  5. Within each group, find products appearing in different releases
     with different UPCs and different sizes
  6. Flag size decreases in realistic range (3-40%) as turnover candidates

USDA branded_food.csv has empty 'description' fields, but food.csv (in the
same ZIP) contains full product descriptions keyed by fdc_id, e.g.
"Lay's Classic Potato Chips 10 Ounce Plastic Bag".  We strip trailing
size/packaging info so different sizes of the same product group together.

Pure function detect_turnover_changes() is independently testable.
"""
import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

from pipeline.lib.supabase_client import get_client
from pipeline.lib.units import convert_to_base
from pipeline.scrapers.base import BaseScraper

_PAGE_SIZE = 1000
_LOG_EVERY = 100000
_CHANGE_THRESHOLD_PCT = 3.0   # Min decrease to flag (skip noise < 3%)
_MAX_CHANGE_PCT = 40.0        # Max decrease to flag (>40% is likely data error)

# Default location for pre-extracted fdc_id -> description JSON
_DEFAULT_DESC_PATH = "/tmp/usda_fdc_descriptions.json"

# ── Text normalization ────────────────────────────────────────────────────

# Common suffixes in brand_owner that add noise
_BRAND_STRIP_SUFFIXES = re.compile(
    r",?\s*\b(inc\.?|llc\.?|ltd\.?|co\.?|corp\.?|corporation|company|"
    r"l\.?l\.?c\.?|l\.?p\.?|plc|sa|gmbh|ag|pty|limited)\b\.?",
    re.IGNORECASE,
)
# Leading "THE" in brand names
_BRAND_STRIP_LEADING_THE = re.compile(r"^\s*the\s+", re.IGNORECASE)
# Collapse multiple whitespace
_MULTI_SPACE = re.compile(r"\s+")
# Non-alphanumeric (keep spaces)
_NON_ALNUM = re.compile(r"[^a-z0-9\s]")


def normalize_brand(brand: str) -> str:
    """Normalize a brand_owner string for grouping.

    Strips legal suffixes (Inc, LLC, etc.), leading 'THE', punctuation,
    and collapses whitespace.  Hyphens become spaces so 'FRITO-LAY'
    normalizes to 'frito lay' rather than 'fritolay'.

    >>> normalize_brand("THE FRITO-LAY, INC.")
    'frito lay'
    >>> normalize_brand("Kellogg's Company")
    'kelloggs'
    >>> normalize_brand("General Mills, Inc")
    'general mills'
    """
    if not brand:
        return ""
    s = brand.lower().strip()
    s = _BRAND_STRIP_SUFFIXES.sub("", s)
    s = _BRAND_STRIP_LEADING_THE.sub("", s)
    # Replace hyphens with spaces BEFORE stripping punctuation
    s = s.replace("-", " ")
    s = _NON_ALNUM.sub("", s)
    s = _MULTI_SPACE.sub(" ", s).strip()
    return s


def normalize_description(desc: str) -> str:
    """Normalize a product description for grouping.

    Lowercases, replaces hyphens with spaces, strips other punctuation,
    collapses whitespace.

    >>> normalize_description("LAY'S CLASSIC POTATO CHIPS")
    'lays classic potato chips'
    >>> normalize_description("  Honey-Nut  Cheerios  ")
    'honey nut cheerios'
    """
    if not desc:
        return ""
    s = desc.lower().strip()
    s = s.replace("-", " ")
    s = _NON_ALNUM.sub("", s)
    s = _MULTI_SPACE.sub(" ", s).strip()
    return s


# ── Description size stripping ───────────────────────────────────────────

# Strip trailing "N Ounce ...", "48 FL OZ ...", "72 Count ..." etc.
_SIZE_TAIL = re.compile(
    r"\s+\d[\d\s/.,]*"
    r"\s*(?:ounces?|oz|pounds?|lbs?|count|ct|grams?|g|ml|"
    r"fl\.?\s*oz|liters?|gallons?|gal|quarts?|qt|pints?|pt)\b"
    r".*$",
    re.IGNORECASE,
)
# Strip trailing "N Pack" pattern (e.g. "4 Pack", "12 Pack")
_N_PACK = re.compile(r"\s+\d+\s+pack\b.*$", re.IGNORECASE)
# Strip trailing "Party/Family/King Size [Bag]" (but NOT "Standard Bar" etc.)
_SIZE_LABEL = re.compile(
    r"\s+(?:party\s+size|family\s+size|king\s+size|snack\s+size|"
    r"fun\s+size)"
    r"(?:\s+\w+)?"
    r"\s*$",
    re.IGNORECASE,
)


def strip_size_from_description(desc: str) -> str:
    """Remove trailing size/packaging info from a USDA food.csv description.

    USDA descriptions sometimes embed sizes, e.g.:
        "Lay's Classic Potato Chips 10 Ounce Plastic Bag"
        "Hershey's Soft Donut Bites 72 Count"
        "WESSON Canola Oil 48 FL OZ"

    We strip these so different sizes of the same product group together
    for turnover comparison.

    >>> strip_size_from_description("Lay's Classic Potato Chips 10 Ounce Plastic Bag")
    "Lay's Classic Potato Chips"
    >>> strip_size_from_description("CAMPBELL'S SOUP TOMATO")
    "CAMPBELL'S SOUP TOMATO"
    >>> strip_size_from_description("Hershey's Soft Donut Bites 72 Count")
    "Hershey's Soft Donut Bites"
    """
    if not desc:
        return ""
    s = _SIZE_TAIL.sub("", desc)
    s = _N_PACK.sub("", s)
    s = _SIZE_LABEL.sub("", s)
    return s.strip()


def _base_unit_for(unit: str) -> str:
    """Return the base unit category for comparison.

    We only compare products whose sizes share the same base unit.
    """
    _, base_unit = convert_to_base(1.0, unit)
    return base_unit


# ── Core detection logic ──────────────────────────────────────────────────


def detect_turnover_changes(
    product_group: Dict[str, Any],
    min_pct: float = _CHANGE_THRESHOLD_PCT,
    max_pct: float = _MAX_CHANGE_PCT,
) -> List[Dict[str, Any]]:
    """Given a group of products with the same brand+name+category, detect
    size decreases across different UPCs in consecutive releases.

    product_group has the shape:
        {
            "brand_owner": "FRITO-LAY, INC.",
            "brand_name": "LAY'S",
            "category": "Chips, Pretzels & Snacks",
            "norm_brand": "frito lay",
            "norm_name": "lays",
            "base_unit": "oz",
            "entries": [
                {
                    "upc": "028400055681",
                    "release_date": "2022-10-28",
                    "size": 10.0,
                    "unit": "oz",
                    "brand_owner": "FRITO-LAY, INC.",
                    "brand_name": "LAY'S",
                    "fdc_id": "12345",
                },
                ...
            ]
        }

    The entries list must be sorted by release_date.

    Args:
        product_group: Group of entries sharing the same brand+name+category.
        min_pct: Minimum decrease percentage to flag (default 3%).
        max_pct: Maximum decrease percentage to flag (default 40%).
                 Changes beyond this are likely data errors.

    Returns a list of change dicts for cases where a product appears in a
    later release with a different UPC and a significantly smaller size.
    """
    entries = product_group.get("entries", [])
    if len(entries) < 2:
        return []

    changes = []  # type: List[Dict[str, Any]]

    # Build a per-release snapshot: {release_date: {upc: (size, unit, entry)}}
    by_release = {}  # type: Dict[str, Dict[str, Tuple[float, str, Dict[str, Any]]]]
    for entry in entries:
        rd = entry["release_date"]
        if rd not in by_release:
            by_release[rd] = {}
        upc = entry["upc"]
        # Keep only first occurrence per (release, UPC)
        if upc not in by_release[rd]:
            by_release[rd][upc] = (entry["size"], entry["unit"], entry)

    releases = sorted(by_release.keys())
    if len(releases) < 2:
        return []

    # Compare consecutive releases for UPC turnover
    for i in range(1, len(releases)):
        old_release = releases[i - 1]
        new_release = releases[i]
        old_upcs = by_release[old_release]
        new_upcs = by_release[new_release]

        # Find UPCs that disappeared (not in new release)
        departed = set(old_upcs.keys()) - set(new_upcs.keys())
        # Find UPCs that appeared (not in old release)
        arrived = set(new_upcs.keys()) - set(old_upcs.keys())

        if not departed or not arrived:
            continue

        # For each departed UPC, compare with each arrived UPC
        for old_upc in departed:
            old_size, old_unit, old_entry = old_upcs[old_upc]
            old_base, old_base_unit = convert_to_base(old_size, old_unit)

            if old_base <= 0:
                continue

            for new_upc in arrived:
                new_size, new_unit, new_entry = new_upcs[new_upc]
                new_base, new_base_unit = convert_to_base(new_size, new_unit)

                if old_base_unit != new_base_unit:
                    continue

                pct = ((new_base - old_base) / old_base) * 100.0

                # Only flag decreases in realistic range
                if pct >= 0:
                    continue
                if abs(pct) < min_pct:
                    continue
                if abs(pct) > max_pct:
                    continue

                changes.append({
                    "norm_brand": product_group.get("norm_brand", ""),
                    "norm_name": product_group.get("norm_name", ""),
                    "brand_owner": new_entry.get("brand_owner", ""),
                    "brand_name": new_entry.get("brand_name", ""),
                    "category": product_group.get("category", ""),
                    "old_upc": old_upc,
                    "new_upc": new_upc,
                    "old_size": old_size,
                    "old_unit": old_unit,
                    "new_size": new_size,
                    "new_unit": new_unit,
                    "old_date": old_release,
                    "new_date": new_release,
                    "pct_change": round(pct, 2),
                    "old_fdc_id": old_entry.get("fdc_id", ""),
                    "new_fdc_id": new_entry.get("fdc_id", ""),
                })

    return changes


# ── Scraper class ─────────────────────────────────────────────────────────


class UsdaTurnoverAnalyzer(BaseScraper):
    """Detects product-turnover shrinkflation across USDA releases.

    Uses food.csv descriptions (loaded from pre-extracted JSON) to group
    products precisely by their full description, not just brand_name.
    This distinguishes e.g. "CAMPBELL'S SOUP TOMATO" from
    "CAMPBELL'S SLOW KETTLE SOUP CLAM CHOWDER".

    Falls back to brand_name grouping if the description lookup is not
    available.
    """

    scraper_name = "usda_turnover"
    source_type = "usda_turnover_change"

    def __init__(self, descriptions_path: Optional[str] = None) -> None:
        super().__init__()
        self._desc_path = descriptions_path or _DEFAULT_DESC_PATH

    @staticmethod
    def _load_descriptions(path: str) -> Dict[str, str]:
        """Load fdc_id → description lookup from pre-extracted JSON.

        Returns empty dict if file doesn't exist.
        """
        if not os.path.exists(path):
            return {}
        with open(path, "r") as f:
            return json.load(f)

    def fetch(
        self, cursor: Dict[str, Any], dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        """Stream all USDA records, group by brand+description+category, detect turnover."""
        client = get_client()
        last_id = cursor.get("last_id", "")

        # Load fdc_id → description lookup (from food.csv extraction)
        desc_map = self._load_descriptions(self._desc_path)
        using_descriptions = bool(desc_map)
        if using_descriptions:
            self.log.info(
                "Loaded %d fdc_id -> description mappings from %s",
                len(desc_map), self._desc_path,
            )
        else:
            self.log.warning(
                "No description file at %s — falling back to brand_name grouping. "
                "Run extract_food_descriptions.py first for precise matching.",
                self._desc_path,
            )

        # {(norm_brand, norm_name, category, base_unit): group_dict}
        groups = {}  # type: Dict[Tuple[str, str, str, str], Dict[str, Any]]
        total_rows = 0
        skipped_no_key = 0
        desc_hits = 0
        desc_misses = 0

        self.log.info(
            "Streaming USDA records for turnover analysis%s ...",
            " from id > %s" % last_id if last_id else "",
        )

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
                release_date = (row.get("source_date") or "")[:10]
                brand_owner = payload.get("brand_owner", "")
                brand_name = payload.get("brand_name", "")
                category = payload.get("branded_food_category", "")
                fdc_id = str(payload.get("fdc_id", ""))

                if not upc or size is None or not release_date:
                    continue

                norm_brand = normalize_brand(brand_owner)

                # Use food.csv description if available, else brand_name
                raw_desc = ""
                if using_descriptions and fdc_id in desc_map:
                    raw_desc = strip_size_from_description(desc_map[fdc_id])
                    desc_hits += 1
                else:
                    raw_desc = brand_name
                    if using_descriptions:
                        desc_misses += 1

                norm_name = normalize_description(raw_desc)

                if not norm_brand or not norm_name:
                    skipped_no_key += 1
                    continue

                base_unit = _base_unit_for(size_unit)
                # Group key: brand + description + category + unit
                key = (norm_brand, norm_name, category, base_unit)

                if key not in groups:
                    groups[key] = {
                        "brand_owner": brand_owner,
                        "brand_name": brand_name,
                        "category": category,
                        "norm_brand": norm_brand,
                        "norm_name": norm_name,
                        "base_unit": base_unit,
                        "entries": [],
                    }

                groups[key]["entries"].append({
                    "upc": upc,
                    "release_date": release_date,
                    "size": size,
                    "unit": size_unit,
                    "brand_owner": brand_owner,
                    "brand_name": brand_name,
                    "fdc_id": fdc_id,
                })

            total_rows += len(rows)
            last_id = rows[-1]["id"]

            if total_rows % _LOG_EVERY == 0:
                self.log.info(
                    "Streamed %d rows, %d product groups so far "
                    "(desc hits: %d, misses: %d)...",
                    total_rows, len(groups), desc_hits, desc_misses,
                )

            if len(rows) < _PAGE_SIZE:
                break

        self.log.info(
            "Streamed %d total rows (%d skipped no key), "
            "%d product groups (desc hits: %d, misses: %d). "
            "Detecting turnover changes...",
            total_rows, skipped_no_key, len(groups),
            desc_hits, desc_misses,
        )

        # Only analyze groups with multiple UPCs (potential turnover)
        all_changes = []  # type: List[Dict[str, Any]]
        multi_upc_groups = 0

        for key, group in groups.items():
            # Quick check: do entries span multiple UPCs?
            upcs_in_group = {e["upc"] for e in group["entries"]}
            if len(upcs_in_group) < 2:
                continue
            multi_upc_groups += 1

            # Sort entries by release date for chronological analysis
            group["entries"].sort(key=lambda e: e["release_date"])
            changes = detect_turnover_changes(group)
            all_changes.extend(changes)

        self.log.info(
            "USDA turnover: %d groups total, %d with multiple UPCs, "
            "%d turnover changes detected",
            len(groups), multi_upc_groups, len(all_changes),
        )

        return all_changes

    def source_id_for(self, item: Dict[str, Any]) -> str:
        return "usda_turn_{}_{}_{}_{}".format(
            item["old_upc"], item["new_upc"],
            item["old_date"], item["new_date"],
        )

    def source_url_for(self, item: Dict[str, Any]) -> Optional[str]:
        fdc_id = item.get("new_fdc_id", "")
        if fdc_id:
            return "https://fdc.nal.usda.gov/food-details/{}/branded".format(
                fdc_id
            )
        return None

    def source_date_for(self, item: Dict[str, Any]) -> Optional[str]:
        return item.get("new_date")

    def next_cursor(
        self, items: List[Dict[str, Any]], prev_cursor: Dict[str, Any]
    ) -> Dict[str, Any]:
        prev_total = int(prev_cursor.get("total_changes", 0))
        return {
            "last_id": "",
            "total_changes": prev_total + len(items),
        }
