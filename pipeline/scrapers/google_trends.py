"""Google Trends scraper — monthly interest scores for shrinkflation.

Fetches the time series for one or more search keywords from Google's
unofficial Trends JSON endpoint and upserts the result into
google_trends_data.

Trends scores are normalised 0-100 *within the fetched window*, so each
run effectively overwrites the previous series. The upsert uses the
unique constraint on (keyword, geo, observation_date) so the table
stays clean.

Resilience notes:
  - Google occasionally serves 429s or 502s — we retry with backoff.
  - Cookies are required (Google sets NID on first request and rejects
    follow-ups without it). We handle that with a single warmup GET.
  - If the API path stops working, we fall back to a manually exported
    CSV at $GOOGLE_TRENDS_CSV_PATH (the dashboard's CSV export). That
    way the chart line stays alive even if the scrape breaks.

Source layout:
    https://trends.google.com/trends/api/explore?…
    → returns widget tokens (one per widget)
    https://trends.google.com/trends/api/widgetdata/multiline?…
    → returns the actual time series, JSON-prefixed with ")]}',"

This module deliberately doesn't take pytrends as a dep — pytrends has
churned its API surface several times and the same auth flow is tiny
to inline. Keeps requirements.txt thin.
"""
import csv
import io
import json
import os
import time
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import requests

from pipeline.config import USER_AGENT
from pipeline.lib.logging_setup import get_logger
from pipeline.lib.supabase_client import get_client
from pipeline.scrapers.base import BaseScraper

log = get_logger("google_trends")

TRENDS_BASE = "https://trends.google.com/trends"
EXPLORE_URL = TRENDS_BASE + "/api/explore"
MULTILINE_URL = TRENDS_BASE + "/api/widgetdata/multiline"

# Default keywords. Add more here as we want more chart lines.
DEFAULT_KEYWORDS = ["shrinkflation"]

# 5-year window — long enough to show the 2022 awareness spike, short
# enough that the monthly buckets give us ~60 data points (not too noisy).
DEFAULT_TIMEFRAME = "today 5-y"
DEFAULT_GEO = ""  # worldwide

_REQUEST_DELAY = 1.5  # seconds — politeness, Google rate-limits hard
_MAX_RETRIES = 4
_BACKOFF_BASE = 4


def aggregate_timeline_to_monthly(timeline):
    # type: (List[Dict[str, Any]]) -> List[Tuple[date, float]]
    """Collapse a Google Trends timelineData payload to month-start points.

    Google's bucket size flips between weekly and monthly depending on the
    requested window — `today 5-y` is right on the boundary. Snapping each
    row to month-start without aggregating would emit duplicate
    (keyword, geo, observation_date) keys in one upsert batch and trip the
    Postgres "ON CONFLICT DO UPDATE … cannot affect row a second time"
    error. We average weekly values within their month so the chart line
    matches what monthly bucketing would have produced.
    """
    buckets = {}  # type: Dict[date, Tuple[float, int]]
    for row in timeline:
        ts = row.get("time")
        value_list = row.get("value") or [0]
        if not ts:
            continue
        try:
            d = datetime.fromtimestamp(int(ts), tz=timezone.utc).date()
        except (ValueError, TypeError):
            continue
        v = float(value_list[0]) if value_list else 0.0
        month_start = d.replace(day=1)
        s, c = buckets.get(month_start, (0.0, 0))
        buckets[month_start] = (s + v, c + 1)
    return [(m, s / c) for m, (s, c) in sorted(buckets.items())]


