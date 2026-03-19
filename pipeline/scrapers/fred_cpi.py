"""FRED CPI scraper — monthly food price index data.

Fetches monthly Consumer Price Index observations from the Federal Reserve
Economic Data (FRED) for major food categories.  Used to provide macro price
context alongside product-level shrinkflation claims.

Data source:
    https://fred.stlouisfed.org
    Public CSV endpoint — no API key required.
    If FRED_API_KEY is set, uses the JSON API instead (more reliable).

Rate limits:
    Public CSV: no documented limit (uses 0.6s delay to be polite)
    JSON API:   120 requests/minute (0.6s delay keeps well under that)

Writes to fred_cpi_data (NOT raw_items — this is reference/context data,
not raw consumer reports).

Cursor schema:
    {"last_dates": {"CPIUFDNS": "2025-01-01", ...}}

    Tracks the latest observation date stored per series so incremental runs
    only need to check for new data points (CPI is released monthly).
"""
import csv
import io
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import requests

from pipeline.config import (
    FRED_API_BASE,
    FRED_API_KEY,
    FRED_CSV_BASE,
    FRED_DELAY,
    FRED_SERIES,
    DEFAULT_TIMEOUT,
)
from pipeline.lib.logging_setup import get_logger
from pipeline.lib.supabase_client import get_client, reset_client
from pipeline.scrapers.base import BaseScraper

log = get_logger("fred_cpi")

# FRED uses "." for missing values in CSV output
_FRED_MISSING = "."

# Retry config for transient HTTP errors
_MAX_RETRIES = 3
_RETRY_BASE_DELAY = 5  # seconds


