"""Helper for writing to the `data_quality_flags` quarantine table (migration 063).

Pipeline scripts use this to mark suspect rows for admin review instead of
mutating them. The table's unique-index on `(flag_kind, target_id)` for open
rows makes raise_flag() idempotent — calling it repeatedly on the same target
won't pile up duplicate flags as long as the original is still open.

Usage:
    from pipeline.lib.data_quality_flags import raise_flag

    raise_flag(
        sb,
        flag_kind="short_brand",
        severity="med",
        entity_id=entity_id,
        detected_by="promote_claims",
        detail={"brand": brand, "length": len(brand)},
    )

The function swallows duplicate-key errors (the idempotent case) but raises
on anything else, so a misconfigured detector surfaces loudly instead of
silently dropping flags.
"""
from typing import Any, Dict, Optional


def raise_flag(
    sb,
    flag_kind,             # type: str
    severity,              # type: str
    detected_by,           # type: str
    claim_id=None,         # type: Optional[str]
    entity_id=None,        # type: Optional[str]
    event_id=None,         # type: Optional[str]
    detail=None,           # type: Optional[Dict[str, Any]]
):
    # type: (...) -> Optional[str]
    """Insert a flag row pointing at exactly one of claim_id / entity_id /
    event_id. Returns the new row id, or None if a duplicate open flag
    already exists for the same (flag_kind, target) combination.

    Severity must be one of 'low' / 'med' / 'high' (enforced by the table's
    CHECK constraint — we don't pre-validate here, just surface the DB error).
    """
    targets = [t for t in (claim_id, entity_id, event_id) if t is not None]
    if len(targets) != 1:
        raise ValueError(
            "raise_flag requires exactly one of claim_id / entity_id / event_id, got {}".format(
                len(targets)
            )
        )

    payload = {
        "flag_kind": flag_kind,
        "severity": severity,
        "detected_by": detected_by,
        "detail": detail or {},
    }
    if claim_id is not None:
        payload["claim_id"] = claim_id
    if entity_id is not None:
        payload["entity_id"] = entity_id
    if event_id is not None:
        payload["event_id"] = event_id

    try:
        resp = sb.table("data_quality_flags").insert(payload).execute()
        rows = resp.data or []
        return rows[0]["id"] if rows else None
    except Exception as exc:  # noqa: BLE001
        # Idempotent re-runs hit the partial unique index on open flags.
        # PostgREST surfaces this as a 23505 / unique_violation. Swallow
        # that one case; re-raise anything else so config errors are loud.
        msg = str(exc)
        if "23505" in msg or "duplicate key" in msg.lower():
            return None
        raise
