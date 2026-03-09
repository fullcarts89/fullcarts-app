#!/usr/bin/env python3
"""
FullCarts Reddit Scraper
========================
PRAW-based pipeline for ingesting shrinkflation reports from Reddit.

Targets: r/shrinkflation, r/Frugal, r/personalfinance, r/grocery,
         r/mildlyinfuriating, r/EatCheapAndHealthy, r/Costco, r/traderjoes

Output:  staging_queue.json  — tiered confidence queue (auto / review / discard)
         known_urls.txt       — dedup registry of already-processed post URLs

Privacy: No usernames are stored — only post URLs + timestamps.

Setup:
  1. pip install praw
  2. Create a Reddit app at https://www.reddit.com/prefs/apps (script type)
  3. Set env vars (or fill REDDIT_* constants below):
       REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
  4. Run:  python reddit_scraper.py
  5. For GitHub Actions cron, see .github/workflows/reddit_scraper.yml at bottom of file.
"""

import os
import re
import json
import time
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

try:
    from supabase import create_client, Client as SupabaseClient
    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False

try:
    from backend.lib.vision import analyze_image, should_analyze, merge_vision_into_parsed
    HAS_VISION = True
except ImportError:
    HAS_VISION = False

# ---------------------------------------------------------------------------
# Config — override via environment variables for CI / GitHub Actions
# ---------------------------------------------------------------------------

REDDIT_CLIENT_ID     = os.getenv("REDDIT_CLIENT_ID",     "YOUR_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "YOUR_CLIENT_SECRET")
REDDIT_USER_AGENT    = os.getenv("REDDIT_USER_AGENT",    "FullCartsBot/1.0 (by u/YOUR_USERNAME; fullcarts.app)")

# Supabase — service role key (PRIVATE, never expose in frontend)
SUPABASE_URL         = os.getenv("SUPABASE_URL",         "https://ntyhbapphnzlariakgrw.supabase.co")
SUPABASE_KEY         = os.getenv("SUPABASE_KEY",         "")  # Set via env var — service_role key

# Subreddits to monitor
TARGET_SUBREDDITS = [
    "shrinkflation",
    "Frugal",
    "personalfinance",
    "grocery",
    "EatCheapAndHealthy",
    "Costco",
    "traderjoes",
]

# How many posts to fetch per subreddit per run (Reddit max = 100 with pagination)
POSTS_PER_SUB = 50

# Output paths
OUTPUT_DIR       = Path(os.getenv("OUTPUT_DIR", "."))
STAGING_FILE     = OUTPUT_DIR / "staging_queue.json"
KNOWN_URLS_FILE  = OUTPUT_DIR / "known_urls.txt"

# Confidence thresholds
TIER_AUTO_THRESHOLD   = 3   # fields found → auto-accept
TIER_REVIEW_THRESHOLD = 1   # fields found → review queue

# Existing FullCarts product UPCs for dedup (extend as product DB grows)
KNOWN_UPCS: set[str] = {
    "016000275560", "024000016816", "021130126026", "011110859830",
    "048001214823", "078742035215", "049000042566", "013800133236",
    "038000845178", "070038588337",
}

# ---------------------------------------------------------------------------
# Known brand list for NLP matching
# ---------------------------------------------------------------------------

KNOWN_BRANDS = [
    "tropicana", "lays", "lay's", "doritos", "gatorade", "pepsi", "coca-cola", "coke",
    "hellmann's", "hellmanns", "unilever", "general mills", "cheerios", "nature valley",
    "tide", "dawn", "bounty", "charmin", "folgers", "maxwell house", "starbucks",
    "oreo", "nabisco", "mondelez", "campbell's", "campbells", "kraft", "heinz",
    "heinz ketchup", "kellogg's", "kelloggs", "special k", "frosted flakes",
    "quaker", "pepsico", "post", "planters", "skippy", "jif", "peanut butter",
    "trader joe's", "trader joes", "costco", "kirkland", "whole foods", "365",
    "ben & jerry's", "haagen-dazs", "breyers", "blue bell",
    "tyson", "perdue", "oscar mayer", "ball park", "hebrew national",
    "minute maid", "simply orange", "florida's natural",
    "colgate", "crest", "oral-b", "listerine",
    "febreze", "glad", "ziploc", "scotch-brite",
    "stouffer's", "lean cuisine", "marie callender's",
    "progresso", "amy's", "annie's", "horizon",
]

# Unit patterns
UNIT_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*(oz|fl\.?\s*oz|ounce[s]?|lb[s]?|pound[s]?|g|gram[s]?|ml|liter[s]?|ct|count|pack|piece[s]?|sheet[s]?)",
    re.IGNORECASE,
)

