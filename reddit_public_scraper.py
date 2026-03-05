#!/usr/bin/env python3
"""
FullCarts Reddit Scraper
========================
Uses the Arctic Shift archive API (no Reddit credentials needed).

Modes:
  --backfill     One-time historical scrape of ALL posts from target subreddits (2017–present)
  --recent       Fetch posts from the last 7 days via Arctic Shift (default)
  --promote-only Skip scraping, just promote staged entries to products/events

Data flow:
  Arctic Shift API
    → parse title + selftext for product/size/brand
    → score confidence (auto / review / discard)
    → upsert to reddit_staging table in Supabase
    → auto-promote high-confidence entries to products + events tables

Uses the post's month as the "when noticed" date for events.

Privacy: No usernames are stored — only post URLs + timestamps.

Setup:
  pip install requests supabase
  export SUPABASE_URL=https://ntyhbapphnzlariakgrw.supabase.co
  export SUPABASE_KEY=<your-service-role-key>
  python reddit_public_scraper.py --backfill
"""

import os
import re
import json
import time
import logging
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import requests

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
# Config
# ---------------------------------------------------------------------------

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ntyhbapphnzlariakgrw.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

USER_AGENT = "FullCartsBot/1.0 (fullcarts.org community shrinkflation tracker)"

# Arctic Shift API (Pushshift/Pullpush successor) — no Reddit credentials needed
ARCTIC_SHIFT_URL = "https://arctic-shift.photon-reddit.com/api/posts/search"

# Output for local fallback
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "."))
KNOWN_URLS_FILE = OUTPUT_DIR / "known_urls_public.txt"

# Confidence thresholds
TIER_AUTO_THRESHOLD = 3    # fields found → auto-accept
TIER_REVIEW_THRESHOLD = 1  # fields found → review queue

# ---------------------------------------------------------------------------
# Target subreddits
# ---------------------------------------------------------------------------
# "dedicated" subs: every post is likely relevant → review tier floor
# "general" subs: require keyword match + fields_found >= 1, and min score
#                 to filter noise from high-volume communities

DEDICATED_SUBREDDITS = ["shrinkflation"]

GENERAL_SUBREDDITS = [
    "grocery",
    "Costco",
    "traderjoes",
    "mildlyinfuriating",
]

ALL_SUBREDDITS = DEDICATED_SUBREDDITS + GENERAL_SUBREDDITS

# Minimum post score for general subreddits (filters low-quality noise)
MIN_SCORE_GENERAL = 5

# ---------------------------------------------------------------------------
# Known brands (reused from existing scraper)
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
    "tostitos", "ruffles", "cheetos", "fritos", "sun chips",
    "pringles", "wheat thins", "triscuit", "ritz", "goldfish",
    "hershey", "reese's", "kit kat", "snickers", "m&m's", "twix",
    "nestle", "nescafe", "coffee mate", "dreyer's", "edy's",
    "tillamook", "chobani", "yoplait", "dannon", "oikos",
    "oscar mayer", "jimmy dean", "johnsonville", "hillshire",
    "goya", "old el paso", "taco bell", "mission",
    "barilla", "ragu", "prego", "classico", "bertolli",
    "hidden valley", "ranch", "french's", "grey poupon",
    "velveeta", "philadelphia", "sargento", "borden",
    "totino's", "digiorno", "red baron", "tombstone",
    "hot pocket", "hot pockets", "bagel bites",
    "frito-lay", "frito lay", "pepperidge farm",
    "smucker's", "smuckers", "welch's", "welchs",
    "aunt jemima", "pearl milling", "mrs butterworth",
    "wonder bread", "sara lee", "arnold", "dave's killer bread",
    "thomas'", "thomas", "entenmann's", "entenmanns",
    "little debbie", "hostess", "drake's",
    "scott", "cottonelle", "viva", "kleenex", "puffs",
    "huggies", "pampers", "luvs",
    "downy", "gain", "all", "arm & hammer", "oxiclean",
    "clorox", "lysol", "pine-sol", "mr clean",
    "dial", "irish spring", "dove", "ivory", "olay",
    "pantene", "head & shoulders", "suave", "tresemme",
    "toblerone", "cadbury", "lindt", "ghirardelli", "godiva",
]

# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

UNIT_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*(oz|fl\.?\s*oz|ounce[s]?|lb[s]?|pound[s]?|g|gram[s]?|kg|ml|liter[s]?|l|ct|count|pack|piece[s]?|sheet[s]?|roll[s]?|sq\.?\s*ft|pt|pint[s]?|qt|quart[s]?|gal|gallon[s]?)",
    re.IGNORECASE,
)

PRICE_PATTERN = re.compile(r"\$\s*(\d+(?:\.\d{1,2})?)", re.IGNORECASE)

FROM_TO_PATTERN = re.compile(
    r"(?:from|was|went from|used to be|previously|old[:]?|originally|started at)\s+"
    r"(\d+(?:\.\d+)?)\s*(oz|fl\.?\s*oz|ounce[s]?|lb[s]?|pound[s]?|g|gram[s]?|kg|ml|ct|count|pack|sheet[s]?|roll[s]?|pt|pint[s]?|qt|quart[s]?|gal|gallon[s]?)?"
    r"(?:\s*(?:to|now|→|->|-->|–|—|-|down to|reduced to|shrunk to|changed to)\s*)"
    r"(\d+(?:\.\d+)?)\s*(oz|fl\.?\s*oz|ounce[s]?|lb[s]?|pound[s]?|g|gram[s]?|kg|ml|ct|count|pack|sheet[s]?|roll[s]?|pt|pint[s]?|qt|quart[s]?|gal|gallon[s]?)?",
    re.IGNORECASE,
)

# Additional patterns for "X oz → Y oz" style (no keyword prefix)
ARROW_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*(oz|fl\.?\s*oz|g|gram[s]?|ml|lb[s]?|ct|count|sheet[s]?|roll[s]?)"
    r"\s*(?:→|->|-->|⟶|to|vs\.?|versus|down to)\s*"
    r"(\d+(?:\.\d+)?)\s*(oz|fl\.?\s*oz|g|gram[s]?|ml|lb[s]?|ct|count|sheet[s]?|roll[s]?)?",
    re.IGNORECASE,
)