class GoogleTrendsScraper(BaseScraper):
    """Scrapes Google Trends monthly interest for tracked keywords."""

    scraper_name = "google_trends"
    source_type = "google_trends"

    def __init__(self) -> None:
        super().__init__()
        self.session = requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT
        # Warmup — pulls a Google cookie (NID) onto the session so the
        # JSON endpoints stop returning 429.
        try:
            self.session.get(TRENDS_BASE + "/explore", timeout=20)
        except requests.RequestException as e:
            log.warning("Trends warmup failed: %s", e)

    # ── BaseScraper API ──────────────────────────────────────────────────

    def fetch(self, cursor, dry_run=False):
        # type: (Dict[str, Any], bool) -> List[Dict[str, Any]]
        """Pulls monthly interest for each configured keyword."""
        keywords = cursor.get("keywords") or DEFAULT_KEYWORDS
        geo = cursor.get("geo", DEFAULT_GEO)
        timeframe = cursor.get("timeframe", DEFAULT_TIMEFRAME)

        items = []
        for kw in keywords:
            try:
                points = self._fetch_keyword(kw, geo, timeframe)
            except Exception as e:
                log.warning("fetch failed for %s: %s — trying CSV fallback", kw, e)
                points = self._csv_fallback(kw)
            for d, v in points:
                items.append({
                    "keyword": kw,
                    "observation_date": d.isoformat(),
                    "value": v,
                    "geo": geo,
                    "timeframe": timeframe,
                })
        log.info("Collected %d monthly points across %d keywords",
                 len(items), len(keywords))
        return items

    def source_id_for(self, item):
        # type: (Dict[str, Any]) -> str
        return "{}:{}:{}".format(
            item.get("keyword", ""),
            item.get("geo", ""),
            item.get("observation_date", ""),
        )

    def next_cursor(self, items, prev_cursor):
        # type: (List[Dict[str, Any]], Dict[str, Any]) -> Dict[str, Any]
        nc = dict(prev_cursor or {})
        nc["last_run_at"] = datetime.now(timezone.utc).isoformat()
        return nc

    # ── Custom store: writes to google_trends_data, not raw_items ────────

    def store(self, items):
        # type: (List[Dict[str, Any]]) -> int
        if not items:
            return 0
        client = get_client()
        # Upsert in batches of 200 against the (keyword, geo, observation_date)
        # unique constraint. on_conflict updates value + fetched_at.
        now = datetime.now(timezone.utc).isoformat()
        for i in range(0, len(items), 200):
            chunk = items[i:i + 200]
            payload = [
                {
                    "keyword": r["keyword"],
                    "observation_date": r["observation_date"],
                    "value": r["value"],
                    "geo": r["geo"],
                    "timeframe": r["timeframe"],
                    "fetched_at": now,
                }
                for r in chunk
            ]
            (client.table("google_trends_data")
             .upsert(payload, on_conflict="keyword,geo,observation_date")
             .execute())
        log.info("Upserted %d google_trends_data rows", len(items))
        return len(items)

    # ── Implementation details ───────────────────────────────────────────

    def _fetch_keyword(self, keyword, geo, timeframe):
        # type: (str, str, str) -> List[Tuple[date, float]]
        req_payload = {
            "comparisonItem": [{"keyword": keyword, "geo": geo, "time": timeframe}],
            "category": 0,
            "property": "",
        }
        params = {
            "hl": "en-US",
            "tz": "0",
            "req": json.dumps(req_payload, separators=(",", ":")),
        }
        explore = self._retrying_get(EXPLORE_URL, params=params)
        # Trends responses are JSON prefixed with ")]}'," — strip it.
        widgets = self._strip_xssi_prefix(explore.text)
        try:
            decoded = json.loads(widgets)
        except json.JSONDecodeError:
            raise RuntimeError("explore response not JSON: {}".format(widgets[:200]))

        timeseries_widget = None
        for w in decoded.get("widgets", []):
            if w.get("id") == "TIMESERIES":
                timeseries_widget = w
                break
        if not timeseries_widget:
            raise RuntimeError("No TIMESERIES widget in explore response")

        token = timeseries_widget["token"]
        widget_req = timeseries_widget["request"]
        multiline_params = {
            "hl": "en-US",
            "tz": "0",
            "req": json.dumps(widget_req, separators=(",", ":")),
            "token": token,
        }
        time.sleep(_REQUEST_DELAY)
        ml = self._retrying_get(MULTILINE_URL, params=multiline_params)
        body = json.loads(self._strip_xssi_prefix(ml.text))
        timeline = body.get("default", {}).get("timelineData", []) or []

        return aggregate_timeline_to_monthly(timeline)

    def _csv_fallback(self, keyword):
        # type: (str) -> List[Tuple[date, float]]
        """Read a manually-exported CSV if the live API fails. The CSV
        is whatever you get from trends.google.com's "download" button —
        two columns: Month (YYYY-MM), Interest. Header row tolerated."""
        path = os.environ.get("GOOGLE_TRENDS_CSV_PATH")
        if not path or not os.path.exists(path):
            log.warning("No GOOGLE_TRENDS_CSV_PATH fallback available for %s", keyword)
            return []
        out = []  # type: List[Tuple[date, float]]
        with open(path) as f:
            for raw in csv.reader(f):
                if not raw or len(raw) < 2:
                    continue
                head = raw[0].strip()
                if not head or not head[0].isdigit():
                    continue
                try:
                    d = datetime.strptime(head + "-01", "%Y-%m-%d").date()
                    v = float(raw[1].strip())
                except (ValueError, TypeError):
                    continue
                out.append((d, v))
        log.info("CSV fallback delivered %d points for %s", len(out), keyword)
        return out

    def _retrying_get(self, url, params=None):
        # type: (str, Optional[Dict[str, Any]]) -> requests.Response
        last = None
        for attempt in range(_MAX_RETRIES):
            try:
                resp = self.session.get(url, params=params, timeout=30)
                if resp.status_code == 200:
                    return resp
                last = "HTTP {}".format(resp.status_code)
            except requests.RequestException as e:
                last = str(e)
            sleep = _BACKOFF_BASE ** attempt
            log.warning("GET %s failed (%s), retry %d/%d in %ds",
                        url, last, attempt + 1, _MAX_RETRIES, sleep)
            time.sleep(sleep)
        raise RuntimeError("GET {} failed after retries: {}".format(url, last))

    @staticmethod
    def _strip_xssi_prefix(text):
        # type: (str) -> str
        return text.lstrip(")]}'").lstrip(",").lstrip()