# Price patterns
PRICE_PATTERN = re.compile(r"\$\s*(\d+(?:\.\d{1,2})?)", re.IGNORECASE)

# "from X to Y" size change patterns
FROM_TO_PATTERN = re.compile(
    r"(?:from|was|went from|used to be|previously|old[:]?)\s+"
    r"(\d+(?:\.\d+)?)\s*(oz|fl\.?\s*oz|ounce[s]?|lb[s]?|pound[s]?|g|gram[s]?|ml|ct|count)?"
    r"(?:\s*(?:to|now|→|->|–|-)\s*)"
    r"(\d+(?:\.\d+)?)\s*(oz|fl\.?\s*oz|ounce[s]?|lb[s]?|pound[s]?|g|gram[s]?|ml|ct|count)?",
    re.IGNORECASE,
)

# Shrinkflation keywords (post must contain at least one)
SHRINK_KEYWORDS = re.compile(
    r"\b(shrinkflation|shrunk|smaller|reduced|less|shrank|downsized|downsizing|"
    r"size cut|weight cut|ounces less|fewer ounces|net weight|same price|price increase|"
    r"got smaller|getting smaller|they reduced|they cut|less product|rip[- ]?off|"
    r"same box|same package|smaller amount)\b",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# NLP parser — ported from FullCarts JS parseText()
# ---------------------------------------------------------------------------

def normalize_unit(u: str) -> str:
    """Normalize unit string to canonical form (matches reddit_public_scraper)."""
    if not u:
        return "oz"
    u = u.lower().strip().rstrip("s")
    mapping = {
        "fl oz": "fl oz", "fl. oz": "fl oz", "ounce": "oz",
        "pound": "lb", "gram": "g", "liter": "l",
        "pint": "pt", "quart": "qt", "gallon": "gal",
        "sheet": "sheets", "roll": "rolls", "piece": "ct",
        "sq ft": "sq ft", "sq. ft": "sq ft",
    }
    return mapping.get(u, u)

def parse_text(text: str) -> dict:
    """
    Extract shrinkflation signals from a block of text.
    Returns a dict with extracted fields and a confidence score.
    """
    result = {
        "brand":        None,
        "product_hint": None,
        "old_size":     None,
        "new_size":     None,
        "old_unit":     None,
        "new_unit":     None,
        "old_price":    None,
        "new_price":    None,
        "fields_found": 0,
        "explicit_from_to": False,
    }

    text_lower = text.lower()

    # Brand detection (word-boundary match to avoid "gain" in "agressive and")
    for brand in KNOWN_BRANDS:
        if re.search(r"(?<![a-z])" + re.escape(brand) + r"(?![a-z])", text_lower):
            result["brand"] = brand.title()
            result["fields_found"] += 1
            break

    # Explicit from→to size change
    m = FROM_TO_PATTERN.search(text)
    if m:
        result["old_size"] = float(m.group(1))
        result["old_unit"] = normalize_unit(m.group(2) or "oz")
        result["new_size"] = float(m.group(3))
        result["new_unit"] = normalize_unit(m.group(4) or result["old_unit"])
        result["explicit_from_to"] = True
        result["fields_found"] += 2

    else:
        # Fallback: grab all unit mentions, assume first=old, last=new
        units = UNIT_PATTERN.findall(text)
        if len(units) >= 2:
            result["old_size"] = float(units[0][0])
            result["old_unit"] = normalize_unit(units[0][1])
            result["new_size"] = float(units[-1][0])
            result["new_unit"] = normalize_unit(units[-1][1])
            # Only count if sizes actually differ
            if result["old_size"] != result["new_size"]:
                result["fields_found"] += 1
        elif len(units) == 1:
            result["new_size"] = float(units[0][0])
            result["new_unit"] = normalize_unit(units[0][1])

    # Price mentions
    prices = PRICE_PATTERN.findall(text)
    if len(prices) >= 2:
        result["old_price"] = float(prices[0])
        result["new_price"] = float(prices[-1])
        result["fields_found"] += 1
    elif len(prices) == 1:
        result["new_price"] = float(prices[0])

    # Extract a short product hint from title/first sentence
    first_line = text.strip().split("\n")[0][:120]
    result["product_hint"] = first_line

    return result


def confidence_tier(parsed: dict, text: str = "") -> str:
    """
    Assign a confidence tier based on how many signal fields were extracted.
    auto   → ≥ TIER_AUTO_THRESHOLD fields + known brand + explicit from→to + shrink keywords
    review → ≥ TIER_REVIEW_THRESHOLD fields + shrink keywords
    discard → noise / off-topic
    """
    f = parsed["fields_found"]
    has_kw = bool(SHRINK_KEYWORDS.search(text)) if text else True  # backwards compat
    if f >= TIER_AUTO_THRESHOLD and parsed["brand"] and parsed["explicit_from_to"] and has_kw:
        return "auto"
    if f >= TIER_REVIEW_THRESHOLD and has_kw:
        return "review"
    if f >= TIER_AUTO_THRESHOLD and parsed["explicit_from_to"]:
        return "review"
    return "discard"


# ---------------------------------------------------------------------------
# Dedup helpers
# ---------------------------------------------------------------------------

def load_known_urls(path: Path) -> set:
    if path.exists():
        return set(path.read_text().splitlines())
    return set()


def save_known_urls(path: Path, urls: set) -> None:
    path.write_text("\n".join(sorted(urls)))


# ---------------------------------------------------------------------------
# Staging queue helpers
# ---------------------------------------------------------------------------

def load_staging(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text())
        except json.JSONDecodeError:
            log = logging.getLogger("fullcarts")
            log.warning(f"Corrupt staging file at {path} — backing up and starting fresh")
            backup = path.with_suffix('.json.corrupt')
            path.rename(backup)
    return {"auto": [], "review": [], "meta": {"last_run": None, "total_processed": 0}}


def save_staging(path: Path, queue: dict) -> None:
    path.write_text(json.dumps(queue, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# Moderator removal detection
# ---------------------------------------------------------------------------

MOD_REMOVAL_KEYWORDS = re.compile(
    r"\b(removed|deleted|doesn't belong|not shrinkflation|off[- ]topic|rule \d|"
    r"violat|spam|repost|duplicate|wrong sub|not relevant|this post has been)\b",
    re.IGNORECASE,
)


def is_mod_removed(post) -> bool:
    """Check if a Reddit post was removed by moderators.

    Checks:
    1. post.removed_by_category == 'moderator'
    2. post.selftext == '[removed]' or '[deleted]'
    3. First comment is from a moderator/AutoModerator with removal language
    """
    # Check PRAW removal attributes
    removed_by = getattr(post, "removed_by_category", None)
    if removed_by in ("moderator", "automod_filtered"):
        return True

    selftext = getattr(post, "selftext", "") or ""
    if selftext.strip() in ("[removed]", "[deleted]"):
        return True

    # Check first comment for mod removal notice
    try:
        post.comment_sort = "old"
        post.comments.replace_more(limit=0)
        if post.comments:
            first = post.comments[0]
            is_mod = (
                getattr(first, "distinguished", None) == "moderator"
                or (
                    getattr(first, "author", None) is not None
                    and str(first.author).lower() in ("automoderator", "automod")
                )
            )
            if is_mod and MOD_REMOVAL_KEYWORDS.search(first.body or ""):
                return True
    except Exception:
        pass  # Comment fetch may fail for deleted posts

    return False


def check_mod_removals(reddit, sb, log) -> int:
    """Re-check existing staging entries for moderator-removed posts.

    Fetches all pending/review entries from reddit_staging and checks
    if the original Reddit post has been removed by moderators.
    Returns the count of dismissed entries.
    """
    result = sb.table("reddit_staging").select("id, source_url").eq(
        "status", "pending"
    ).execute()
    entries = result.data or []
    dismissed = 0

    for entry in entries:
        source_url = entry.get("source_url", "")
        if not source_url:
            continue

        # Extract Reddit post ID from URL
        # Format: https://reddit.com/r/subreddit/comments/POST_ID/...
        parts = source_url.rstrip("/").split("/")
        try:
            comments_idx = parts.index("comments")
            post_id = parts[comments_idx + 1]
        except (ValueError, IndexError):
            continue

        try:
            post = reddit.submission(id=post_id)
            # Access an attribute to trigger the fetch
            _ = post.title

            if is_mod_removed(post):
                sb.table("reddit_staging").update(
                    {"status": "dismissed"}
                ).eq("id", entry["id"]).execute()
                dismissed += 1
                log.info(f"  Dismissed (mod-removed): {source_url[:80]}")

        except Exception as exc:
            # Post may be deleted entirely — dismiss it
            if "404" in str(exc) or "Not Found" in str(exc):
                sb.table("reddit_staging").update(
                    {"status": "dismissed"}
                ).eq("id", entry["id"]).execute()
                dismissed += 1
                log.info(f"  Dismissed (deleted): {source_url[:80]}")
            else:
                log.warning(f"  Mod-check failed for {entry['id']}: {exc}")

        time.sleep(0.5)  # Rate limit

    return dismissed


# ---------------------------------------------------------------------------
# Core scraping logic
# ---------------------------------------------------------------------------

_IMAGE_DOMAINS = {"i.redd.it", "i.imgur.com", "imgur.com", "preview.redd.it"}


def _extract_image_url_praw(post) -> Optional[str]:
    """Return a direct image URL from a PRAW post object, or None.

    Handles direct image links, gallery posts (media_metadata), and
    preview images.
    """
    url = getattr(post, "url", "") or ""
    post_hint = getattr(post, "post_hint", "") or ""

    # Direct image link (i.redd.it, imgur, etc.)
    if post_hint == "image" or any(d in url for d in _IMAGE_DOMAINS):
        return url[:500] if url else None

    # Reddit gallery posts: images stored in media_metadata
    media_meta = getattr(post, "media_metadata", None)
    if media_meta and isinstance(media_meta, dict):
        for item in media_meta.values():
            if item.get("status") != "valid" and item.get("e") != "Image":
                continue
            src = item.get("s", {})
            img_url = src.get("u") or src.get("gif")
            if img_url:
                return img_url.replace("&amp;", "&")[:500]

    # Fallback: Reddit preview images
    preview = getattr(post, "preview", None)
    if preview and isinstance(preview, dict):
        images = preview.get("images", [])
        if images:
            src = images[0].get("source", {})
            img_url = src.get("url")
            if img_url:
                return img_url.replace("&amp;", "&")[:500]

    return None


def build_entry(post, parsed: dict, tier: str) -> dict:
    """Build a staging entry from a Reddit post + parsed signals."""
    return {
        "source_url":    f"https://reddit.com{post.permalink}",
        "subreddit":     post.subreddit.display_name,
        "posted_utc":    datetime.fromtimestamp(post.created_utc, tz=timezone.utc).isoformat(),
        "scraped_utc":   datetime.now(tz=timezone.utc).isoformat(),
        "tier":          tier,
        "title":         post.title[:200],
        "body":          (post.selftext or "")[:2000],
        "image_url":     _extract_image_url_praw(post),
        "brand":         parsed["brand"],
        "product_hint":  parsed["product_hint"],
        "old_size":      parsed["old_size"],
        "old_unit":      parsed["old_unit"],
        "new_size":      parsed["new_size"],
        "new_unit":      parsed["new_unit"],
        "old_price":     parsed["old_price"],
        "new_price":     parsed["new_price"],
        "explicit_from_to": parsed["explicit_from_to"],
        "fields_found":  parsed["fields_found"],
        "score":         post.score,
        "num_comments":  post.num_comments,
        # No username stored — privacy-first
    }


def promote_auto_entries(sb, log) -> int:
    """Promote high-confidence reddit entries directly to products + events."""
    result = sb.table("reddit_staging").select("*").eq("tier", "auto").eq("status", "pending").execute()
    entries = result.data or []
    promoted = 0

    for entry in entries:
        if not entry.get("old_size") or not entry.get("new_size"):
            continue

        upc = f"REDDIT-{entry['id'][:8]}"
        old_s = float(entry["old_size"])
        new_s = float(entry["new_size"])
        unit = entry.get("new_unit") or entry.get("old_unit") or "oz"
        pct = round(((old_s - new_s) / old_s) * 100, 2) if old_s > 0 else 0

        product_name = (entry.get("product_hint") or "Unknown Product")[:100]
        brand = entry.get("brand")

        try:
            # Upsert product
            sb.table("products").upsert({
                "upc": upc,
                "name": product_name,
                "brand": brand,
                "category": "Other",
                "current_size": new_s,
                "unit": unit,
                "type": "shrinkflation",
                "repeat_offender": False,
                "source": "reddit_bot"
            }, on_conflict="upc").execute()

            # Upsert event (prevent duplicates)
            posted = entry.get("posted_utc") or datetime.now(tz=timezone.utc).isoformat()
            sb.table("events").upsert({
                "upc": upc,
                "date": str(posted)[:10],
                "old_size": old_s,
                "new_size": new_s,
                "unit": unit,
                "pct": pct,
                "price_before": entry.get("old_price"),
                "price_after": entry.get("new_price"),
                "type": "shrinkflation",
                "notes": f"Auto-imported from Reddit: {entry.get('source_url', '')}",
                "source": "reddit_bot"
            }, on_conflict="upc,date,source").execute()

            # Mark as promoted
            sb.table("reddit_staging").update({"status": "promoted"}).eq("id", entry["id"]).execute()
            promoted += 1
            log.info(f"  Promoted: {product_name} ({brand})")

        except Exception as exc:
            log.warning(f"  Promotion failed for {entry['id']}: {exc}")

    return promoted


def run_scraper(dry_run: bool = False) -> None:
    """Main scraping entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)s  %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    log = logging.getLogger("fullcarts")

    # Validate credentials
    if REDDIT_CLIENT_ID == "YOUR_CLIENT_ID":
        log.error("Set REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET env vars before running.")
        raise SystemExit(1)

    import praw  # noqa: PLC0415 — imported here so missing praw gives a clear error

    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
        # Read-only — no login required
    )

    known_urls = load_known_urls(KNOWN_URLS_FILE)
    queue      = load_staging(STAGING_FILE)
    new_urls   = set()

    stats = {"seen": 0, "skipped_dup": 0, "auto": 0, "review": 0, "discard": 0, "no_keyword": 0}

    for sub_name in TARGET_SUBREDDITS:
        log.info(f"Fetching r/{sub_name} …")
        try:
            subreddit = reddit.subreddit(sub_name)
            # Pull from both hot and new to maximise coverage
            posts = list(subreddit.hot(limit=POSTS_PER_SUB // 2)) + \
                    list(subreddit.new(limit=POSTS_PER_SUB // 2))
        except Exception as exc:
            log.warning(f"r/{sub_name} fetch failed: {exc}")
            continue

        for post in posts:
            stats["seen"] += 1
            url = f"https://reddit.com{post.permalink}"

            # Dedup
            if url in known_urls:
                stats["skipped_dup"] += 1
                continue

            # Skip posts removed by moderators
            if is_mod_removed(post):
                stats.setdefault("mod_removed", 0)
                stats["mod_removed"] += 1
                new_urls.add(url)
                continue

            # Combine title + selftext for NLP
            full_text = f"{post.title}\n{post.selftext or ''}"

            # Must contain at least one shrinkflation keyword
            if not SHRINK_KEYWORDS.search(full_text):
                stats["no_keyword"] += 1
                new_urls.add(url)  # Mark as seen so we don't re-evaluate
                continue

            parsed = parse_text(full_text)

            is_dedicated = sub_name.lower() == "shrinkflation"

            # Early discard: non-dedicated sub posts with no extractable fields
            if not is_dedicated and parsed["fields_found"] == 0:
                stats["discard"] += 1
                new_urls.add(url)
                continue

            # Vision analysis: only for dedicated subs to avoid wasting API
            # calls on low-signal posts from general subreddits.
            image_url = _extract_image_url_praw(post)
            vision_result = None
            if is_dedicated and HAS_VISION and should_analyze(parsed, image_url):
                vision_result = analyze_image(image_url, post.title)
                if vision_result:
                    parsed = merge_vision_into_parsed(parsed, vision_result)
                    stats.setdefault("vision_analyzed", 0)
                    stats["vision_analyzed"] += 1

            tier   = confidence_tier(parsed, text=full_text)

            # Visual-only shrinkflation: vision confirmed shrinkflation but no
            # numbers could be extracted. Force to review tier for human judgment.
            if vision_result and vision_result.get("visual_only") and tier == "discard":
                tier = "review"

            stats[tier] += 1

            if not dry_run and tier != "discard":
                entry = build_entry(post, parsed, tier)
                # Attach vision metadata if available
                if vision_result:
                    entry["ai_description"] = vision_result.get("description")
                    entry["visual_only"] = bool(vision_result.get("visual_only"))
                queue[tier].append(entry)
                log.info(f"  [{tier.upper():6}] {post.title[:70]}")

            new_urls.add(url)

        # Respect Reddit rate limits between subreddits
        time.sleep(1.5)

    # Persist
    known_urls |= new_urls
    queue["meta"]["last_run"]          = datetime.now(tz=timezone.utc).isoformat()
    queue["meta"]["total_processed"]   = queue["meta"].get("total_processed", 0) + stats["seen"]

    if not dry_run:
        save_known_urls(KNOWN_URLS_FILE, known_urls)
        save_staging(STAGING_FILE, queue)

        # Also write to Supabase if configured
        if HAS_SUPABASE and SUPABASE_KEY:
            try:
                sb: SupabaseClient = create_client(SUPABASE_URL, SUPABASE_KEY)
                # Collect all new entries (auto + review) for upsert
                all_entries = []
                for tier_name in ("auto", "review"):
                    for entry in queue[tier_name]:
                        all_entries.append(entry)

                if all_entries:
                    sb.table("reddit_staging").upsert(
                        all_entries, on_conflict="source_url",
                        ignore_duplicates=True
                    ).execute()
                    log.info(f"Supabase: inserted {len(all_entries)} entries to reddit_staging (skipped existing)")

                # Auto-promote high-confidence entries to products + events
                promoted = promote_auto_entries(sb, log)
                log.info(f"Auto-promoted {promoted} entries to products + events")

                # Check existing staging entries for mod-removed posts
                log.info("Checking existing staging entries for mod-removed posts...")
                mod_dismissed = check_mod_removals(reddit, sb, log)
                log.info(f"Mod-removal check: dismissed {mod_dismissed} entries")
            except Exception as exc:
                log.warning(f"Supabase write failed (JSON fallback still saved): {exc}")
        elif not SUPABASE_KEY:
            log.info("SUPABASE_KEY not set — skipping database write (JSON saved locally)")

    # Summary
    log.info("=" * 60)
    log.info(f"Run complete — seen:{stats['seen']}  dupes:{stats['skipped_dup']}  "
             f"no-keyword:{stats['no_keyword']}")
    log.info(f"  auto:{stats['auto']}  review:{stats['review']}  discard:{stats['discard']}")
    if stats.get("mod_removed"):
        log.info(f"  mod-removed (skipped): {stats['mod_removed']}")
    if stats.get("vision_analyzed"):
        log.info(f"  vision analyzed: {stats['vision_analyzed']} images")
    log.info(f"Staging queue → {STAGING_FILE}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="FullCarts Reddit Scraper")
    parser.add_argument("--dry-run", action="store_true",
                        help="Parse posts but do not write to disk.")
    args = parser.parse_args()

    run_scraper(dry_run=args.dry_run)


# ===========================================================================
# GitHub Actions workflow — save as .github/workflows/reddit_scraper.yml
# ===========================================================================
#
# name: FullCarts Reddit Scraper
#
# on:
#   schedule:
#     - cron: "0 */6 * * *"   # every 6 hours
#   workflow_dispatch:          # allow manual trigger
#
# jobs:
#   scrape:
#     runs-on: ubuntu-latest
#     steps:
#       - uses: actions/checkout@v4
#
#       - name: Set up Python
#         uses: actions/setup-python@v5
#         with:
#           python-version: "3.11"
#
#       - name: Install dependencies
#         run: pip install praw
#
#       - name: Run scraper
#         env:
#           REDDIT_CLIENT_ID:     ${{ secrets.REDDIT_CLIENT_ID }}
#           REDDIT_CLIENT_SECRET: ${{ secrets.REDDIT_CLIENT_SECRET }}
#           REDDIT_USER_AGENT:    "FullCartsBot/1.0 (by u/YOUR_USERNAME; fullcarts.app)"
#           OUTPUT_DIR:           data
#         run: python reddit_scraper.py
#
#       - name: Commit updated staging queue
#         run: |
#           git config user.name  "github-actions[bot]"
#           git config user.email "github-actions[bot]@users.noreply.github.com"
#           git add data/staging_queue.json data/known_urls.txt
#           git diff --cached --quiet || git commit -m "chore: update reddit staging queue [skip ci]"
#           git push
#
# ===========================================================================
# staging_queue.json schema
# ===========================================================================
#
# {
#   "auto": [              ← ready to import into FullCarts after spot-check
#     {
#       "source_url":       "https://reddit.com/r/shrinkflation/comments/...",
#       "subreddit":        "shrinkflation",
#       "posted_utc":       "2026-02-18T14:22:00+00:00",
#       "scraped_utc":      "2026-02-20T06:00:01+00:00",
#       "tier":             "auto",
#       "title":            "Tropicana OJ went from 52oz to 46oz, same price!",
#       "brand":            "Tropicana",
#       "product_hint":     "Tropicana OJ went from 52oz to 46oz, same price!",
#       "old_size":         52.0,
#       "old_unit":         "oz",
#       "new_size":         46.0,
#       "new_unit":         "oz",
#       "old_price":        null,
#       "new_price":        null,
#       "explicit_from_to": true,
#       "fields_found":     3,
#       "score":            847,
#       "num_comments":     142
#     }
#   ],
#   "review": [ ... ],     ← needs human validation before import
#   "meta": {
#     "last_run":         "2026-02-20T06:00:05+00:00",
#     "total_processed":  1240
#   }
# }
