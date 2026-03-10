"""Cursor management via the scraper_state table."""
from datetime import datetime, timezone
from typing import Any, Dict

from pipeline.lib.supabase_client import get_client
from pipeline.lib.logging_setup import get_logger

log = get_logger("cursor")


def load_cursor(scraper_name: str) -> Dict[str, Any]:
    """Read last_cursor JSONB from scraper_state.  Returns {} if no prior run."""
    client = get_client()
    resp = (
        client.table("scraper_state")
        .select("last_cursor")
        .eq("scraper_name", scraper_name)
        .execute()
    )
    if resp.data:
        return resp.data[0].get("last_cursor") or {}
    return {}


def save_cursor(
    scraper_name: str,
    cursor: Dict[str, Any],
    status: str,
    items_processed: int,
) -> None:
    """Upsert scraper_state with new cursor, status, and count."""
    client = get_client()
    now = datetime.now(timezone.utc).isoformat()
    row = {
        "scraper_name": scraper_name,
        "last_cursor": cursor,
        "last_run_at": now,
        "last_run_status": status,
        "items_processed": items_processed,
        "updated_at": now,
    }
    client.table("scraper_state").upsert(row, on_conflict="scraper_name").execute()
    log.info(
        "Cursor saved for %s: status=%s, items=%d",
        scraper_name, status, items_processed,
    )
