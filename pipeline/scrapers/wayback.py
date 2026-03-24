"""Wayback Machine historical product page scraper.

Fetches archived snapshots of retail product pages from the Internet Archive
to build historical size/weight timelines for known shrinkflation offenders.

This is a **targeted investigation tool**, not a bulk discovery scraper.
Given a list of product URLs, it queries the CDX API for snapshots, fetches
the archived HTML, and extracts size/weight data from each snapshot.

Supported retailers: Walmart, Amazon, Kroger, Target, Open Food Facts, USDA FDC.

Usage:
    python -m pipeline wayback          # live run (top 3 products)
    python -m pipeline wayback --dry-run
"""
import hashlib
import re
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from pipeline.config import (
    USER_AGENT,
    WAYBACK_CDX_API,
    WAYBACK_ARCHIVE_BASE,
    WAYBACK_CDX_RPS,
    WAYBACK_FETCH_RPS,
    WAYBACK_FETCH_TIMEOUT,
)
from pipeline.lib.http_client import RateLimitedSession
from pipeline.lib.logging_setup import get_logger
from pipeline.lib.units import normalize_unit, parse_package_weight
from pipeline.scrapers.base import BaseScraper

log = get_logger("wayback")

# ── Wayback Machine settings (from config) ──────────────────────────────────

_CDX_RPS = WAYBACK_CDX_RPS
_FETCH_RPS = WAYBACK_FETCH_RPS
_CDX_API = WAYBACK_CDX_API
_ARCHIVE_BASE = WAYBACK_ARCHIVE_BASE


# ═════════════════════════════════════════════════════════════════════════════
# Retailer detection
# ═════════════════════════════════════════════════════════════════════════════

def detect_retailer(url):
    # type: (str) -> str
    """Detect retailer from URL.  Returns a key like 'walmart', 'amazon', etc."""
    url_lower = url.lower()
    if "walmart.com" in url_lower:
        return "walmart"
    if "amazon.com" in url_lower:
        return "amazon"
    if "kroger.com" in url_lower:
        return "kroger"
    if "target.com" in url_lower:
        return "target"
    if "openfoodfacts.org" in url_lower:
        return "openfoodfacts"
    if "fdc.nal.usda.gov" in url_lower:
        return "usda_fdc"
    return "generic"


# ═════════════════════════════════════════════════════════════════════════════
# Shared extraction patterns
# ═════════════════════════════════════════════════════════════════════════════

# JSON-LD structured data (Schema.org — works across many retailers)
_JSON_LD_PATTERN = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.DOTALL | re.IGNORECASE,
)

_JSON_WEIGHT_PATTERN = re.compile(
    r'"(?:weight|size|netContent)"\s*:\s*\{[^}]*'
    r'"value"\s*:\s*"?(\d+(?:\.\d+)?)"?[^}]*'
    r'"unitText"\s*:\s*"([^"]+)"',
    re.DOTALL,
)

# Page title
_TITLE_PATTERN = re.compile(
    r'<title[^>]*>(.*?)</title>',
    re.DOTALL | re.IGNORECASE,
)

# og:title meta tag
_OG_TITLE_PATTERN = re.compile(
    r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\']([^"\']*)["\']',
    re.IGNORECASE,
)

# Generic spec-label patterns (work across most retailers)
_GENERIC_SPEC_PATTERNS = [
    re.compile(
        r'(?:net\s*weight|net\s*wt|size|volume|quantity|total\s*weight|package\s*size)'
        r'[:\s]*(\d+(?:\.\d+)?\s*'
        r'(?:fl\.?\s*oz|oz|lb|lbs|g|kg|ml|l|ct|count|sheets|rolls|gal|qt|pt))',
        re.IGNORECASE,
    ),
    re.compile(
        r'<meta[^>]*(?:name|property)=["\']product:weight["\'][^>]*content=["\']([^"\']*)["\']',
        re.IGNORECASE,
    ),
]


# ═════════════════════════════════════════════════════════════════════════════
# Retailer-specific extractors
# ═════════════════════════════════════════════════════════════════════════════