SHRINK_KEYWORDS = re.compile(
    r"\b(shrinkflation|shrunk|smaller|reduced|less|shrank|downsized|downsizing|"
    r"size cut|weight cut|ounces less|fewer ounces|net weight|same price|price increase|"
    r"got smaller|getting smaller|they reduced|they cut|less product|rip[- ]?off|"
    r"same box|same package|smaller amount|used to be|went from|half the size|"
    r"thin[n]?er|narrower|shorter|lighter|watered down|diluted|"
    r"fewer count|less sheets|less rolls|family size|not as big|getting ripped off)\b",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Category guesser
# ---------------------------------------------------------------------------

def guess_category(text: str) -> str:
    t = text.lower()
    if re.search(r"juice|soda|water|drink|coffee|tea|milk|creamer|gatorade|powerade|lemonade|beer|wine|energy drink", t):
        return "Beverages"
    if re.search(r"chip[s]?|cookie|cracker|pretzel|popcorn|candy|chocolate|gum|snack|goldfish|cheeto|dorito|frito|pringles|oreo|ritz|wheat thin", t):
        return "Snacks"
    if re.search(r"cereal|oat|granola|cheerio|frosted flake|special k|raisin bran", t):
        return "Cereal"
    if re.search(r"paper towel|toilet paper|tissue|napkin|bounty|charmin|scott|cottonelle|kleenex", t):
        return "Paper Goods"
    if re.search(r"soap|shampoo|conditioner|detergent|cleaner|dish|laundry|tide|dawn|lysol|clorox|toothpaste|deodorant", t):
        return "Household"
    if re.search(r"ice cream|frozen|pizza|bagel bite|hot pocket|totino|digiorno|stouffer|lean cuisine", t):
        return "Frozen"
    if re.search(r"bread|bagel|muffin|roll|bun|tortilla|wrap|pita|croissant|english muffin", t):
        return "Bakery"
    if re.search(r"yogurt|cheese|butter|cream cheese|sour cream|cottage cheese|milk|egg", t):
        return "Dairy"
    if re.search(r"sauce|ketchup|mustard|mayo|dressing|salsa|soup|broth|pasta|rice|bean|canned", t):
        return "Pantry"
    if re.search(r"chicken|beef|pork|turkey|bacon|sausage|hot dog|deli|meat|fish|shrimp|salmon", t):
        return "Meat"
    if re.search(r"peanut butter|jam|jelly|honey|syrup|spread|nutella", t):
        return "Spreads"
    return "Other"


# ---------------------------------------------------------------------------
# NLP parser
# ---------------------------------------------------------------------------

def normalize_unit(u: str) -> str:
    """Normalize unit string to a canonical form."""
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
    """Extract shrinkflation signals from text."""
    result = {
        "brand": None,
        "product_hint": None,
        "old_size": None,
        "new_size": None,
        "old_unit": None,
        "new_unit": None,
        "old_price": None,
        "new_price": None,
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
    if not m:
        m = ARROW_PATTERN.search(text)

    if m:
        old_val = float(m.group(1))
        new_val = float(m.group(3))
        old_unit = normalize_unit(m.group(2) or "oz")
        new_unit = normalize_unit(m.group(4) or old_unit)

        # Sanity: old should be bigger than new for shrinkflation
        if old_val > new_val:
            result["old_size"] = old_val
            result["new_size"] = new_val
            result["old_unit"] = old_unit
            result["new_unit"] = new_unit
            result["explicit_from_to"] = True
            result["fields_found"] += 2
        elif new_val > old_val:
            # They wrote it backwards — swap
            result["old_size"] = new_val
            result["new_size"] = old_val
            result["old_unit"] = new_unit
            result["new_unit"] = old_unit
            result["explicit_from_to"] = True
            result["fields_found"] += 2

    if not result["explicit_from_to"]:
        # Fallback: grab all unit mentions, assume first=old, last=new
        units = UNIT_PATTERN.findall(text)
        if len(units) >= 2:
            old_val = float(units[0][0])
            old_unit = normalize_unit(units[0][1])
            new_val = float(units[-1][0])
            new_unit = normalize_unit(units[-1][1])
            # Only count if sizes differ and same unit type
            if old_val != new_val and old_unit == new_unit:
                if old_val > new_val:
                    result["old_size"] = old_val
                    result["new_size"] = new_val
                else:
                    result["old_size"] = new_val
                    result["new_size"] = old_val
                result["old_unit"] = old_unit
                result["new_unit"] = new_unit
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

    # Extract a clean product hint from title
    first_line = text.strip().split("\n")[0][:120]
    # Clean up common reddit prefixes
    cleaned = re.sub(r"^\[?META\]?\s*", "", first_line, flags=re.IGNORECASE)
    cleaned = re.sub(r"^\[?Discussion\]?\s*", "", cleaned, flags=re.IGNORECASE)
    result["product_hint"] = cleaned.strip()

    return result


def confidence_tier(parsed: dict, subreddit: str = "", text: str = "") -> str:
    """Assign a confidence tier.

    Auto-tier now requires shrinkflation keywords to prevent off-topic posts
    from being auto-promoted.
    """
    f = parsed["fields_found"]
    has_kw = bool(SHRINK_KEYWORDS.search(text)) if text else True  # backwards compat
    if f >= TIER_AUTO_THRESHOLD and parsed["brand"] and parsed["explicit_from_to"] and has_kw:
        return "auto"
    if f >= TIER_REVIEW_THRESHOLD and has_kw:
        return "review"
    # Strong signal without keywords still goes to review
    if f >= TIER_AUTO_THRESHOLD and parsed["explicit_from_to"]:
        return "review"
    # Posts from dedicated shrinkflation subs are inherently relevant (mostly
    # image posts where product/size info lives in the photo, not the title).
    if subreddit.lower() in DEDICATED_SUBREDDITS:
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
# Arctic Shift archive fetcher (no Reddit credentials needed)
# ---------------------------------------------------------------------------

def fetch_arctic_shift_batch(subreddit: str = "shrinkflation", before_utc: int = None, after_utc: int = 0, limit: int = 100) -> list:
    """Fetch a batch of posts from Arctic Shift API."""
    params = {
        "subreddit": subreddit,
        "limit": min(limit, 100),
        "sort": "desc",
    }
    if before_utc:
        params["before"] = before_utc
    if after_utc:
        params["after"] = after_utc

    headers = {"User-Agent": USER_AGENT}

    try:
        resp = requests.get(ARCTIC_SHIFT_URL, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.json().get("data", [])
    except Exception as e:
        logging.getLogger("fullcarts").warning(f"Arctic Shift fetch failed: {e}")
        return []


def _fetch_all_one_sub(sub: str) -> list:
    """Fetch all historical posts for a single subreddit (thread-safe)."""
    log = logging.getLogger("fullcarts")
    is_dedicated = sub.lower() in DEDICATED_SUBREDDITS
    max_batches = 500 if is_dedicated else 100

    log.info(f"\n  --- r/{sub} (max {max_batches} batches) ---")
    before_utc = None
    posts_out = []

    for batch_num in range(1, max_batches + 1):
        posts = fetch_arctic_shift_batch(subreddit=sub, before_utc=before_utc, limit=100)
        if not posts:
            log.info(f"  r/{sub}: no more posts after batch {batch_num}")
            break

        posts_out.extend(posts)
        oldest_ts = min(p["created_utc"] for p in posts)
        before_utc = int(oldest_ts)

        oldest_date = datetime.utcfromtimestamp(oldest_ts).strftime("%Y-%m-%d")
        log.info(f"  r/{sub} batch {batch_num}: {len(posts)} posts "
                 f"(sub total: {len(posts_out)}, oldest: {oldest_date})")

        time.sleep(0.3)

    log.info(f"  r/{sub}: {len(posts_out)} posts fetched")
    return posts_out


def fetch_all_arctic_shift(log, subreddits: list = None) -> list:
    """Paginate through ALL historical posts via Arctic Shift (parallel)."""
    subreddits = subreddits or ALL_SUBREDDITS
    all_posts = []

    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = {
            pool.submit(_fetch_all_one_sub, sub): sub
            for sub in subreddits
        }
        for fut in as_completed(futures):
            sub = futures[fut]
            try:
                posts = fut.result()
                all_posts.extend(posts)
            except Exception as e:
                log.warning(f"  r/{sub}: fetch failed — {e}")

    return all_posts


# ---------------------------------------------------------------------------
# Entry builder
# ---------------------------------------------------------------------------

_IMAGE_DOMAINS = {"i.redd.it", "i.imgur.com", "imgur.com", "preview.redd.it"}


def _extract_image_url(post: dict) -> str | None:
    """Return a direct image URL from an Arctic Shift post dict, or None.

    Handles direct image links, gallery posts (media_metadata), and
    preview images.
    """
    url = post.get("url") or ""
    post_hint = post.get("post_hint") or ""

    # Direct image link (i.redd.it, imgur, etc.)
    if post_hint == "image" or any(d in url for d in _IMAGE_DOMAINS):
        return url[:500] if url else None

    # Reddit gallery posts: images stored in media_metadata
    media_meta = post.get("media_metadata")
    if media_meta and isinstance(media_meta, dict):
        # Pick the first image from the gallery
        for item in media_meta.values():
            if item.get("status") != "valid" and item.get("e") != "Image":
                continue
            # Prefer the source (full-res) image
            src = item.get("s", {})
            img_url = src.get("u") or src.get("gif")
            if img_url:
                # Reddit HTML-encodes URLs in media_metadata
                return img_url.replace("&amp;", "&")[:500]

    # Fallback: Reddit preview images (available on many image posts)
    preview = post.get("preview", {})
    if isinstance(preview, dict):
        images = preview.get("images", [])
        if images:
            src = images[0].get("source", {})
            img_url = src.get("url")
            if img_url:
                return img_url.replace("&amp;", "&")[:500]

    return None


def build_entry(post: dict, parsed: dict, tier: str) -> dict:
    """Build a staging entry from a Reddit post + parsed signals."""
    created_utc = post.get("created_utc", 0)
    permalink = post.get("permalink", "")

    # Use the post's month as the "when noticed" date
    if created_utc:
        post_date = datetime.utcfromtimestamp(created_utc)
        # First of the month the post was made
        date_noticed = post_date.strftime("%Y-%m-01")
    else:
        date_noticed = datetime.now(tz=timezone.utc).strftime("%Y-%m-01")

    return {
        "source_url": f"https://reddit.com{permalink}" if permalink.startswith("/") else permalink,
        "subreddit": post.get("subreddit", "shrinkflation"),
        "posted_utc": datetime.utcfromtimestamp(created_utc).isoformat() if created_utc else None,
        "scraped_utc": datetime.now(tz=timezone.utc).isoformat(),
        "tier": tier,
        # status is NOT included here — the DB default ('pending') applies on
        # first insert, and omitting it from the upsert payload ensures that
        # re-scraping the same source_url does not reset an already-promoted,
        # dismissed, or rejected record back to 'pending'.
        "title": (post.get("title") or "")[:200],
        "body": (post.get("selftext") or "")[:2000],
        "image_url": _extract_image_url(post),
        "brand": parsed["brand"],
        "product_hint": parsed["product_hint"],
        "old_size": parsed["old_size"],
        "old_unit": parsed["old_unit"],
        "new_size": parsed["new_size"],
        "new_unit": parsed["new_unit"],
        "old_price": parsed["old_price"],
        "new_price": parsed["new_price"],
        "explicit_from_to": parsed["explicit_from_to"],
        "fields_found": parsed["fields_found"],
        "score": post.get("score", 0),
        "num_comments": post.get("num_comments", 0),
        "date_noticed": date_noticed,
    }


# ---------------------------------------------------------------------------
# Promote auto entries to products + events
# ---------------------------------------------------------------------------

def promote_auto_entries(sb: "SupabaseClient", log) -> int:
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
        date_noticed = entry.get("date_noticed") or entry.get("posted_utc", "")[:10]

        # Guess category from product info
        category = guess_category(f"{product_name} {brand or ''}")

        try:
            # Upsert product
            sb.table("products").upsert({
                "upc": upc,
                "name": product_name,
                "brand": brand,
                "category": category,
                "current_size": new_s,
                "unit": unit,
                "type": "shrinkflation",
                "repeat_offender": False,
                "source": "reddit_bot"
            }, on_conflict="upc").execute()

            # Upsert event (prevent duplicates)
            sb.table("events").upsert({
                "upc": upc,
                "date": date_noticed,
                "old_size": old_s,
                "new_size": new_s,
                "unit": unit,
                "pct": pct,
                "price_before": entry.get("old_price"),
                "price_after": entry.get("new_price"),
                "type": "shrinkflation",
                "notes": f"Auto-imported from r/shrinkflation: {entry.get('source_url', '')}",
                "source": "reddit_bot"
            }, on_conflict="upc,date,source").execute()

            # Mark as promoted
            sb.table("reddit_staging").update({"status": "promoted"}).eq("id", entry["id"]).execute()
            promoted += 1
            log.info(f"  ✅ Promoted: {product_name} ({brand}) — {old_s}{unit} → {new_s}{unit} [{date_noticed}]")

        except Exception as exc:
            log.warning(f"  ❌ Promotion failed for {entry.get('id', '?')}: {exc}")

    return promoted


# ---------------------------------------------------------------------------
# Main scraping logic
# ---------------------------------------------------------------------------

def process_posts(posts: list, known_urls: set, log) -> tuple:
    """Process a list of posts, return (entries, new_urls, stats)."""
    entries = []
    new_urls = set()
    stats = {"seen": 0, "skipped_dup": 0, "auto": 0, "review": 0, "discard": 0, "no_keyword": 0}

    for post in posts:
        stats["seen"] += 1
        permalink = post.get("permalink", "")
        url = f"https://reddit.com{permalink}" if permalink.startswith("/") else permalink

        # Dedup
        if url in known_urls:
            stats["skipped_dup"] += 1
            continue

        # Combine title + selftext
        title = post.get("title", "")
        selftext = post.get("selftext", "") or ""
        full_text = f"{title}\n{selftext}"

        # Dedicated subs: every post is likely relevant
        # General subs: require keyword match + minimum score to filter noise
        subreddit = post.get("subreddit", "").lower()
        is_dedicated = subreddit in DEDICATED_SUBREDDITS

        if not is_dedicated:
            # Score gate: skip low-engagement posts from general subs
            score = post.get("score", 0)
            if score < MIN_SCORE_GENERAL:
                stats["no_keyword"] += 1
                new_urls.add(url)
                continue
            # Keyword gate: must mention shrinkflation concepts
            if not SHRINK_KEYWORDS.search(full_text):
                stats["no_keyword"] += 1
                new_urls.add(url)
                continue

        parsed = parse_text(full_text)

        # Vision analysis: if text parsing is weak and post has an image,
        # use Claude vision to extract product details from the photo.
        image_url = _extract_image_url(post)
        vision_result = None
        if HAS_VISION and should_analyze(parsed, image_url):
            vision_result = analyze_image(image_url, title)
            if vision_result:
                parsed = merge_vision_into_parsed(parsed, vision_result)
                stats.setdefault("vision_analyzed", 0)
                stats["vision_analyzed"] += 1

        tier = confidence_tier(parsed, subreddit=subreddit, text=full_text)

        # Visual-only shrinkflation: vision confirmed shrinkflation but no
        # numbers could be extracted. Force to review tier for human judgment.
        if vision_result and vision_result.get("visual_only") and tier == "discard":
            tier = "review"
        stats[tier] += 1

        if tier != "discard":
            entry = build_entry(post, parsed, tier)
            # Attach vision metadata if available
            if vision_result:
                entry["ai_description"] = vision_result.get("description")
                entry["visual_only"] = bool(vision_result.get("visual_only"))
            entries.append(entry)

            ts = post.get("created_utc", 0)
            date_str = datetime.utcfromtimestamp(ts).strftime("%Y-%m") if ts else "?"
            log.info(f"  [{tier.upper():6}] [{date_str}] {title[:70]}")

        new_urls.add(url)

    return entries, new_urls, stats


def upsert_to_supabase(sb: "SupabaseClient", entries: list, log) -> int:
    """Upsert entries to reddit_staging table. Returns count upserted."""
    if not entries:
        return 0

    # Batch in chunks of 50
    upserted = 0
    first_error_logged = False
    for i in range(0, len(entries), 50):
        batch = entries[i:i + 50]
        try:
            sb.table("reddit_staging").upsert(
                batch, on_conflict="source_url"
            ).execute()
            upserted += len(batch)
        except Exception as exc:
            if not first_error_logged:
                log.warning(f"  Supabase batch upsert failed (batch {i // 50 + 1}): {exc}")
                first_error_logged = True
            # Try one by one
            for entry in batch:
                try:
                    sb.table("reddit_staging").upsert(
                        entry, on_conflict="source_url"
                    ).execute()
                    upserted += 1
                except Exception as exc2:
                    # Log first few failures with full detail
                    if upserted == 0 and i == 0:
                        log.warning(f"    Single upsert failed: {exc2}")
                        log.warning(f"    Entry keys: {list(entry.keys())}")

    return upserted


def _fetch_recent_one_sub(sub: str, after_utc: int, max_batches: int = 20) -> list:
    """Fetch recent posts for a single subreddit (thread-safe)."""
    log = logging.getLogger("fullcarts")
    log.info(f"\n  --- r/{sub} (recent, max {max_batches} batches) ---")
    before_utc = None
    posts_out = []

    for batch_num in range(1, max_batches + 1):
        posts = fetch_arctic_shift_batch(subreddit=sub, before_utc=before_utc, after_utc=after_utc, limit=100)
        if not posts:
            break

        posts_out.extend(posts)
        oldest_ts = min(p["created_utc"] for p in posts)
        before_utc = int(oldest_ts)

        log.info(f"  r/{sub} batch {batch_num}: {len(posts)} posts (sub total: {len(posts_out)})")
        time.sleep(0.3)

    log.info(f"  r/{sub}: {len(posts_out)} recent posts fetched")
    return posts_out


def fetch_recent_arctic_shift(log, days: int = 7, subreddits: list = None) -> list:
    """Fetch recent posts from the last N days via Arctic Shift API (parallel)."""
    subreddits = subreddits or ALL_SUBREDDITS
    after_utc = int(time.time()) - (days * 86400)
    all_posts = []

    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = {
            pool.submit(_fetch_recent_one_sub, sub, after_utc): sub
            for sub in subreddits
        }
        for fut in as_completed(futures):
            sub = futures[fut]
            try:
                posts = fut.result()
                all_posts.extend(posts)
            except Exception as e:
                log.warning(f"  r/{sub}: fetch failed — {e}")

    return all_posts


def run_recent(log):
    """Fetch recent posts via Arctic Shift API (last 7 days)."""
    log.info("=" * 60)
    log.info("MODE: Recent posts (Arctic Shift API — last 7 days)")
    log.info(f"Subreddits: {', '.join(ALL_SUBREDDITS)}")
    log.info("=" * 60)

    known_urls = load_known_urls(KNOWN_URLS_FILE)

    log.info("\nFetching recent posts from Arctic Shift...")
    all_posts = fetch_recent_arctic_shift(log, days=7)

    # Deduplicate by id
    seen_ids = set()
    unique_posts = []
    for p in all_posts:
        pid = p.get("id")
        if pid and pid not in seen_ids:
            seen_ids.add(pid)
            unique_posts.append(p)

    log.info(f"\nTotal unique posts fetched: {len(unique_posts)}")

    entries, new_urls, stats = process_posts(unique_posts, known_urls, log)

    # Save to Supabase
    if HAS_SUPABASE and SUPABASE_KEY:
        sb = create_client(SUPABASE_URL, SUPABASE_KEY)
        upserted = upsert_to_supabase(sb, entries, log)
        log.info(f"\nSupabase: upserted {upserted} entries to reddit_staging")

        promoted = promote_auto_entries(sb, log)
        log.info(f"Auto-promoted {promoted} entries to products + events")
    else:
        # Save locally
        local_file = OUTPUT_DIR / "public_staging.json"
        existing = json.loads(local_file.read_text()) if local_file.exists() else []
        existing.extend(entries)
        local_file.write_text(json.dumps(existing, indent=2, ensure_ascii=False))
        log.info(f"\nSaved {len(entries)} entries to {local_file}")

    # Update known URLs
    known_urls |= new_urls
    save_known_urls(KNOWN_URLS_FILE, known_urls)

    # Summary
    log.info("\n" + "=" * 60)
    log.info(f"Recent scrape complete — seen:{stats['seen']}  dupes:{stats['skipped_dup']}  "
             f"no-keyword:{stats['no_keyword']}")
    log.info(f"  auto:{stats['auto']}  review:{stats['review']}  discard:{stats['discard']}")
    if stats.get("vision_analyzed"):
        log.info(f"  vision analyzed: {stats['vision_analyzed']} images")


def run_backfill(log):
    """Historical backfill via Arctic Shift archive API."""
    log.info("=" * 60)
    log.info("MODE: Historical backfill (Arctic Shift archive)")
    log.info(f"Subreddits: {', '.join(ALL_SUBREDDITS)}")
    log.info("=" * 60)

    known_urls = load_known_urls(KNOWN_URLS_FILE)

    log.info("\nFetching ALL historical posts from Arctic Shift...")
    all_posts = fetch_all_arctic_shift(log)
    log.info(f"\nTotal historical posts fetched: {len(all_posts)}")

    if not all_posts:
        log.warning("No posts returned from Arctic Shift — API may be down")
        return

    # Sort by date for nice logging
    all_posts.sort(key=lambda p: p.get("created_utc", 0))

    oldest = datetime.utcfromtimestamp(all_posts[0]["created_utc"]).strftime("%Y-%m-%d")
    newest = datetime.utcfromtimestamp(all_posts[-1]["created_utc"]).strftime("%Y-%m-%d")
    log.info(f"Date range: {oldest} → {newest}")

    entries, new_urls, stats = process_posts(all_posts, known_urls, log)

    # Save to Supabase
    if HAS_SUPABASE and SUPABASE_KEY:
        sb = create_client(SUPABASE_URL, SUPABASE_KEY)
        upserted = upsert_to_supabase(sb, entries, log)
        log.info(f"\nSupabase: upserted {upserted} entries to reddit_staging")

        promoted = promote_auto_entries(sb, log)
        log.info(f"Auto-promoted {promoted} entries to products + events")
    else:
        local_file = OUTPUT_DIR / "backfill_staging.json"
        existing = json.loads(local_file.read_text()) if local_file.exists() else []
        existing.extend(entries)
        local_file.write_text(json.dumps(existing, indent=2, ensure_ascii=False))
        log.info(f"\nSaved {len(entries)} entries to {local_file}")

    # Update known URLs
    known_urls |= new_urls
    save_known_urls(KNOWN_URLS_FILE, known_urls)

    # Summary
    log.info("\n" + "=" * 60)
    log.info(f"Backfill complete — seen:{stats['seen']}  dupes:{stats['skipped_dup']}  "
             f"no-keyword:{stats['no_keyword']}")
    log.info(f"  auto:{stats['auto']}  review:{stats['review']}  discard:{stats['discard']}")
    if stats.get("vision_analyzed"):
        log.info(f"  vision analyzed: {stats['vision_analyzed']} images")

    # Year-by-year breakdown
    year_counts = {}
    for entry in entries:
        year = entry.get("date_noticed", "????")[:4]
        year_counts[year] = year_counts.get(year, 0) + 1
    log.info("\nEntries by year:")
    for year in sorted(year_counts):
        log.info(f"  {year}: {year_counts[year]}")


def run_promote_only(log):
    """Just promote pending auto entries — no scraping."""
    log.info("=" * 60)
    log.info("MODE: Promote only")
    log.info("=" * 60)

    if not HAS_SUPABASE or not SUPABASE_KEY:
        log.error("SUPABASE_KEY required for promote-only mode")
        return

    sb = create_client(SUPABASE_URL, SUPABASE_KEY)
    promoted = promote_auto_entries(sb, log)
    log.info(f"\nPromoted {promoted} entries to products + events")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)s  %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    log = logging.getLogger("fullcarts")

    parser = argparse.ArgumentParser(description="FullCarts Public Reddit Scraper (no API key needed)")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--backfill", action="store_true",
                       help="Historical backfill of ALL r/shrinkflation posts via Arctic Shift")
    group.add_argument("--recent", action="store_true",
                       help="Fetch recent posts from the last 7 days via Arctic Shift (default)")
    group.add_argument("--promote-only", action="store_true",
                       help="Skip scraping, just promote staged auto entries")
    args = parser.parse_args()

    if args.backfill:
        run_backfill(log)
    elif args.promote_only:
        run_promote_only(log)
    else:
        run_recent(log)
