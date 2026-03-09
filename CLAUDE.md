# FullCarts Project Context

## Python Compatibility
Target runtime is Python 3.9 (macOS system Python). Never use:
- `X | Y` union type syntax (use `Optional[X]`, `Union[X, Y]`)
- `dict[K, V]`, `list[T]`, `set[T]` in annotations (use `Dict`, `List`, `Set` from typing)
Always grep the entire project for these patterns before committing.

## Supabase
- Project: ntyhbapphnzlariakgrw
- URL: https://ntyhbapphnzlariakgrw.supabase.co
- Site: https://fullcarts.org
- Admin login: long-press header logo -> password prompt (hash in app_settings table)

## Scraper Commands
- Recent: `SUPABASE_KEY="<service_role_key>" python3 reddit_public_scraper.py --recent`
- Backfill: `SUPABASE_KEY="<service_role_key>" python3 reddit_public_scraper.py --backfill`
- Promote: `python3 backend/jobs/promote_staging.py`