def _extract_walmart(html):
    # type: (str) -> Tuple[Optional[float], Optional[str], Optional[str]]
    """Walmart-specific extraction patterns."""
    # Walmart data attributes
    m = re.search(r'data-product-size=["\']([^"\']+)["\']', html, re.IGNORECASE)
    if m:
        size, unit = parse_package_weight(m.group(1))
        if size is not None:
            return size, unit, "walmart_data_attr"

    # Walmart specification rows: <td>Net Weight</td><td>9.25 OZ</td>
    m = re.search(
        r'(?:Net\s*Weight|Package\s*Size|Size)[^<]*</(?:td|th|dt|span)>\s*'
        r'<(?:td|dd|span)[^>]*>\s*([^<]+)',
        html, re.IGNORECASE,
    )
    if m:
        size, unit = parse_package_weight(m.group(1).strip())
        if size is not None:
            return size, unit, "walmart_spec_row"

    return None, None, None


def _extract_amazon(html):
    # type: (str) -> Tuple[Optional[float], Optional[str], Optional[str]]
    """Amazon-specific extraction patterns."""
    # Amazon detail table: "Package Information" / "Item Weight" / "Size" rows
    for label in [
        "Size", "Package Information", "Item Weight", "Net Content",
        "Net Quantity", "Unit Count", "Item Package Quantity",
    ]:
        pattern = re.compile(
            r'(?:<th[^>]*>|<span[^>]*class="[^"]*label[^"]*"[^>]*>)\s*'
            + re.escape(label)
            + r'\s*</(?:th|span)>\s*<(?:td|span)[^>]*>\s*([^<]+)',
            re.IGNORECASE,
        )
        m = pattern.search(html)
        if m:
            size, unit = parse_package_weight(m.group(1).strip())
            if size is not None:
                return size, unit, "amazon_detail_table"

    # Amazon "a-size-base" spans near size/weight info
    m = re.search(
        r'(?:Size|Weight|Volume|Count)[:\s]*</span>\s*<span[^>]*>\s*'
        r'(\d+(?:\.\d+)?\s*(?:fl\.?\s*oz|oz|lb|g|kg|ml|l|ct|count|pack))',
        html, re.IGNORECASE,
    )
    if m:
        size, unit = parse_package_weight(m.group(1))
        if size is not None:
            return size, unit, "amazon_span"

    # Amazon variation button text: "9.25 Ounce (Pack of 1)"
    m = re.search(
        r'(\d+(?:\.\d+)?)\s*(Ounce|Fl\s*Oz|Count|Pack)\s*\(Pack of \d+\)',
        html, re.IGNORECASE,
    )
    if m:
        size = float(m.group(1))
        unit = normalize_unit(m.group(2))
        return size, unit, "amazon_variation"

    return None, None, None


def _extract_kroger(html):
    # type: (str) -> Tuple[Optional[float], Optional[str], Optional[str]]
    """Kroger-specific extraction patterns."""
    # Kroger product detail: size in a "ProductDetails-header" or similar block
    # "Doritos Nacho Cheese Tortilla Chips - 9.25 oz"
    m = re.search(
        r'class="[^"]*(?:ProductDetails|product-title|kds-Heading)[^"]*"[^>]*>'
        r'\s*([^<]+)',
        html, re.IGNORECASE,
    )
    if m:
        size, unit = parse_package_weight(m.group(1).strip())
        if size is not None:
            return size, unit, "kroger_heading"

    # Kroger UPC-detail block: "Size: 9.25 OZ"
    m = re.search(
        r'(?:Size|Weight|Net\s*Wt)[:\s]*</(?:span|dt|th)>\s*'
        r'<(?:span|dd|td)[^>]*>\s*([^<]+)',
        html, re.IGNORECASE,
    )
    if m:
        size, unit = parse_package_weight(m.group(1).strip())
        if size is not None:
            return size, unit, "kroger_spec"

    # Kroger JSON in page: "productSize":"9.25 oz"
    m = re.search(
        r'"(?:productSize|size|sellBy)"\s*:\s*"([^"]+)"',
        html,
    )
    if m:
        size, unit = parse_package_weight(m.group(1))
        if size is not None:
            return size, unit, "kroger_json"

    return None, None, None


