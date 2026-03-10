"""USDA FoodData Central quarterly branded-food scraper.

Downloads the latest USDA FDC branded food ZIP release, streams the CSV,
and writes matching records to raw_items and variant_observations.
Memory-efficient: the CSV is never fully loaded into RAM.
"""
import csv
import io
import os
import tempfile
import zipfile
from datetime import date
from typing import Any, Dict, Iterator, List, Optional, Tuple

from pipeline.config import USDA_FDC_BASE, USDA_RELEASES, USER_AGENT
from pipeline.lib.http_client import RateLimitedSession
from pipeline.lib.supabase_client import get_client
from pipeline.lib.units import parse_package_weight
from pipeline.scrapers.base import BaseScraper

# USDA bulk download — be polite, single request per run
_USDA_RPS = 0.5
_LOG_EVERY = 10_000


class UsdaQuarterlyScraper(BaseScraper):
    """Downloads and processes the latest USDA FDC branded food CSV release."""

    scraper_name = "usda_quarterly"
    source_type = "usda"

    def __init__(self) -> None:
        super().__init__()
        self._session = RateLimitedSession(
            requests_per_second=_USDA_RPS,
            user_agent=USER_AGENT,
        )
        # Latest release is the last entry in config
        self._release_date, self._release_filename = USDA_RELEASES[-1]

    # ── BaseScraper interface ──────────────────────────────────────────────

    def fetch(
        self, cursor: Dict[str, Any], dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        """Download the latest USDA release and parse branded_food.csv.

        Returns a list of dicts, one per parseable row (UPC + weight present).
        To keep memory bounded the full list is still returned for compatibility
        with BaseScraper.run(); very large releases may need chunked processing
        via a direct override of run() in a future version.
        """
        self.log.info(
            "Processing USDA quarterly release: %s (%s)",
            self._release_date,
            self._release_filename,
        )
        items: List[Dict[str, Any]] = []

        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = self._download_release(tmpdir)
            if zip_path is None:
                self.log.error("USDA download failed; returning empty list")
                return []
            for i, row in enumerate(self._stream_rows(zip_path)):
                if i > 0 and i % _LOG_EVERY == 0:
                    self.log.info("USDA: processed %d rows so far...", i)
                items.append(row)

        self.log.info(
            "USDA quarterly: %d parseable rows from release %s",
            len(items),
            self._release_date,
        )
        return items

    def store(self, items: List[Dict[str, Any]]) -> int:
        """Write raw_items, then write variant_observations for matching UPCs."""
        stored = super().store(items)
        self._store_variant_observations(items)
        return stored

    def source_id_for(self, item: Dict[str, Any]) -> str:
        # Include release date so each quarterly snapshot is a separate record
        return f"usda_{item['gtin_upc']}_{item['fdc_id']}_{self._release_date}"

    def source_url_for(self, item: Dict[str, Any]) -> Optional[str]:
        return (
            f"https://fdc.nal.usda.gov/food-details/{item['fdc_id']}/branded"
        )

    def source_date_for(self, item: Dict[str, Any]) -> Optional[str]:
        return self._release_date

    def next_cursor(
        self, items: List[Dict[str, Any]], prev_cursor: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {
            "last_release": self._release_date,
            "records_processed": len(items),
        }

    # ── Download & parse ───────────────────────────────────────────────────

    def _download_release(self, tmpdir: str) -> Optional[str]:
        """Download the USDA ZIP to tmpdir.  Returns local path or None."""
        url = f"{USDA_FDC_BASE}/{self._release_filename}"
        self.log.info("Downloading USDA release from %s", url)

        resp = self._session.get(url, stream=True)
        if resp is None:
            return None

        zip_path = os.path.join(tmpdir, self._release_filename)
        with open(zip_path, "wb") as fh:
            for chunk in resp.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    fh.write(chunk)

        self.log.info(
            "USDA ZIP saved to %s (%d bytes)",
            zip_path,
            os.path.getsize(zip_path),
        )
        return zip_path

    def _stream_rows(self, zip_path: str) -> Iterator[Dict[str, Any]]:
        """Yield parsed row dicts from branded_food.csv inside the ZIP.

        Only rows with a non-empty gtin_upc and parseable package_weight are
        yielded.
        """
        with zipfile.ZipFile(zip_path, "r") as zf:
            # Locate branded_food.csv — it may be nested in a subdirectory
            csv_name = next(
                (n for n in zf.namelist() if n.endswith("branded_food.csv")),
                None,
            )
            if csv_name is None:
                self.log.error(
                    "branded_food.csv not found inside %s", zip_path
                )
                return

            self.log.info("Streaming %s from ZIP", csv_name)
            with zf.open(csv_name) as raw_file:
                # csv.DictReader needs a text-mode stream
                text_file = io.TextIOWrapper(raw_file, encoding="utf-8", errors="replace")
                reader = csv.DictReader(text_file)
                for row in reader:
                    parsed = self._parse_row(row)
                    if parsed is not None:
                        yield parsed

    def _parse_row(self, row: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Convert a branded_food.csv row to our canonical dict format.

        Returns None if the row lacks a UPC or has an unparseable weight.
        """
        upc = (row.get("gtin_upc") or "").strip()
        if not upc:
            return None

        package_weight_raw = (row.get("package_weight") or "").strip()
        size, size_unit = parse_package_weight(package_weight_raw)
        if size is None:
            return None

        return {
            "fdc_id": (row.get("fdc_id") or "").strip(),
            "gtin_upc": upc,
            "brand_owner": (row.get("brand_owner") or "").strip(),
            "brand_name": (row.get("brand_name") or "").strip(),
            "description": (row.get("description") or "").strip(),
            "package_weight": package_weight_raw,
            "serving_size": (row.get("serving_size") or "").strip(),
            "serving_size_unit": (row.get("serving_size_unit") or "").strip(),
            "branded_food_category": (row.get("branded_food_category") or "").strip(),
            # Carry parsed values for variant_observations use
            "_size": size,
            "_size_unit": size_unit,
        }

    # ── variant_observations ───────────────────────────────────────────────

    def _store_variant_observations(
        self, items: List[Dict[str, Any]]
    ) -> None:
        """Upsert variant_observations for rows whose UPC matches a pack_variant."""
        client = get_client()

        all_upcs = list({i["gtin_upc"] for i in items})
        variant_map = self._load_variant_map(all_upcs)
        if not variant_map:
            self.log.info("No matching UPCs in pack_variants; skipping observations")
            return

        raw_id_map = self._load_raw_item_ids(items, variant_map)
        source_ref = f"usda_quarterly_{self._release_date}"
        rows: List[Dict[str, Any]] = []

        for item in items:
            upc = item["gtin_upc"]
            variant_id = variant_map.get(upc)
            if variant_id is None:
                continue

            rows.append({
                "variant_id": variant_id,
                "observed_date": self._release_date,
                "source_type": "usda",
                "source_ref": source_ref,
                "size": item["_size"],
                "size_unit": item["_size_unit"],
                "raw_item_id": raw_id_map.get(self.source_id_for(item)),
            })

        if not rows:
            self.log.info("No variant_observations to write for usda_quarterly")
            return

        batch_size = 50
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            client.table("variant_observations").upsert(
                batch,
                on_conflict="variant_id,observed_date,source_type,retailer",
            ).execute()

        self.log.info(
            "Upserted %d variant_observations for usda_quarterly", len(rows)
        )

    def _load_variant_map(self, upcs: List[str]) -> Dict[str, Any]:
        """Return {upc: variant_id} for UPCs that exist in pack_variants."""
        if not upcs:
            return {}
        client = get_client()
        # Supabase .in_() accepts a list; batch if very large
        result: Dict[str, Any] = {}
        batch_size = 500
        for i in range(0, len(upcs), batch_size):
            batch = upcs[i:i + batch_size]
            resp = (
                client.table("pack_variants")
                .select("id,upc")
                .in_("upc", batch)
                .execute()
            )
            for row in (resp.data or []):
                result[row["upc"]] = row["id"]
        return result

    def _load_raw_item_ids(
        self,
        items: List[Dict[str, Any]],
        variant_map: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Return {source_id: raw_item_id} for items whose UPC is in variant_map."""
        client = get_client()
        relevant_source_ids = [
            self.source_id_for(i)
            for i in items
            if i["gtin_upc"] in variant_map
        ]
        if not relevant_source_ids:
            return {}
        result: Dict[str, Any] = {}
        batch_size = 500
        for i in range(0, len(relevant_source_ids), batch_size):
            batch = relevant_source_ids[i:i + batch_size]
            resp = (
                client.table("raw_items")
                .select("id,source_id")
                .eq("source_type", self.source_type)
                .in_("source_id", batch)
                .execute()
            )
            for row in (resp.data or []):
                result[row["source_id"]] = row["id"]
        return result
