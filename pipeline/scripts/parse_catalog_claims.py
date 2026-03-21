#!/usr/bin/env python3
"""Direct parser for structured catalog data (OFF, Kroger, Open Prices).

Reads raw_items with source_type in (openfoodfacts, kroger_api, open_prices)
and creates claims by mapping raw_payload JSON fields directly — NO Anthropic
API calls.  This is dramatically cheaper and faster than running these through
Claude Haiku, since the data is already structured.

Usage:
    python -m pipeline.scripts.parse_catalog_claims [OPTIONS]

Options:
    --limit N           Process at most N items (default: all)
    --source-type TYPE  Only process one source type
    --batch-size N      Items per DB write batch (default: 100)
    --dry-run           Print what would be written without writing
    --extractor VER     Extractor version string (default: direct-v1)
"""
import argparse
import re
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from pipeline.lib.logging_setup import get_logger
from pipeline.lib.supabase_client import get_client, reset_client
from pipeline.lib.units import parse_package_weight

log = get_logger("parse_catalog_claims")

DEFAULT_EXTRACTOR = "direct-v1"
POSTG_REST_PAGE_SIZE = 1000

# Category mapping for OFF categories string -> our categories
_CATEGORY_MAP = {
    "chips": "chips",
    "crisps": "chips",
    "snack": "snacks",
    "snacks": "snacks",
    "cereal": "cereal",
    "cereals": "cereal",
    "cookie": "cookies",
    "cookies": "cookies",
    "biscuit": "cookies",
    "cracker": "crackers",
    "crackers": "crackers",
    "yogurt": "yogurt",
    "yoghurt": "yogurt",
    "ice cream": "ice_cream",
    "ice-cream": "ice_cream",
    "candy": "candy",
    "chocolate": "candy",
    "confectionery": "candy",
    "beverage": "beverages",
    "beverages": "beverages",
    "drink": "beverages",
    "drinks": "beverages",
    "juice": "beverages",
    "soda": "beverages",
    "frozen": "frozen_meals",
    "frozen meal": "frozen_meals",
    "canned": "canned_goods",
    "bread": "bread",
    "pasta": "pasta",
    "noodle": "pasta",
    "condiment": "condiments",
    "sauce": "condiments",
    "ketchup": "condiments",
    "mustard": "condiments",
    "dairy": "dairy",
    "milk": "dairy",
    "cheese": "dairy",
    "butter": "dairy",
    "cream": "dairy",
    "meat": "meat",
    "beef": "meat",
    "chicken": "meat",
    "pork": "meat",
    "produce": "produce",
    "fruit": "produce",
    "vegetable": "produce",
}