def _extract_target(html):
    # type: (str) -> Tuple[Optional[float], Optional[str], Optional[str]]
    """Target-specific extraction patterns."""
    # Target product title in h1 or data-test="product-title"
    m = re.search(
        r'data-test=["\']product-title["\'][^>]*>([^<]+)',
        html, re.IGNORECASE,
    )
    if m:
        size, unit = parse_package_weight(m.group(1).strip())
        if size is not None:
            return size, unit, "target_title_attr"

    # Target specification rows
    m = re.search(
        r'(?:Net [Ww]eight|Package Quantity|Size)[:\s]*</(?:span|b|div)>\s*'
        r'<(?:span|div)[^>]*>\s*([^<]+)',
        html, re.IGNORECASE,
    )
    if m:
        size, unit = parse_package_weight(m.group(1).strip())
        if size is not None:
            return size, unit, "target_spec"

    # Target uses Redux state JSON embedded in page
    m = re.search(
        r'"package_quantity"\s*:\s*"([^"]+)"',
        html,
    )
    if m:
        size, unit = parse_package_weight(m.group(1))
        if size is not None:
            return size, unit, "target_json"

    # Target net_weight field in JSON
    m = re.search(
        r'"net_weight"\s*:\s*"([^"]+)"',
        html,
    )
    if m:
        size, unit = parse_package_weight(m.group(1))
        if size is not None:
            return size, unit, "target_json"

    return None, None, None


def _extract_openfoodfacts(html):
    # type: (str) -> Tuple[Optional[float], Optional[str], Optional[str]]
    """Open Food Facts-specific extraction patterns."""
    # OFF has clean, stable markup: <span id="field_quantity_value">340 g</span>
    m = re.search(
        r'id=["\']field_quantity_value["\'][^>]*>\s*([^<]+)',
        html, re.IGNORECASE,
    )
    if m:
        size, unit = parse_package_weight(m.group(1).strip())
        if size is not None:
            return size, unit, "off_quantity_field"

    # OFF also uses: "Quantity: 340 g" in plain text
    m = re.search(
        r'Quantity[:\s]*(\d+(?:\.\d+)?\s*(?:fl\.?\s*oz|oz|lb|g|kg|ml|l|ct))',
        html, re.IGNORECASE,
    )
    if m:
        size, unit = parse_package_weight(m.group(1))
        if size is not None:
            return size, unit, "off_quantity_text"

    # OFF JSON-LD or embedded product data
    m = re.search(
        r'"product_quantity"\s*:\s*"?(\d+(?:\.\d+)?)"?',
        html,
    )
    if m:
        # OFF stores quantity in grams by default
        try:
            size = float(m.group(1))
            return size, "g", "off_json"
        except ValueError:
            pass

    return None, None, None


def _extract_usda_fdc(html):
    # type: (str) -> Tuple[Optional[float], Optional[str], Optional[str]]
    """USDA FoodData Central-specific extraction patterns."""
    # USDA FDC: "Package Weight: 9.25 oz" in detail page
    m = re.search(
        r'Package\s*Weight[:\s]*([^<]+)',
        html, re.IGNORECASE,
    )
    if m:
        size, unit = parse_package_weight(m.group(1).strip())
        if size is not None:
            return size, unit, "usda_package_weight"

    # USDA FDC specification table
    m = re.search(
        r'(?:Serving\s*Size|Household\s*Serving)[^<]*</(?:td|th|span)>\s*'
        r'<(?:td|span)[^>]*>\s*([^<]+)',
        html, re.IGNORECASE,
    )
    if m:
        size, unit = parse_package_weight(m.group(1).strip())
        if size is not None:
            return size, unit, "usda_serving"

    # USDA FDC embedded JSON: "packageWeight":"9.25 oz"
    m = re.search(
        r'"(?:packageWeight|householdServingFullText|servingSize)"\s*:\s*"([^"]+)"',
        html,
    )
    if m:
        size, unit = parse_package_weight(m.group(1))
        if size is not None:
            return size, unit, "usda_json"

    return None, None, None


