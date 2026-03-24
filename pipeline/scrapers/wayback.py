"""Wayback Machine historical product page scraper.

Fetches archived snapshots of retail product pages from the Internet Archive
to build historical size/weight timelines for known shrinkflation offenders.

This is a **targeted investigation tool**, not a bulk discovery scraper.
Given a list of product URLs, it queries the CDX API for snapshots, fetches
the archived HTML, and extracts size/weight data from each snapshot.

Usage:
    python -m pipeline wayback          # live run (top 3 products)
    python -m pipeline wayback --dry-run
"""
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
from pipeline.lib.units import parse_package_weight
from pipeline.scrapers.base import BaseScraper

log = get_logger("wayback")

# ── Wayback Machine settings (from config) ──────────────────────────────────

_CDX_RPS = WAYBACK_CDX_RPS
_FETCH_RPS = WAYBACK_FETCH_RPS
_CDX_API = WAYBACK_CDX_API
_ARCHIVE_BASE = WAYBACK_ARCHIVE_BASE

# ── Target products for POC ──────────────────────────────────────────────────
# Top 3 repeat offenders from claims data, with known retail URLs.
# Each entry: (brand, product_name, upc, [list of retail URLs to check])

POC_TARGETS = [
    {
        "brand": "Frito-Lay",
        "product_name": "Doritos Nacho Cheese",
        "upc": "028400090506",
        "category": "Snacks",
        "urls": [
            "https://www.walmart.com/ip/Doritos-Nacho-Cheese-Flavored-Tortilla-Chips-9-25-oz/433078695",
            "https://www.walmart.com/ip/Doritos-Nacho-Cheese-Tortilla-Chips-Party-Size-14-5-oz/10535170",
        ],
    },
    {
        "brand": "Tropicana",
        "product_name": "Tropicana Pure Premium Orange Juice",
        "upc": "048500205020",
        "category": "Beverages",
        "urls": [
            "https://www.walmart.com/ip/Tropicana-Pure-Premium-No-Pulp-100-Orange-Juice-52-fl-oz/10451188",
            "https://www.walmart.com/ip/Tropicana-Pure-Premium-Some-Pulp-100-Orange-Juice-89-fl-oz/10451197",
        ],
    },
    {
        "brand": "General Mills",
        "product_name": "Cheerios Original",
        "upc": "016000275263",
        "category": "Cereals",
        "urls": [
            "https://www.walmart.com/ip/Cheerios-Heart-Healthy-Cereal-Gluten-Free-Cereal-With-Whole-Grain-Oats-18-oz/10311453",
            "https://www.walmart.com/ip/General-Mills-Cheerios-Cereal-8-9-oz/10311388",
        ],
    },
]


# ── HTML Parsers ─────────────────────────────────────────────────────────────

# Walmart product pages embed structured data in JSON-LD and have size info
# in specific HTML patterns.  These patterns change over time, so we try
# multiple strategies.

# Pattern 1: JSON-LD structured data (modern Walmart pages, ~2020+)
_JSON_LD_PATTERN = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.DOTALL | re.IGNORECASE,
)

# Pattern 2: Product title containing size (e.g. "Doritos Nacho Cheese, 9.25 oz")
_TITLE_PATTERN = re.compile(
    r'<title[^>]*>(.*?)</title>',
    re.DOTALL | re.IGNORECASE,
)

# Pattern 3: Specific Walmart markup patterns for product specs
_SPEC_PATTERNS = [
    # "Net Weight: 9.25 oz" or "Size: 52 fl oz" in spec tables
    re.compile(
        r'(?:net\s*weight|size|volume|quantity|count)[:\s]*'
        r'(\d+(?:\.\d+)?\s*(?:fl\.?\s*oz|oz|lb|lbs|g|kg|ml|l|ct|count|sheets|rolls|gal|qt|pt))',
        re.IGNORECASE,
    ),
    # Generic product weight in meta tags
    re.compile(
        r'<meta[^>]*(?:name|property)=["\'](?:og:title|product:weight)["\'][^>]*content=["\']([^"\']*)["\']',
        re.IGNORECASE,
    ),
    # Walmart-specific data attributes
    re.compile(
        r'data-product-size=["\']([^"\']+)["\']',
        re.IGNORECASE,
    ),
]

# Pattern for extracting product name from JSON-LD
_JSON_NAME_PATTERN = re.compile(r'"name"\s*:\s*"([^"]+)"')
_JSON_WEIGHT_PATTERN = re.compile(
    r'"(?:weight|size|netContent)"\s*:\s*\{[^}]*"value"\s*:\s*"?(\d+(?:\.\d+)?)"?[^}]*"unitText"\s*:\s*"([^"]+)"',
    re.DOTALL,
)