def main():
    # type: () -> None
    parser = argparse.ArgumentParser(
        description="Parse structured catalog data directly into claims"
    )
    parser.add_argument(
        "--limit", type=int, default=0,
        help="Max items to process (0 = all)",
    )
    parser.add_argument(
        "--source-type", type=str, default=None,
        choices=["openfoodfacts", "kroger_api", "open_prices", "walmart"],
        help="Only process this source type",
    )
    parser.add_argument(
        "--batch-size", type=int, default=100,
        help="Items per DB write batch",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print what would be written without writing",
    )
    parser.add_argument(
        "--extractor", type=str, default=DEFAULT_EXTRACTOR,
        help="Extractor version string",
    )
    args = parser.parse_args()

    log.info(
        "Starting direct parse (limit=%s, source=%s, dry_run=%s, extractor=%s)",
        args.limit or "all",
        args.source_type or "all catalog types",
        args.dry_run,
        args.extractor,
    )

    source_types = (
        [args.source_type] if args.source_type
        else ["openfoodfacts", "kroger_api", "open_prices", "walmart"]
    )

    total_parsed = 0
    total_skipped = 0
    total_errors = 0
    start_time = time.time()

    for st in source_types:
        unprocessed = _find_unprocessed_items(
            extractor_version=args.extractor,
            source_type=st,
            limit=args.limit - total_parsed if args.limit else 0,
        )
        log.info("Found %d unprocessed %s items", len(unprocessed), st)

        if not unprocessed:
            continue

        for i in range(0, len(unprocessed), args.batch_size):
            batch = unprocessed[i:i + args.batch_size]
            batch_num = i // args.batch_size + 1
            log.info(
                "Processing %s batch %d (%d items)", st, batch_num, len(batch)
            )

            for item in batch:
                try:
                    claim_data = _parse_item(item)
                except Exception as exc:
                    total_errors += 1
                    if total_errors <= 10:
                        log.error(
                            "Error parsing %s/%s: %s",
                            st, item.get("id", "?"), str(exc)[:200],
                        )
                    continue

                if claim_data is None:
                    total_skipped += 1
                    continue

                total_parsed += 1

                if args.dry_run:
                    if total_parsed <= 5:
                        log.info(
                            "[DRY RUN] %s | %s | %s | size=%s %s | upc=%s",
                            st,
                            claim_data.get("brand") or "?",
                            claim_data.get("product_name") or "?",
                            claim_data.get("new_size") or "?",
                            claim_data.get("new_size_unit") or "",
                            claim_data.get("upc") or "none",
                        )
                else:
                    _write_claim(item, claim_data, args.extractor)

            if args.limit and total_parsed >= args.limit:
                break

        if args.limit and total_parsed >= args.limit:
            break

    elapsed = time.time() - start_time
    log.info(
        "Done: parsed=%d, skipped=%d, errors=%d, elapsed=%.0fs",
        total_parsed, total_skipped, total_errors, elapsed,
    )


# ── Source-specific parsers ─────────────────────────────────────────────────


def _parse_item(item):
    # type: (Dict[str, Any]) -> Optional[Dict[str, Any]]
    """Route to the appropriate parser based on source_type."""
    source_type = item["source_type"]
    payload = item.get("raw_payload", {})

    if not payload:
        return None

    if source_type == "openfoodfacts":
        return _parse_off(payload)
    elif source_type == "kroger_api":
        return _parse_kroger(payload)
    elif source_type == "open_prices":
        return _parse_open_prices(payload)
    elif source_type == "walmart":
        return _parse_walmart(payload)
    else:
        return None


def _parse_off(payload):
    # type: (Dict[str, Any]) -> Optional[Dict[str, Any]]
    """Parse an Open Food Facts product record directly.

    OFF payload fields: code, product_name, brands, quantity,
    product_quantity, product_quantity_unit, categories
    """
    code = _safe_str(payload.get("code"))
    name = _safe_str(payload.get("product_name"))
    brands = _safe_str(payload.get("brands"))

    # Need at least a product name or brand
    if not name and not brands:
        return None

    # Parse size from quantity field
    size = None  # type: Optional[float]
    size_unit = None  # type: Optional[str]

    # Try numeric product_quantity first
    pq = payload.get("product_quantity")
    pq_unit = _safe_str(payload.get("product_quantity_unit"))
    if pq is not None:
        try:
            size = float(pq)
            if size <= 0:
                size = None
            elif pq_unit:
                from pipeline.lib.units import normalize_unit
                size_unit = normalize_unit(pq_unit)
        except (TypeError, ValueError):
            pass

    # Fall back to parsing the "quantity" string (e.g. "500 g", "12 oz")
    if size is None:
        qty_str = _safe_str(payload.get("quantity"))
        if qty_str:
            size, size_unit = parse_package_weight(qty_str)

    # Determine category
    categories_raw = _safe_str(payload.get("categories"))
    category = _classify_category(categories_raw)

    # Compute confidence based on data completeness
    conf_brand = 0.9 if brands else 0.0
    conf_name = 0.9 if name else 0.0
    conf_size = 0.9 if size else 0.0
    overall = min(
        0.9,
        (conf_brand + conf_name + conf_size) / 3,
    )

    return {
        "brand": _title_case(brands),
        "product_name": name,
        "category": category,
        "old_size": None,
        "old_size_unit": None,
        "new_size": size,
        "new_size_unit": size_unit,
        "old_price": None,
        "new_price": None,
        "retailer": None,
        "upc": code,
        "observed_date": None,
        "change_description": "catalog_entry",
        "is_shrinkflation": False,
        "confidence": {
            "brand": conf_brand,
            "product_name": conf_name,
            "size_change": 0.0,
            "overall": overall,
        },
    }