# ═════════════════════════════════════════════════════════════════════════════
# Unified extraction dispatcher
# ═════════════════════════════════════════════════════════════════════════════

# Map retailer keys to their specialist extractors
_RETAILER_EXTRACTORS = {
    "walmart": _extract_walmart,
    "amazon": _extract_amazon,
    "kroger": _extract_kroger,
    "target": _extract_target,
    "openfoodfacts": _extract_openfoodfacts,
    "usda_fdc": _extract_usda_fdc,
}  # type: Dict[str, Any]


def extract_size_from_html(html, url=""):
    # type: (str, str) -> Tuple[Optional[float], Optional[str], Optional[str]]
    """Extract product size/weight from archived HTML.

    Uses a layered approach:
      1. JSON-LD structured data (Schema.org — works across all retailers)
      2. Retailer-specific extraction (site-aware patterns)
      3. Page title parsing (universal fallback)
      4. Generic spec-label patterns
      5. Body text scan (last resort)

    Returns (size, unit, extraction_method) or (None, None, None).
    """
    if not html:
        return None, None, None

    retailer = detect_retailer(url)

    # ── Layer 1: JSON-LD structured data ─────────────────────────────────
    for match in _JSON_LD_PATTERN.finditer(html):
        json_text = match.group(1)
        weight_match = _JSON_WEIGHT_PATTERN.search(json_text)
        if weight_match:
            try:
                size = float(weight_match.group(1))
                unit_text = weight_match.group(2).strip()
                unit = normalize_unit(unit_text)
                return size, unit, "json_ld"
            except (ValueError, TypeError):
                pass

    # ── Layer 2: Retailer-specific extraction ────────────────────────────
    extractor = _RETAILER_EXTRACTORS.get(retailer)
    if extractor is not None:
        size, unit, method = extractor(html)
        if size is not None:
            return size, unit, method

    # ── Layer 3: Page title ──────────────────────────────────────────────
    # Try og:title first (more reliable), then <title>
    og_match = _OG_TITLE_PATTERN.search(html)
    if og_match:
        og_text = og_match.group(1).strip()
        og_text = og_text.replace("&amp;", "&").replace("&#39;", "'")
        size, unit = parse_package_weight(og_text)
        if size is not None:
            return size, unit, "og_title"

    title_match = _TITLE_PATTERN.search(html)
    if title_match:
        title_text = title_match.group(1).strip()
        title_text = title_text.replace("&amp;", "&").replace("&#39;", "'")
        size, unit = parse_package_weight(title_text)
        if size is not None:
            return size, unit, "title"

    # ── Layer 4: Generic spec-label patterns ─────────────────────────────
    for pattern in _GENERIC_SPEC_PATTERNS:
        spec_match = pattern.search(html)
        if spec_match:
            spec_text = spec_match.group(1).strip()
            size, unit = parse_package_weight(spec_text)
            if size is not None:
                return size, unit, "spec_label"

    # ── Layer 5: Body text scan (last resort) ────────────────────────────
    body_match = re.search(
        r'<body[^>]*>(.*?)</body>',
        html[:50000],
        re.DOTALL | re.IGNORECASE,
    )
    if body_match:
        body_text = re.sub(r'<[^>]+>', ' ', body_match.group(1))
        size_label = re.search(
            r'(?:net\s*(?:wt|weight)|size|volume|contents?)'
            r'[:\s]+(\d+(?:\.\d+)?\s*\w+)',
            body_text,
            re.IGNORECASE,
        )
        if size_label:
            size, unit = parse_package_weight(size_label.group(1))
            if size is not None:
                return size, unit, "body_text"

    return None, None, None


