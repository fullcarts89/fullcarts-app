"""Lazy-init Supabase client for the pipeline (service_role key)."""
from pipeline.config import SUPABASE_URL, SUPABASE_KEY
from pipeline.lib.logging_setup import get_logger

log = get_logger("supabase")

_client = None


def get_client():
    """Lazy-init Supabase client.  Raises if credentials missing."""
    global _client
    if _client is not None:
        return _client

    if not SUPABASE_KEY:
        raise RuntimeError(
            "SUPABASE_KEY not set — cannot connect to Supabase. "
            "Set the environment variable to your service_role key."
        )

    from supabase import create_client
    _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    log.info("Supabase client connected to %s", SUPABASE_URL)
    return _client


def reset_client():
    """Force a new Supabase client on next get_client() call.

    Useful when HTTP/2 connections hit stream limits on large batch jobs.
    """
    global _client
    _client = None
    log.info("Supabase client reset — will reconnect on next call")