def _parse_kroger(payload):
    # type: (Dict[str, Any]) -> Optional[Dict[str, Any]]
    """Parse a Kroger API product record directly.

    Kroger payload fields: description, brand, upc, productId, size,
    items[0].price.regular, categories
    """
    desc = _safe_str(payload.get("description"))
    brand = _safe_str(payload.get("brand"))
    upc = _safe_str(payload.get("upc")) or _safe_str(payload.get("productId"))

    if not desc and not brand:
        return None

    # Parse size
    size = None  # type: Optional[float]
    size_unit = None  # type: Optional[str]
    size_str = _safe_str(payload.get("size"))
    if not size_str:
        item_info = payload.get("itemInformation")
        if isinstance(item_info, dict):
            size_str = _safe_str(item_info.get("size"))
    if size_str:
        size, size_unit = parse_package_weight(size_str)

    # Extract price
    price = None  # type: Optional[float]
    items = payload.get("items", [])
    if items and isinstance(items, list):
        price_info = items[0].get("price", {}) if isinstance(items[0], dict) else {}
        raw_price = price_info.get("regular") or price_info.get("promo")
        if raw_price is not None:
            try:
                price = float(raw_price)
                if price <= 0:
                    price = None
            except (TypeError, ValueError):
                pass

    # Categories
    categories_raw = payload.get("categories", [])
    category = None  # type: Optional[str]
    if isinstance(categories_raw, list) and categories_raw:
        category = _classify_category(" ".join(str(c) for c in categories_raw))
    elif isinstance(categories_raw, str):
        category = _classify_category(categories_raw)

    conf_brand = 0.95 if brand else 0.0
    conf_name = 0.95 if desc else 0.0
    conf_size = 0.9 if size else 0.0
    overall = min(
        0.95,
        (conf_brand + conf_name + conf_size) / 3,
    )

    return {
        "brand": _title_case(brand),
        "product_name": desc,
        "category": category,
        "old_size": None,
        "old_size_unit": None,
        "new_size": size,
        "new_size_unit": size_unit,
        "old_price": None,
        "new_price": price,
        "retailer": "Kroger",
        "upc": upc,
        "observed_date": None,
        "change_description": "catalog_entry",
        "is_shrinkflation": False,
        "confidence": {
            "brand": conf_brand,
            "product_name": conf_name,
            "size_change": 0.0,
            "overall": overall,
        },
    }