# ═════════════════════════════════════════════════════════════════════════════
# Target products for POC
# ═════════════════════════════════════════════════════════════════════════════
# Top 3 repeat offenders from claims data, with URLs across all 6 retailers.

POC_TARGETS = [
    {
        "brand": "Frito-Lay",
        "product_name": "Doritos Nacho Cheese",
        "upc": "028400090506",
        "category": "Snacks",
        "urls": [
            # Walmart
            "https://www.walmart.com/ip/Doritos-Nacho-Cheese-Flavored-Tortilla-Chips-9-25-oz/433078695",
            "https://www.walmart.com/ip/Doritos-Nacho-Cheese-Tortilla-Chips-Party-Size-14-5-oz/10535170",
            # Amazon
            "https://www.amazon.com/dp/B00HXIXW6U",
            # Kroger
            "https://www.kroger.com/p/doritos-nacho-cheese-flavored-tortilla-chips/0002840009050",
            # Target
            "https://www.target.com/p/doritos-nacho-cheese-chips/-/A-12959553",
            # Open Food Facts
            "https://world.openfoodfacts.org/product/0028400090506",
            # USDA FDC
            "https://fdc.nal.usda.gov/food-details/2646102/branded",
        ],
    },
    {
        "brand": "Tropicana",
        "product_name": "Tropicana Pure Premium Orange Juice",
        "upc": "048500205020",
        "category": "Beverages",
        "urls": [
            # Walmart
            "https://www.walmart.com/ip/Tropicana-Pure-Premium-No-Pulp-100-Orange-Juice-52-fl-oz/10451188",
            "https://www.walmart.com/ip/Tropicana-Pure-Premium-Some-Pulp-100-Orange-Juice-89-fl-oz/10451197",
            # Amazon
            "https://www.amazon.com/dp/B000WGRF4U",
            # Kroger
            "https://www.kroger.com/p/tropicana-pure-premium-no-pulp-orange-juice/0004850020502",
            # Target
            "https://www.target.com/p/tropicana-pure-premium-no-pulp-orange-juice/-/A-12953581",
            # Open Food Facts
            "https://world.openfoodfacts.org/product/0048500205020",
            # USDA FDC
            "https://fdc.nal.usda.gov/food-details/2344949/branded",
        ],
    },
    {
        "brand": "General Mills",
        "product_name": "Cheerios Original",
        "upc": "016000275263",
        "category": "Cereals",
        "urls": [
            # Walmart
            "https://www.walmart.com/ip/Cheerios-Heart-Healthy-Cereal-Gluten-Free-Cereal-With-Whole-Grain-Oats-18-oz/10311453",
            "https://www.walmart.com/ip/General-Mills-Cheerios-Cereal-8-9-oz/10311388",
            # Amazon
            "https://www.amazon.com/dp/B00I5QBK2K",
            # Kroger
            "https://www.kroger.com/p/cheerios-gluten-free-cereal/0001600027526",
            # Target
            "https://www.target.com/p/cheerios-cereal/-/A-12959225",
            # Open Food Facts
            "https://world.openfoodfacts.org/product/0016000275263",
            # USDA FDC
            "https://fdc.nal.usda.gov/food-details/2508096/branded",
        ],
    },
]


# ═════════════════════════════════════════════════════════════════════════════
# Scraper
# ═════════════════════════════════════════════════════════════════════════════