def extract_size_from_html(html, url=""):
    # type: (str, str) -> Tuple[Optional[float], Optional[str], Optional[str]]
    """Extract product size/weight from archived HTML.

    Tries multiple strategies in order of reliability.
    Returns (size, unit, extraction_method) or (None, None, None).
    """
    if not html:
        return None, None, None

    # Strategy 1: JSON-LD structured data
    for match in _JSON_LD_PATTERN.finditer(html):
        json_text = match.group(1)
        weight_match = _JSON_WEIGHT_PATTERN.search(json_text)
        if weight_match:
            try:
                size = float(weight_match.group(1))
                unit_text = weight_match.group(2).strip()
                from pipeline.lib.units import normalize_unit
                unit = normalize_unit(unit_text)
                return size, unit, "json_ld"
            except (ValueError, TypeError):
                pass

    # Strategy 2: Parse size from page title
    title_match = _TITLE_PATTERN.search(html)
    if title_match:
        title_text = title_match.group(1).strip()
        # Clean HTML entities
        title_text = title_text.replace("&amp;", "&").replace("&#39;", "'")
        size, unit = parse_package_weight(title_text)
        if size is not None:
            return size, unit, "title"

    # Strategy 3: Spec table patterns
    for pattern in _SPEC_PATTERNS:
        spec_match = pattern.search(html)
        if spec_match:
            spec_text = spec_match.group(1).strip()
            size, unit = parse_package_weight(spec_text)
            if size is not None:
                return size, unit, "spec_table"

    # Strategy 4: Look for size anywhere in the first 50KB of page body
    # (broad fallback — less reliable but catches edge cases)
    body_match = re.search(
        r'<body[^>]*>(.*?)</body>',
        html[:50000],
        re.DOTALL | re.IGNORECASE,
    )
    if body_match:
        body_text = re.sub(r'<[^>]+>', ' ', body_match.group(1))
        # Look for explicit size labels
        size_label = re.search(
            r'(?:net\s*(?:wt|weight)|size|volume|contents?)[:\s]+(\d+(?:\.\d+)?\s*\w+)',
            body_text,
            re.IGNORECASE,
        )
        if size_label:
            size, unit = parse_package_weight(size_label.group(1))
            if size is not None:
                return size, unit, "body_text"

    return None, None, None


# ── Scraper ──────────────────────────────────────────────────────────────────

class WaybackScraper(BaseScraper):
    """Fetch archived product pages from the Wayback Machine.

    For each target product URL, queries the CDX API for monthly snapshots,
    fetches the archived HTML, extracts size/weight, and stores results
    in raw_items with source_type='wayback'.
    """

    scraper_name = "wayback"
    source_type = "wayback"

    def __init__(self):
        # type: () -> None
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

    def fetch(self, cursor, dry_run=False):
        # type: (Dict[str, Any], bool) -> List[Dict[str, Any]]
        """For each target product, query CDX and fetch archived snapshots."""
        items = []  # type: List[Dict[str, Any]]
        targets = POC_TARGETS

        for target in targets:
            brand = target["brand"]
            product_name = target["product_name"]
            self.log.info(
                "Processing: %s — %s (%d URLs)",
                brand, product_name, len(target["urls"]),
            )

            for url in target["urls"]:
                snapshots = self._query_cdx(url)
                self.log.info(
                    "  URL %s: %d unique snapshots", url[:80], len(snapshots),
                )

                for snapshot in snapshots:
                    timestamp = snapshot["timestamp"]
                    archived_url = "{}/{}id_/{}".format(
                        _ARCHIVE_BASE, timestamp, url,
                    )

                    if dry_run:
                        items.append(self._build_item(
                            target, url, snapshot, None, None, None, None,
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
                        target, url, snapshot, size, unit, method,
                        len(html),
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
        collapse=digest to skip identical page captures.
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

    def _build_item(self, target, url, snapshot, size, unit, method, html_len):
        # type: (Dict[str, Any], str, Dict[str, str], Optional[float], Optional[str], Optional[str], Optional[int]) -> Dict[str, Any]
        """Build a raw_items payload dict."""
        import hashlib
        url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
        timestamp = snapshot.get("timestamp", "")

        return {
            "snapshot_timestamp": timestamp,
            "url_hash": url_hash,
            "archived_url": "{}/{}id_/{}".format(
                _ARCHIVE_BASE, timestamp, url,
            ),
            "original_url": url,
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
