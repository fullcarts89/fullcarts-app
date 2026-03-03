"""
Shared Supabase client for all backend jobs and scrapers.
"""
import logging
from backend.config import SUPABASE_URL, SUPABASE_KEY

log = logging.getLogger("fullcarts")

_client = None

def get_client():
    """Lazy-init Supabase client. Raises if credentials missing."""
    global _client
    if _client is not None:
        return _client

    if not SUPABASE_KEY:
        raise RuntimeError("SUPABASE_KEY not set — cannot connect to Supabase")

    from supabase import create_client
    _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    log.info(f"Supabase client connected to {SUPABASE_URL}")
    return _client