class FredCpiScraper(BaseScraper):
    """Scraper for FRED food CPI time series.

    Fetches all series defined in FRED_SERIES on the first run (full history),
    then only new observations on subsequent runs (incremental).
    """

    scraper_name = "fred_cpi"
    source_type = "fred"

    def __init__(self) -> None:
        super().__init__()
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "FullCartsBot/2.0 (https://fullcarts.org; data pipeline)",
        })

    # ── BaseScraper interface ─────────────────────────────────────────────────

    def fetch(
        self, cursor: Dict[str, Any], dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        """Fetch CPI observations for all configured FRED series.

        On first run (empty cursor) fetches all available history.
        On subsequent runs fetches only observations after the last stored date.
        """
        last_dates = cursor.get("last_dates", {})
        all_items = []

        for series_id, series_name, category in FRED_SERIES:
            since = last_dates.get(series_id)
            self.log.info(
                "Fetching %s (%s) since=%s", series_id, series_name, since or "beginning"
            )

            observations = self._fetch_series(series_id, since)
            self.log.info("  → %d new observations for %s", len(observations), series_id)

            for obs_date, value in observations:
                all_items.append({
                    "_series_id": series_id,
                    "_series_name": series_name,
                    "_category": category,
                    "_observation_date": obs_date,
                    "_value": value,
                    "_source_url": f"https://fred.stlouisfed.org/series/{series_id}",
                })

            if len(FRED_SERIES) > 1:
                time.sleep(FRED_DELAY)

        return all_items

    def source_id_for(self, item: Dict[str, Any]) -> str:
        """Unique ID is series_id + observation_date."""
        return "{}_{}".format(item["_series_id"], item["_observation_date"])

    def next_cursor(
        self, items: List[Dict[str, Any]], prev_cursor: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Track the latest observation date per series."""
        last_dates = dict(prev_cursor.get("last_dates", {}))

        for item in items:
            sid = item["_series_id"]
            obs_date = item["_observation_date"]
            if sid not in last_dates or obs_date > last_dates[sid]:
                last_dates[sid] = obs_date

        return {"last_dates": last_dates}

    # ── Custom store (writes to fred_cpi_data, not raw_items) ────────────────

    def store(self, items: List[Dict[str, Any]]) -> int:
        """Upsert observations to fred_cpi_data table.

        Uses ON CONFLICT (series_id, observation_date) DO NOTHING so
        re-running is fully idempotent.
        """
        client = get_client()
        now = datetime.now(timezone.utc).isoformat()
        batch_size = 50
        total_new = 0

        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            rows = []
            for item in batch:
                rows.append({
                    "series_id": item["_series_id"],
                    "series_name": item["_series_name"],
                    "category": item["_category"],
                    "observation_date": item["_observation_date"],
                    "value": item["_value"],
                    "source_url": item["_source_url"],
                    "captured_at": now,
                })

            batch_num = i // batch_size
            resp = self._upsert_fred_with_retry(client, rows, batch_num)

            if resp is None:
                client = get_client()
                resp = self._upsert_fred_with_retry(client, rows, batch_num)

            if resp and resp.data:
                total_new += len(resp.data)

            self.log.debug(
                "Batch %d-%d: upserted %d rows",
                i, i + len(batch),
                len(resp.data) if resp and resp.data else 0,
            )

        return total_new

    def _upsert_fred_with_retry(self, client, rows, batch_num):
        """Upsert to fred_cpi_data with exponential backoff on transient errors."""
        for attempt in range(_MAX_RETRIES):
            try:
                return (
                    client.table("fred_cpi_data")
                    .upsert(rows, on_conflict="series_id,observation_date")
                    .execute()
                )
            except Exception as exc:
                exc_name = type(exc).__name__
                exc_str = str(exc)
                is_transient = (
                    "RemoteProtocolError" in exc_name
                    or "ConnectionTerminated" in exc_str
                    or "502" in exc_str
                    or "503" in exc_str
                    or "Bad gateway" in exc_str
                    or "Service Unavailable" in exc_str
                )

                if not is_transient:
                    raise

                delay = _RETRY_BASE_DELAY * (2 ** attempt)
                self.log.warning(
                    "Transient error at batch %d (attempt %d/%d): %s. "
                    "Retrying in %ds...",
                    batch_num, attempt + 1, _MAX_RETRIES,
                    exc_name, delay,
                )
                time.sleep(delay)
                reset_client()
                client = get_client()

        # Final attempt — let it raise if it fails
        return (
            client.table("fred_cpi_data")
            .upsert(rows, on_conflict="series_id,observation_date")
            .execute()
        )

    # ── FRED data fetching ────────────────────────────────────────────────────

    def _fetch_series(
        self, series_id: str, since: Optional[str]
    ) -> List[tuple]:
        """Fetch observations for one series.

        Returns list of (date_str, value_or_None) tuples for dates > since.
        Uses JSON API if FRED_API_KEY is set, otherwise public CSV endpoint.
        """
        if FRED_API_KEY:
            return self._fetch_series_json(series_id, since)
        return self._fetch_series_csv(series_id, since)

    def _fetch_series_csv(
        self, series_id: str, since: Optional[str]
    ) -> List[tuple]:
        """Fetch via the public CSV endpoint (no API key required).

        URL: https://fred.stlouisfed.org/graph/fredgraph.csv?id=<SERIES_ID>
        Returns CSV with columns: DATE, VALUE
        """
        url = "{}?id={}".format(FRED_CSV_BASE, series_id)
        if since:
            # FRED CSV doesn't support date filtering — we filter client-side
            pass

        resp = self._get_with_retry(url)
        if resp is None:
            self.log.warning("Failed to fetch CSV for %s, skipping", series_id)
            return []

        try:
            text = resp.text
            reader = csv.DictReader(io.StringIO(text))
            # FRED CSV uses "observation_date" and series_id as column names,
            # not "DATE" and "VALUE".  Fall back to those names for safety.
            fieldnames = reader.fieldnames or []
            date_col = "observation_date" if "observation_date" in fieldnames else "DATE"
            value_col = series_id if series_id in fieldnames else "VALUE"
            observations = []
            for row in reader:
                date_str = row.get(date_col, "").strip()
                value_str = row.get(value_col, "").strip()

                if not date_str:
                    continue

                # Skip observations we already have
                if since and date_str <= since:
                    continue

                # FRED uses "." for missing/unreported values
                value = None
                if value_str and value_str != _FRED_MISSING:
                    try:
                        value = float(value_str)
                    except ValueError:
                        self.log.debug(
                            "Unexpected value %r for %s on %s",
                            value_str, series_id, date_str,
                        )
                        continue

                observations.append((date_str, value))

            return observations

        except Exception as exc:
            self.log.error(
                "Error parsing CSV for %s: %s", series_id, exc
            )
            return []

    def _fetch_series_json(
        self, series_id: str, since: Optional[str]
    ) -> List[tuple]:
        """Fetch via the FRED JSON API (requires API key).

        URL: https://api.stlouisfed.org/fred/series/observations
        Paginates in 1000-observation chunks.
        """
        params = {
            "series_id": series_id,
            "api_key": FRED_API_KEY,
            "file_type": "json",
            "limit": 1000,
            "offset": 0,
        }
        if since:
            params["observation_start"] = since

        observations = []

        while True:
            url = "{}/series/observations".format(FRED_API_BASE)
            resp = self._get_with_retry(url, params=params)
            if resp is None:
                self.log.warning(
                    "Failed to fetch JSON page for %s at offset %d, stopping",
                    series_id, params["offset"],
                )
                break

            try:
                data = resp.json()
            except Exception as exc:
                self.log.error(
                    "JSON parse error for %s: %s", series_id, exc
                )
                break

            page_obs = data.get("observations", [])
            if not page_obs:
                break

            for obs in page_obs:
                date_str = obs.get("date", "").strip()
                value_str = obs.get("value", "").strip()

                if not date_str:
                    continue

                value = None
                if value_str and value_str != _FRED_MISSING:
                    try:
                        value = float(value_str)
                    except ValueError:
                        continue

                observations.append((date_str, value))

            # FRED returns count of total observations in this response
            if len(page_obs) < params["limit"]:
                break  # Last page

            params["offset"] += params["limit"]
            time.sleep(FRED_DELAY)

        return observations

    def _get_with_retry(
        self, url: str, params: Optional[Dict[str, Any]] = None
    ) -> Optional[requests.Response]:
        """GET request with retries on transient errors.

        Returns None if all retries are exhausted or the series doesn't exist.
        """
        for attempt in range(_MAX_RETRIES):
            try:
                resp = self._session.get(
                    url, params=params, timeout=DEFAULT_TIMEOUT
                )

                if resp.status_code == 404:
                    self.log.warning("Series not found at %s (404)", url)
                    return None

                if resp.status_code == 400:
                    self.log.warning(
                        "Bad request for %s (400): %s",
                        url, resp.text[:200],
                    )
                    return None

                resp.raise_for_status()
                return resp

            except requests.exceptions.HTTPError as exc:
                status = exc.response.status_code if exc.response else 0
                if status in (502, 503):
                    delay = _RETRY_BASE_DELAY * (2 ** attempt)
                    self.log.warning(
                        "HTTP %d for %s (attempt %d/%d), retrying in %ds...",
                        status, url, attempt + 1, _MAX_RETRIES, delay,
                    )
                    time.sleep(delay)
                else:
                    raise

            except requests.exceptions.ConnectionError as exc:
                delay = _RETRY_BASE_DELAY * (2 ** attempt)
                self.log.warning(
                    "Connection error for %s (attempt %d/%d): %s. "
                    "Retrying in %ds...",
                    url, attempt + 1, _MAX_RETRIES, exc, delay,
                )
                time.sleep(delay)

            except requests.exceptions.Timeout:
                delay = _RETRY_BASE_DELAY * (2 ** attempt)
                self.log.warning(
                    "Timeout for %s (attempt %d/%d), retrying in %ds...",
                    url, attempt + 1, _MAX_RETRIES, delay,
                )
                time.sleep(delay)

        self.log.error("All %d retries exhausted for %s", _MAX_RETRIES, url)
        return None
