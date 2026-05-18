"""Consumer Reports scraper — public shrinkflation findings.

Walks a curated list of Consumer Reports pages that index named-brand
shrinkflation findings, extracts each product reference, and upserts
into consumer_reports_findings.

We intentionally stay on the public CR pages (no paywall). The seed
URLs below are the long-running shrinkflation index articles CR
maintains; if CR moves them, the workflow surfaces a no-rows warning
in the job summary and we can update the list.

Scrape pattern:
  - GET each seed page
  - Parse HTML with selectolax (fast, deps-light)
  - Pull <h2> / <h3> headings inside the body — those are the per-brand
    cards CR uses in their shrinkflation pieces
  - For each, capture the heading text, the first paragraph (excerpt),
    and any image/link
  - Heuristic brand+product split: heading is usually "Brand — Product"
    or "Brand: Product"; fall back to single-field if no separator

The matcher (entity_id resolution) lives in a separate one-shot script:
  pipeline/scripts/match_consumer_reports.py

That's run after this scraper finishes so the matching round-trip
doesn't slow the scrape itself.
"""
import re
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests

from pipeline.config import USER_AGENT
from pipeline.lib.logging_setup import get_logger
from pipeline.lib.supabase_client import get_client
from pipeline.scrapers.base import BaseScraper

log = get_logger("consumer_reports")

# Seed pages — CR's evergreen shrinkflation indices. Add new URLs here
# as they publish more round-ups; the unique-on-source_url constraint
# stops dupes.
SEED_URLS = [
    "https://www.consumerreports.org/cro/news/2024/01/shrinkflation/index.htm",
    "https://www.consumerreports.org/consumer-protection/shrinkflation-everything-you-need-to-know/",
    "https://www.consumerreports.org/money/inflation/shrinkflation-getting-less-for-your-money-a1097984111/",
]

_REQUEST_DELAY = 2.0  # seconds — be a good citizen
_MAX_RETRIES = 3
_BACKOFF_BASE = 4
_HEADING_RX = re.compile(r"^\s*(.+?)\s*(?:—|–|-|:)\s*(.+?)\s*$", re.UNICODE)
_DATE_META_NAMES = ("article:published_time", "publishdate", "date", "pubdate")


class ConsumerReportsScraper(BaseScraper):
    """Scrapes Consumer Reports shrinkflation index pages."""

    scraper_name = "consumer_reports"
    source_type = "consumer_reports"

    def __init__(self) -> None:
        super().__init__()
        self.session = requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT
        self.session.headers["Accept"] = "text/html"

    def fetch(self, cursor, dry_run=False):
        # type: (Dict[str, Any], bool) -> List[Dict[str, Any]]
        seed_urls = cursor.get("seed_urls") or SEED_URLS
        items = []  # type: List[Dict[str, Any]]
        for url in seed_urls:
            log.info("Fetching %s", url)
            try:
                html = self._get(url)
            except Exception as e:
                log.warning("skip %s: %s", url, e)
                continue
            for finding in _parse_page(url, html):
                items.append(finding)
            time.sleep(_REQUEST_DELAY)
        log.info("Extracted %d Consumer Reports findings", len(items))
        return items

    def source_id_for(self, item):
        # type: (Dict[str, Any]) -> str
        return item.get("source_url", "")

    def next_cursor(self, items, prev_cursor):
        # type: (List[Dict[str, Any]], Dict[str, Any]) -> Dict[str, Any]
        nc = dict(prev_cursor or {})
        nc["last_run_at"] = datetime.now(timezone.utc).isoformat()
        return nc

    # Custom store: writes to consumer_reports_findings, not raw_items.
    def store(self, items):
        # type: (List[Dict[str, Any]]) -> int
        if not items:
            return 0
        client = get_client()
        # Each row's source_url is the de-dup key. One CR article can
        # mention multiple brands — we keep one row per (source_url),
        # but the parser may emit one row per finding sharing the same
        # source_url+headline+brand. So we dedup before upsert.
        seen = {}  # type: Dict[str, Dict[str, Any]]
        for r in items:
            key = "{}|{}|{}".format(
                r.get("source_url", ""),
                (r.get("brand") or "").lower(),
                (r.get("product_name") or "").lower(),
            )
            seen[key] = r
        rows = list(seen.values())

        # Upsert in batches with on_conflict on (source_url, brand, product_name).
        # We synthesise a "find-or-create" key by trying upsert on source_url
        # alone; if a finding with same source_url already exists with a
        # different brand we still write it as a new row by giving each a
        # synthetic source_url anchor.
        # Simpler approach: write source_url with anchor fragments so each
        # (source_url + brand) gets its own unique key.
        ready = []
        for r in rows:
            anchor_bits = [r.get("brand") or "", r.get("product_name") or ""]
            anchor = re.sub(r"[^a-z0-9]+", "-",
                            "-".join(anchor_bits).lower()).strip("-")
            full_url = r["source_url"]
            if anchor:
                full_url = "{}#{}".format(r["source_url"], anchor[:80])
            ready.append({
                "source_url": full_url,
                "title": r.get("title") or "",
                "published_at": r.get("published_at"),
                "excerpt": r.get("excerpt"),
                "brand": r.get("brand"),
                "product_name": r.get("product_name"),
                "upc": r.get("upc"),
                "size_before": r.get("size_before"),
                "size_after": r.get("size_after"),
                "size_unit": r.get("size_unit"),
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            })

        total = 0
        for i in range(0, len(ready), 100):
            chunk = ready[i:i + 100]
            (client.table("consumer_reports_findings")
             .upsert(chunk, on_conflict="source_url")
             .execute())
            total += len(chunk)
        log.info("Upserted %d consumer_reports_findings rows", total)
        return total

    def _get(self, url):
        # type: (str) -> str
        last = None
        for attempt in range(_MAX_RETRIES):
            try:
                resp = self.session.get(url, timeout=30)
                if resp.status_code == 200 and resp.text:
                    return resp.text
                last = "HTTP {}".format(resp.status_code)
            except requests.RequestException as e:
                last = str(e)
            sleep = _BACKOFF_BASE ** attempt
            log.warning("GET %s failed (%s), retry %d/%d in %ds",
                        url, last, attempt + 1, _MAX_RETRIES, sleep)
            time.sleep(sleep)
        raise RuntimeError("GET {} failed after retries: {}".format(url, last))