class WaybackScraper(BaseScraper):
    """Fetch archived product pages from the Wayback Machine.

    For each target product URL, queries the CDX API for monthly snapshots,
    fetches the archived HTML, extracts size/weight, and stores results
    in raw_items with source_type='wayback'.

    Can run in two modes:
      1. Default: processes the built-in POC_TARGETS list
      2. Ad-hoc:  pass --url (one or more URLs) with --brand and --product
                  to investigate any product on the fly

    Examples:
        # Default POC targets
        python -m pipeline wayback --dry-run

        # Investigate a specific product by URL(s)
        python -m pipeline wayback \\
            --url https://www.walmart.com/ip/Oreo-Cookies/123456 \\
            --url https://www.amazon.com/dp/B00EXAMPLE \\
            --brand "Mondelez" --product "Oreo Original"

        # Single URL, minimal metadata
        python -m pipeline wayback --url https://www.target.com/p/test/-/A-123
    """

    scraper_name = "wayback"
    source_type = "wayback"

    def __init__(self, urls=None, brand=None, product_name=None,
                 upc=None, category=None):
        # type: (Optional[List[str]], Optional[str], Optional[str], Optional[str], Optional[str]) -> None
        super().__init__()
        self._cdx_session = RateLimitedSession(
            requests_per_second=_CDX_RPS,
            user_agent=USER_AGENT,
        )
        self._fetch_session = RateLimitedSession(
            requests_per_second=_FETCH_RPS,
            user_agent=USER_AGENT,
            timeout=WAYBACK_FETCH_TIMEOUT,
        )
        # Ad-hoc target overrides (set via CLI args)
        self._adhoc_urls = urls
        self._adhoc_brand = brand
        self._adhoc_product = product_name
        self._adhoc_upc = upc
        self._adhoc_category = category

    def _resolve_targets(self):
        # type: () -> List[Dict[str, Any]]
        """Build the target list — either from CLI args or POC defaults."""
        if self._adhoc_urls:
            return [{
                "brand": self._adhoc_brand or "Unknown",
                "product_name": self._adhoc_product or "Unknown Product",
                "upc": self._adhoc_upc,
                "category": self._adhoc_category,
                "urls": self._adhoc_urls,
            }]
        return POC_TARGETS

    def fetch(self, cursor, dry_run=False):
        # type: (Dict[str, Any], bool) -> List[Dict[str, Any]]
        """For each target product, query CDX and fetch archived snapshots."""
        items = []  # type: List[Dict[str, Any]]
        targets = self._resolve_targets()

        for target in targets:
            brand = target["brand"]
            product_name = target["product_name"]
            self.log.info(
                "Processing: %s — %s (%d URLs)",
                brand, product_name, len(target["urls"]),
            )

            for url in target["urls"]:
                retailer = detect_retailer(url)
                snapshots = self._query_cdx(url)
                self.log.info(
                    "  [%s] %s: %d unique snapshots",
                    retailer, url[:80], len(snapshots),
                )

                for snapshot in snapshots:
                    timestamp = snapshot["timestamp"]
                    archived_url = "{}/{}id_/{}".format(
                        _ARCHIVE_BASE, timestamp, url,
                    )

                    if dry_run:
                        items.append(self._build_item(
                            target, url, retailer, snapshot,
                            None, None, None, None,
                        ))
                        continue

                    # Fetch the archived page
                    html = self._fetch_archived_page(archived_url)
                    if html is None:
                        self.log.debug(
                            "  Failed to fetch %s", archived_url[:100],
                        )
                        continue

                    # Extract size/weight
                    size, unit, method = extract_size_from_html(html, url)

                    item = self._build_item(
                        target, url, retailer, snapshot,
                        size, unit, method, len(html),
                    )
                    items.append(item)

                    if size is not None:
                        self.log.info(
                            "  [%s] %s %s (via %s)",
                            self._format_timestamp(timestamp),
                            size, unit, method,
                        )
                    else:
                        self.log.debug(
                            "  [%s] No size extracted",
                            self._format_timestamp(timestamp),
                        )

        self.log.info("Total items collected: %d", len(items))
        return items

    def source_id_for(self, item):
        # type: (Dict[str, Any]) -> str
        """Unique ID: wayback_{timestamp}_{url_hash}."""
        return "wayback_{}_{}".format(
            item["snapshot_timestamp"],
            item["url_hash"],
        )

    def source_url_for(self, item):
        # type: (Dict[str, Any]) -> Optional[str]
        return item.get("archived_url")

    def source_date_for(self, item):
        # type: (Dict[str, Any]) -> Optional[str]
        ts = item.get("snapshot_timestamp", "")
        if len(ts) >= 8:
            try:
                dt = datetime.strptime(ts[:14].ljust(14, "0"), "%Y%m%d%H%M%S")
                return dt.replace(tzinfo=timezone.utc).isoformat()
            except ValueError:
                pass
        return None

    def next_cursor(self, items, prev_cursor):
        # type: (List[Dict[str, Any]], Dict[str, Any]) -> Dict[str, Any]
        now = datetime.now(timezone.utc).isoformat()
        return {
            "last_run": now,
            "items_fetched": len(items),
            "targets_processed": len(POC_TARGETS),
        }

    # ── CDX API queries ──────────────────────────────────────────────────

    def _query_cdx(self, url):
        # type: (str) -> List[Dict[str, str]]
        """Query CDX API for all unique snapshots of a URL.

        Uses collapse=timestamp:6 for ~monthly granularity and
        digest deduplication to skip identical page captures.
        Returns list of dicts with 'timestamp', 'statuscode', 'digest'.
        """
        params = {
            "url": url,
            "output": "json",
            "fl": "timestamp,statuscode,digest,length",
            "filter": "statuscode:200",
            "collapse": "timestamp:6",  # one per month (YYYYMM)
            "limit": 500,
        }

        resp = self._cdx_session.get(
            _CDX_API,
            params=params,
            raise_for_status=False,
        )
        if resp is None:
            self.log.warning("CDX query failed for %s", url[:80])
            return []

        if resp.status_code == 429:
            self.log.warning("CDX rate limited — backing off 60s")
            time.sleep(60)
            return []

        if resp.status_code >= 400:
            self.log.warning(
                "CDX returned %d for %s", resp.status_code, url[:80],
            )
            return []

        try:
            data = resp.json()
        except Exception:
            self.log.warning("CDX JSON decode failed for %s", url[:80])
            return []

        if not data or len(data) < 2:
            return []

        # First row is headers, rest is data
        headers = data[0]
        snapshots = []
        seen_digests = set()  # type: set

        for row in data[1:]:
            record = dict(zip(headers, row))
            digest = record.get("digest", "")

            # Skip duplicate content even across months
            if digest in seen_digests:
                continue
            seen_digests.add(digest)

            snapshots.append(record)

        return snapshots

    def _fetch_archived_page(self, archived_url):
        # type: (str) -> Optional[str]
        """Fetch an archived page using the id_ modifier for raw content."""
        resp = self._fetch_session.get(
            archived_url,
            raise_for_status=False,
        )
        if resp is None:
            return None

        if resp.status_code == 429:
            self.log.warning("Archive fetch rate limited — backing off 30s")
            time.sleep(30)
            return None

        if resp.status_code >= 400:
            return None

        return resp.text

    # ── Helpers ──────────────────────────────────────────────────────────

    def _build_item(self, target, url, retailer, snapshot, size, unit, method, html_len):
        # type: (Dict[str, Any], str, str, Dict[str, str], Optional[float], Optional[str], Optional[str], Optional[int]) -> Dict[str, Any]
        """Build a raw_items payload dict."""
        url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
        timestamp = snapshot.get("timestamp", "")

        return {
            "snapshot_timestamp": timestamp,
            "url_hash": url_hash,
            "archived_url": "{}/{}id_/{}".format(
                _ARCHIVE_BASE, timestamp, url,
            ),
            "original_url": url,
            "retailer": retailer,
            "brand": target["brand"],
            "product_name": target["product_name"],
            "upc": target.get("upc"),
            "category": target.get("category"),
            "extracted_size": size,
            "extracted_unit": unit,
            "extraction_method": method,
            "html_length": html_len,
            "cdx_digest": snapshot.get("digest"),
            "cdx_length": snapshot.get("length"),
        }

    @staticmethod
    def _format_timestamp(ts):
        # type: (str) -> str
        """Format a CDX timestamp like '20230615142030' to '2023-06-15'."""
        if len(ts) >= 8:
            return "{}-{}-{}".format(ts[:4], ts[4:6], ts[6:8])
        return ts
