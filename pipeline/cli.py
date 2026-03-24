"""Unified CLI entrypoint for the FullCarts pipeline.

Usage:
    python -m pipeline reddit_recent    [--dry-run]
    python -m pipeline reddit_backfill  [--dry-run]
    python -m pipeline news_rss         [--dry-run]
    python -m pipeline gdelt            [--dry-run]
    python -m pipeline gdelt_backfill   [--dry-run]
    python -m pipeline off_daily        [--dry-run]
    python -m pipeline off_discovery    [--dry-run]
    python -m pipeline kroger           [--dry-run]
    python -m pipeline kroger_discovery [--dry-run]
    python -m pipeline usda_quarterly   [--dry-run]
    python -m pipeline usda_backfill    [--dry-run]
    python -m pipeline usda_variance    [--dry-run]
    python -m pipeline usda_turnover    [--dry-run]
    python -m pipeline bls_shrinkflation [--dry-run]
    python -m pipeline open_prices      [--dry-run]
    python -m pipeline fred_cpi         [--dry-run]
    python -m pipeline walmart          [--dry-run]
    python -m pipeline walmart_discovery [--dry-run]
    python -m pipeline upc_backfill     [--dry-run]
    python -m pipeline wayback          [--dry-run]
    python -m pipeline wayback --url URL [--url URL2] --brand BRAND --product NAME [--upc UPC]
"""
import argparse
import sys

from pipeline.lib.logging_setup import get_logger

log = get_logger("cli")

# Lazy imports to avoid loading all scrapers on every invocation
SCRAPER_MAP = {
    "reddit_recent": "pipeline.scrapers.reddit_recent:RedditRecentScraper",
    "reddit_backfill": "pipeline.scrapers.reddit_backfill:RedditBackfillScraper",
    "news_rss": "pipeline.scrapers.news_rss:NewsRssScraper",
    "gdelt": "pipeline.scrapers.gdelt:GdeltScraper",
    "gdelt_backfill": "pipeline.scrapers.gdelt_backfill:GdeltBackfillScraper",
    "off_daily": "pipeline.scrapers.openfoodfacts:OpenFoodFactsScraper",
    "off_discovery": "pipeline.scrapers.off_discovery:OffDiscoveryScraper",
    "kroger": "pipeline.scrapers.kroger:KrogerScraper",
    "kroger_discovery": "pipeline.scrapers.kroger_discovery:KrogerDiscoveryScraper",
    "usda_quarterly": "pipeline.scrapers.usda_quarterly:UsdaQuarterlyScraper",
    "usda_backfill": "pipeline.scrapers.usda_backfill:UsdaBackfillScraper",
    "usda_variance": "pipeline.scrapers.usda_variance:UsdaVarianceAnalyzer",
    "usda_turnover": "pipeline.scrapers.usda_turnover:UsdaTurnoverAnalyzer",
    "bls_shrinkflation": "pipeline.scrapers.bls_shrinkflation:BlsShrinkflationScraper",
    "open_prices": "pipeline.scrapers.open_prices:OpenPricesScraper",
    "fred_cpi": "pipeline.scrapers.fred_cpi:FredCpiScraper",
    "walmart": "pipeline.scrapers.walmart:WalmartDiscoveryScraper",
    "walmart_discovery": "pipeline.scrapers.walmart:WalmartDiscoveryScraper",
    "upc_backfill": "pipeline.scrapers.upc_backfill:UpcBackfillScraper",
    "wayback": "pipeline.scrapers.wayback:WaybackScraper",
}


def _load_scraper(name: str):
    """Dynamically import and instantiate a scraper by name."""
    if name not in SCRAPER_MAP:
        log.error(
            "Unknown scraper: %s. Available: %s",
            name, ", ".join(sorted(SCRAPER_MAP.keys())),
        )
        sys.exit(1)

    module_path, class_name = SCRAPER_MAP[name].rsplit(":", 1)
    module = __import__(module_path, fromlist=[class_name])
    cls = getattr(module, class_name)
    return cls()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="FullCarts data ingestion pipeline",
    )
    parser.add_argument(
        "scraper",
        choices=sorted(SCRAPER_MAP.keys()),
        help="Which scraper to run",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch data but do not write to Supabase",
    )

    # ── Wayback-specific arguments ────────────────────────────────────────
    wayback_group = parser.add_argument_group(
        "wayback options",
        "Options for the wayback scraper (ignored by other scrapers)",
    )
    wayback_group.add_argument(
        "--url",
        action="append",
        dest="urls",
        metavar="URL",
        help="Product page URL to investigate (repeatable). "
             "Any retailer: Walmart, Amazon, Kroger, Target, OFF, USDA",
    )
    wayback_group.add_argument(
        "--brand",
        help="Brand name for the product (used with --url)",
    )
    wayback_group.add_argument(
        "--product",
        help="Product name (used with --url)",
    )
    wayback_group.add_argument(
        "--upc",
        help="UPC barcode (used with --url)",
    )
    wayback_group.add_argument(
        "--category",
        help="Product category (used with --url)",
    )

    args = parser.parse_args()

    if args.scraper == "wayback" and args.urls:
        # Build WaybackScraper with ad-hoc target
        from pipeline.scrapers.wayback import WaybackScraper
        scraper = WaybackScraper(
            urls=args.urls,
            brand=args.brand,
            product_name=args.product,
            upc=args.upc,
            category=args.category,
        )
    else:
        scraper = _load_scraper(args.scraper)

    try:
        scraper.run(dry_run=args.dry_run)
    except KeyboardInterrupt:
        log.info("Interrupted by user")
        sys.exit(130)
    except Exception:
        log.exception("Scraper %s failed", args.scraper)
        sys.exit(1)


if __name__ == "__main__":
    main()