def _parse_open_prices(payload):
    # type: (Dict[str, Any]) -> Optional[Dict[str, Any]]
    """Parse an Open Prices receipt record directly.

    Open Prices payload fields: product_code, product.product_name,
    product.brands, price, currency, date, location.osm_name
    """
    code = _safe_str(payload.get("product_code")) or _safe_str(
        payload.get("barcode")
    )

    product = payload.get("product", {})
    name = None  # type: Optional[str]
    brand = None  # type: Optional[str]
    if isinstance(product, dict):
        name = _safe_str(product.get("product_name"))
        brand = _safe_str(product.get("brands"))

    # Need at least a barcode or product name
    if not name and not code:
        return None

    # Price
    price = None  # type: Optional[float]
    raw_price = payload.get("price")
    if raw_price is not None:
        try:
            price = float(raw_price)
            if price <= 0:
                price = None
        except (TypeError, ValueError):
            pass

    currency = _safe_str(payload.get("currency"))

    # Date
    observed_date = None  # type: Optional[str]
    raw_date = payload.get("date") or payload.get("created")
    if raw_date:
        date_str = str(raw_date).strip()[:10]
        if re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            observed_date = date_str

    # Store / retailer
    retailer = None  # type: Optional[str]
    location = payload.get("location", {})
    if isinstance(location, dict):
        retailer = _safe_str(
            location.get("osm_name") or location.get("name")
        )

    conf_brand = 0.8 if brand else 0.0
    conf_name = 0.8 if name else 0.0
    overall = min(
        0.8,
        (conf_brand + conf_name + (0.8 if price else 0.0)) / 3,
    )

    return {
        "brand": _title_case(brand),
        "product_name": name,
        "category": None,
        "old_size": None,
        "old_size_unit": None,
        "new_size": None,
        "new_size_unit": None,
        "old_price": None,
        "new_price": price,
        "retailer": retailer,
        "upc": code,
        "observed_date": observed_date,
        "change_description": "price_observation",
        "is_shrinkflation": False,
        "confidence": {
            "brand": conf_brand,
            "product_name": conf_name,
            "size_change": 0.0,
            "overall": overall,
        },
    }


def _parse_walmart(payload):
    # type: (Dict[str, Any]) -> Optional[Dict[str, Any]]
    """Parse a Walmart Affiliate API product record directly.

    Walmart payload fields: name, brandName, upc, itemId,
    salePrice, size, categoryPath, shortDescription
    """
    name = _safe_str(payload.get("name"))
    brand = _safe_str(payload.get("brandName"))
    upc = _safe_str(payload.get("upc"))
    item_id = _safe_str(payload.get("itemId"))

    if not name and not brand:
        return None

    # Parse size from the size field or product name
    size = None  # type: Optional[float]
    size_unit = None  # type: Optional[str]
    size_str = _safe_str(payload.get("size"))
    if size_str:
        size, size_unit = parse_package_weight(size_str)
    # Fall back to parsing size from product name if not in size field
    if size is None and name:
        size, size_unit = parse_package_weight(name)

    # Price
    price = None  # type: Optional[float]
    raw_price = payload.get("salePrice") or payload.get("msrp")
    if raw_price is not None:
        try:
            price = float(raw_price)
            if price <= 0:
                price = None
        except (TypeError, ValueError):
            pass

    # Category from categoryPath
    cat_path = _safe_str(payload.get("categoryPath"))
    category = _classify_category(cat_path)

    # Use UPC if available, otherwise item ID
    product_code = upc or (str(item_id) if item_id else None)

    conf_brand = 0.95 if brand else 0.0
    conf_name = 0.95 if name else 0.0
    conf_size = 0.9 if size else 0.0
    overall = min(
        0.95,
        (conf_brand + conf_name + conf_size) / 3,
    )

    return {
        "brand": _title_case(brand),
        "product_name": name,
        "category": category,
        "old_size": None,
        "old_size_unit": None,
        "new_size": size,
        "new_size_unit": size_unit,
        "old_price": None,
        "new_price": price,
        "retailer": "Walmart",
        "upc": product_code,
        "observed_date": None,
        "change_description": "catalog_entry",
        "is_shrinkflation": False,
        "confidence": {
            "brand": conf_brand,
            "product_name": conf_name,
            "size_change": 0.0,
            "overall": overall,
        },
    }


# ── DB helpers ──────────────────────────────────────────────────────────────


def _find_unprocessed_items(extractor_version, source_type, limit):
    # type: (str, str, int) -> List[Dict[str, Any]]
    """Find raw_items that don't have a claim for this extractor version."""
    client = get_client()

    log.info("Fetching processed IDs for extractor=%s, source=%s...",
             extractor_version, source_type)
    processed_ids = _get_processed_ids(client, extractor_version, source_type)
    log.info("Found %d already-processed items", len(processed_ids))

    items = _fetch_raw_items(client, source_type, processed_ids, limit)
    return items