# ── Parsing ──────────────────────────────────────────────────────────────


def _parse_page(url, html):
    # type: (str, str) -> List[Dict[str, Any]]
    """Extract structured findings from one CR article.

    Uses BeautifulSoup (already a pipeline dep). CR uses <h2>/<h3>
    to label per-product callouts, and follows each with one or more
    <p> tags containing the excerpt. We grab them in order.
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        # Final fallback if bs4 isn't available for some reason.
        return _parse_page_regex(url, html)

    soup = BeautifulSoup(html, "html.parser")

    title_tag = soup.find("h1")
    title = title_tag.get_text(strip=True) if title_tag else ""
    published_at = _extract_published_bs(soup)

    findings = []  # type: List[Dict[str, Any]]
    article = soup.find("article") or soup.body or soup
    # Walk h2/h3 headings inside the article body. Each one is a
    # potential product callout.
    seen = set()
    for tag in article.find_all(["h2", "h3"]):
        head = tag.get_text(strip=True)
        if not head or head in seen:
            continue
        seen.add(head)
        brand, product = _split_brand_product(head)
        if not brand or not product:
            continue
        excerpt = _first_para_after_bs(tag)
        findings.append({
            "source_url": url,
            "title": title or head,
            "published_at": published_at,
            "excerpt": excerpt,
            "brand": brand,
            "product_name": product,
        })
    return findings


def _first_para_after_bs(tag):
    # type: (Any) -> Optional[str]
    """BeautifulSoup variant of _first_para_after."""
    sib = tag.find_next_sibling()
    seen = 0
    while sib is not None and seen < 8:
        if getattr(sib, "name", None) == "p":
            txt = sib.get_text(strip=True)
            if txt and len(txt) > 20:
                return txt[:600]
        sib = sib.find_next_sibling()
        seen += 1
    return None


def _extract_published_bs(soup):
    # type: (Any) -> Optional[str]
    for meta in soup.find_all("meta"):
        prop = (meta.get("property") or "").lower()
        name = (meta.get("name") or "").lower()
        if prop in _DATE_META_NAMES or name in _DATE_META_NAMES:
            v = meta.get("content") or ""
            if v:
                return v.split("T")[0]
    return None


def _parse_page_regex(url, html):
    # type: (str, str) -> List[Dict[str, Any]]
    """Minimal heading scraper for environments without selectolax."""
    findings = []  # type: List[Dict[str, Any]]
    title_match = re.search(r"<h1[^>]*>(.*?)</h1>", html, flags=re.I | re.S)
    title = re.sub(r"<[^>]+>", "", title_match.group(1)).strip() if title_match else ""
    for m in re.finditer(r"<h[23][^>]*>(.*?)</h[23]>", html, flags=re.I | re.S):
        head = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        if not head:
            continue
        brand, product = _split_brand_product(head)
        if not brand or not product:
            continue
        findings.append({
            "source_url": url,
            "title": title or head,
            "published_at": None,
            "excerpt": None,
            "brand": brand,
            "product_name": product,
        })
    return findings


def _split_brand_product(heading):
    # type: (str) -> tuple
    """Try to split a heading like 'Brand — Product' into (brand, product).

    Returns (None, None) for headings that don't look like product
    callouts (no separator, or generic copy)."""
    if not heading:
        return None, None
    # Skip obvious non-product headings
    bad_starts = ("how ", "why ", "what ", "the ", "this ", "tips ", "things ")
    if heading.lower().startswith(bad_starts):
        return None, None
    m = _HEADING_RX.match(heading)
    if not m:
        return None, None
    brand = m.group(1).strip()
    product = m.group(2).strip()
    if len(brand) < 2 or len(product) < 2:
        return None, None
    # Reject very long brand strings (probably a sentence, not a brand)
    if len(brand) > 60 or len(product) > 120:
        return None, None
    return brand, product