def _get_processed_ids(client, extractor_version, source_type):
    # type: (Any, str, str) -> Set[str]
    """Get raw_item_ids already processed by this extractor.

    Filters by source_type via a join on raw_items to avoid pulling IDs
    from unrelated source types.
    """
    processed = set()  # type: Set[str]
    offset = 0

    while True:
        resp = (
            client.table("claims")
            .select("raw_item_id")
            .eq("extractor_version", extractor_version)
            .range(offset, offset + POSTG_REST_PAGE_SIZE - 1)
            .execute()
        )
        if not resp.data:
            break
        for row in resp.data:
            processed.add(row["raw_item_id"])
        if len(resp.data) < POSTG_REST_PAGE_SIZE:
            break
        offset += POSTG_REST_PAGE_SIZE

    return processed


def _fetch_raw_items(client, source_type, exclude_ids, limit):
    # type: (Any, str, Set[str], int) -> List[Dict[str, Any]]
    """Fetch raw_items for a source type, excluding already-processed IDs."""
    items = []  # type: List[Dict[str, Any]]
    offset = 0
    target = limit if limit else float("inf")

    while len(items) < target:
        resp = (
            client.table("raw_items")
            .select("id,source_type,source_id,source_url,source_date,raw_payload")
            .eq("source_type", source_type)
            .order("captured_at", desc=False)
            .range(offset, offset + POSTG_REST_PAGE_SIZE - 1)
            .execute()
        )
        if not resp.data:
            break

        for row in resp.data:
            if row["id"] not in exclude_ids:
                items.append(row)
                if limit and len(items) >= limit:
                    return items

        if len(resp.data) < POSTG_REST_PAGE_SIZE:
            break
        offset += POSTG_REST_PAGE_SIZE

        if offset > 0 and offset % (POSTG_REST_PAGE_SIZE * 20) == 0:
            reset_client()
            client = get_client()

    return items


def _write_claim(item, claim_data, extractor_version):
    # type: (Dict[str, Any], Dict[str, Any], str) -> None
    """Write a directly-parsed claim to the claims table."""
    client = get_client()

    row = {
        "raw_item_id": item["id"],
        "extractor_version": extractor_version,
        "claim_index": 0,
        "extracted_at": datetime.now(timezone.utc).isoformat(),
        "brand": claim_data.get("brand"),
        "product_name": claim_data.get("product_name"),
        "category": claim_data.get("category"),
        "old_size": claim_data.get("old_size"),
        "old_size_unit": claim_data.get("old_size_unit"),
        "new_size": claim_data.get("new_size"),
        "new_size_unit": claim_data.get("new_size_unit"),
        "old_price": claim_data.get("old_price"),
        "new_price": claim_data.get("new_price"),
        "retailer": claim_data.get("retailer"),
        "upc": claim_data.get("upc"),
        "observed_date": claim_data.get("observed_date"),
        "change_description": claim_data.get("change_description"),
        "confidence": claim_data.get("confidence", {}),
        "status": "pending",
    }

    try:
        client.table("claims").upsert(
            row, on_conflict="raw_item_id,extractor_version,claim_index"
        ).execute()
    except Exception as exc:
        log.error(
            "Failed to write claim for raw_item %s: %s",
            item["id"], str(exc)[:200],
        )


# ── Utility helpers ─────────────────────────────────────────────────────────


def _safe_str(value):
    # type: (Any) -> Optional[str]
    if value is None:
        return None
    s = str(value).strip()
    return s if s else None


def _title_case(value):
    # type: (Optional[str]) -> Optional[str]
    if not value:
        return None
    return value.strip().title()


def _classify_category(categories_str):
    # type: (Optional[str]) -> Optional[str]
    """Map a categories string to one of our standard categories."""
    if not categories_str:
        return None
    lower = categories_str.lower()
    for keyword, cat in _CATEGORY_MAP.items():
        if keyword in lower:
            return cat
    return "other"


if __name__ == "__main__":
    main()
