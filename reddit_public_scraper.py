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
ARCTIC_SHIFT_COMMENTS_URL = "https://arctic-shift.photon-reddit.com/api/comments/search"

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

# Retailer detection — extract where the product was spotted
KNOWN_RETAILERS = [
    "walmart", "target", "costco", "sam's club", "sams club", "kroger",
    "safeway", "albertsons", "publix", "heb", "h-e-b", "aldi", "lidl",
    "trader joe's", "trader joes", "whole foods", "amazon", "wegmans",
    "food lion", "stop & shop", "stop and shop", "giant", "meijer",
    "winco", "dollar general", "dollar tree", "family dollar",
    "cvs", "walgreens", "rite aid", "7-eleven", "7 eleven",
]
RETAILER_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(r) for r in KNOWN_RETAILERS) + r")\b",
    re.IGNORECASE,
)

# Region detection from subreddit or text clues
REGION_CLUES = {
    "canada": "CA", "canadian": "CA", "loblaws": "CA", "no frills": "CA",
    "shoppers drug mart": "CA", "dollarama": "CA",
    "uk": "UK", "tesco": "UK", "sainsbury": "UK", "asda": "UK", "aldi uk": "UK",
    "australia": "AU", "woolworths": "AU", "coles": "AU",
}
REGION_SUBREDDITS = {
    "canadianfrugal": "CA", "australia": "AU", "unitedkingdom": "UK",
    "asda": "UK", "tesco": "UK",
}

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

    All tiers now route to the human review queue — 'auto' just means
    higher confidence, but still requires human validation before promotion.
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


def compute_confidence_score(parsed: dict, tier: str, has_vision: bool = False,
                              subreddit: str = "") -> int:
    """Compute a 0-100 numeric confidence score from extraction signals.

    Scores are weighted by signal reliability:
      - Explicit from→to pattern:  +25 (strongest text signal)
      - Brand detected:            +15
      - Fields found:              +8 per field (max 40)
      - Shrinkflation subreddit:   +10 (topical context)
      - Vision analysis enriched:  +10
      - Prices extracted:          +5
    """
    score = 0

    if parsed.get("explicit_from_to"):
        score += 25
    if parsed.get("brand"):
        score += 15

    fields = min(parsed.get("fields_found", 0), 5)
    score += fields * 8

    if subreddit.lower() in DEDICATED_SUBREDDITS:
        score += 10
    if has_vision:
        score += 10
    if parsed.get("old_price") and parsed.get("new_price"):
        score += 5

    return min(score, 100)


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


def _extract_image_url_from_reddit_json(permalink: str) -> str | None:
    """Fetch image URL directly from Reddit's public JSON API.

    Used as a fallback when Arctic Shift doesn't include media_metadata
    (common for gallery posts).
    """
    if not permalink:
        return None
    try:
        json_url = f"https://www.reddit.com{permalink}.json" if permalink.startswith("/") else f"{permalink}.json"
        resp = requests.get(json_url, headers={"User-Agent": USER_AGENT}, timeout=10)
        if resp.status_code == 429:
            time.sleep(2)
            resp = requests.get(json_url, headers={"User-Agent": USER_AGENT}, timeout=10)
        if resp.status_code != 200:
            return None
        data = resp.json()
        post = data[0]["data"]["children"][0]["data"]

        # Direct image
        url = post.get("url") or ""
        if re.search(r"\.(jpg|jpeg|png|gif|webp)(\?|$)", url, re.IGNORECASE):
            return url[:500]
        if any(d in url for d in _IMAGE_DOMAINS):
            return url[:500]

        # Gallery media_metadata
        meta = post.get("media_metadata")
        if meta and isinstance(meta, dict):
            for item in meta.values():
                src = item.get("s", {})
                img_url = src.get("u") or src.get("gif")
                if img_url:
                    return img_url.replace("&amp;", "&")[:500]

        # Preview images
        images = post.get("preview", {}).get("images", [])
        if images:
            img_url = images[0].get("source", {}).get("url")
            if img_url:
                return img_url.replace("&amp;", "&")[:500]

    except Exception as e:
        logging.getLogger("fullcarts").debug(f"Reddit JSON fallback failed for {permalink}: {e}")
    return None


def _extract_image_url(post: dict) -> str | None:
    """Return a direct image URL from an Arctic Shift post dict, or None.

    Handles direct image links, gallery posts (media_metadata),
    preview images, and falls back to Reddit's JSON API.
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
            if item.get("status") != "valid" or item.get("e") not in ("Image", "AnimatedImage"):
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

    # Fallback: gallery posts or posts where Arctic Shift lacks image data
    # Fetch directly from Reddit's JSON API
    is_gallery = post.get("is_gallery") or "/gallery/" in url
    permalink = post.get("permalink") or ""
    if is_gallery or (permalink and not url.endswith(tuple(".jpg .jpeg .png .gif .webp".split()))):
        reddit_img = _extract_image_url_from_reddit_json(permalink)
        if reddit_img:
            return reddit_img

    return None


def detect_retailer(text: str) -> str | None:
    """Extract retailer name from post text."""
    m = RETAILER_PATTERN.search(text)
    return m.group(0).title() if m else None


def detect_region(text: str, subreddit: str = "") -> str:
    """Detect geographic region from text and subreddit clues."""
    sub_lower = subreddit.lower()
    if sub_lower in REGION_SUBREDDITS:
        return REGION_SUBREDDITS[sub_lower]
    text_lower = text.lower()
    for clue, region in REGION_CLUES.items():
        if clue in text_lower:
            return region
    return "US"


def build_entry(post: dict, parsed: dict, tier: str,
                has_vision: bool = False) -> dict:
    """Build a staging entry from a Reddit post + parsed signals."""
    created_utc = post.get("created_utc", 0)
    permalink = post.get("permalink", "")
    subreddit = post.get("subreddit", "shrinkflation")

    # Use the post's month as the "when noticed" date
    if created_utc:
        post_date = datetime.utcfromtimestamp(created_utc)
        # First of the month the post was made
        date_noticed = post_date.strftime("%Y-%m-01")
    else:
        date_noticed = datetime.now(tz=timezone.utc).strftime("%Y-%m-01")

    full_text = f"{post.get('title', '')}\n{post.get('selftext', '')}"

    return {
        "source_url": f"https://reddit.com{permalink}" if permalink.startswith("/") else permalink,
        "subreddit": subreddit,
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
        # New enrichment fields
        "confidence_score": compute_confidence_score(
            parsed, tier, has_vision=has_vision, subreddit=subreddit
        ),
        "extraction_method": "text+vision" if has_vision else "text",
        "retailer": detect_retailer(full_text),
        "region": detect_region(full_text, subreddit),
    }


# ---------------------------------------------------------------------------
# Promote auto entries to products + events
# ---------------------------------------------------------------------------
# NOTE: Auto-promotion has been disabled. ALL entries now require human
# review through the admin review queue before being promoted to the
# products + events tables. The 'auto' tier indicates high confidence
# but still needs validation.
#
# The promote_staging.py backend job handles promotion after human review.


# ---------------------------------------------------------------------------
# Moderator removal detection
# ---------------------------------------------------------------------------

# Patterns that indicate a mod removed a post for not being shrinkflation
MOD_REMOVAL_PATTERNS = re.compile(
    r"not\s+(an?\s+)?(example|instance|case)\s+of\s+shrinkflation"
    r"|not\s+shrinkflation"
    r"|doesn.t\s+(qualify|count)\s+as\s+shrinkflation"
    r"|this\s+is(n.t|\s+not)\s+shrinkflation"
    r"|removed.*not\s+shrinkflation"
    r"|rule\s+\d+.*not\s+shrinkflation",
    re.IGNORECASE,
)


def _is_mod_removed_not_shrinkflation(post: dict) -> bool:
    """Check if a post was removed by mods for not being shrinkflation.

    Uses two signals:
    1. Post-level: title says '[Removed by moderator]' or removed_by_category is set
    2. Comment-level: fetches top-level comments from Arctic Shift and checks
       if a moderator (distinguished=moderator) left a comment matching
       removal patterns like 'Not an example of shrinkflation'.
    """
    post_id = post.get("id", "")

    # Quick check: does the post look removed?
    title = post.get("title", "")
    removed_by = post.get("removed_by_category") or ""
    selftext = post.get("selftext") or ""
    is_removed = (
        "[removed" in title.lower()
        or removed_by in ("moderator", "automod")
        or selftext == "[removed]"
    )

    # If it's not even removed, skip the comment fetch
    if not is_removed:
        return False

    # Fetch top-level comments to check for mod explanation
    if not post_id:
        return False

    try:
        resp = requests.get(
            ARCTIC_SHIFT_COMMENTS_URL,
            params={
                "link_id": post_id,
                "parent_id": "",  # top-level only
                "limit": 10,
                "sort": "asc",
                "fields": "author,body,distinguished",
            },
            headers={"User-Agent": USER_AGENT},
            timeout=10,
        )
        resp.raise_for_status()
        comments = resp.json().get("data", [])
    except Exception:
        return False

    for comment in comments:
        # Only check moderator-distinguished comments
        if comment.get("distinguished") != "moderator":
            continue
        body = comment.get("body") or ""
        if MOD_REMOVAL_PATTERNS.search(body):
            return True

    return False


# ---------------------------------------------------------------------------
# Main scraping logic
# ---------------------------------------------------------------------------

def process_posts(posts: list, known_urls: set, log) -> tuple:
    """Process a list of posts, return (entries, new_urls, stats)."""
    entries = []
    new_urls = set()
    stats = {"seen": 0, "skipped_dup": 0, "mod_removed": 0, "auto": 0, "review": 0, "discard": 0, "no_keyword": 0}

    for post in posts:
        stats["seen"] += 1
        permalink = post.get("permalink", "")
        url = f"https://reddit.com{permalink}" if permalink.startswith("/") else permalink

        # Dedup
        if url in known_urls:
            stats["skipped_dup"] += 1
            continue

        # Skip posts removed by mods for not being shrinkflation
        if _is_mod_removed_not_shrinkflation(post):
            title = post.get("title", "")
            log.info(f"  [MOD-RM] Skipping mod-removed post: {title[:70]}")
            stats["mod_removed"] += 1
            new_urls.add(url)
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
            entry = build_entry(post, parsed, tier, has_vision=bool(vision_result))
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

    # Pre-filter: exclude entries whose source_url already has a non-pending
    # status (promoted/dismissed/rejected). This prevents any possibility of
    # the upsert resetting reviewed records back to 'pending'.
    source_urls = [e["source_url"] for e in entries if e.get("source_url")]
    reviewed_urls = set()
    for chunk_start in range(0, len(source_urls), 200):
        chunk = source_urls[chunk_start:chunk_start + 200]
        try:
            result = (sb.table("reddit_staging")
                      .select("source_url")
                      .in_("source_url", chunk)
                      .neq("status", "pending")
                      .execute())
            reviewed_urls.update(row["source_url"] for row in (result.data or []))
        except Exception:
            pass  # If the check fails, proceed with all entries (safe — upsert uses ignore_duplicates)

    if reviewed_urls:
        entries = [e for e in entries if e.get("source_url") not in reviewed_urls]
        log.info(f"  Skipped {len(reviewed_urls)} already-reviewed entries")

    if not entries:
        return 0

    # Batch in chunks of 50
    upserted = 0
    first_error_logged = False
    for i in range(0, len(entries), 50):
        batch = entries[i:i + 50]
        try:
            sb.table("reddit_staging").upsert(
                batch, on_conflict="source_url",
                ignore_duplicates=True
            ).execute()
            upserted += len(batch)
        except Exception as exc:
            if not first_error_logged:
                log.warning(f"  Supabase batch insert failed (batch {i // 50 + 1}): {exc}")
                first_error_logged = True
            # Try one by one
            for entry in batch:
                try:
                    sb.table("reddit_staging").upsert(
                        entry, on_conflict="source_url",
                        ignore_duplicates=True
                    ).execute()
                    upserted += 1
                except Exception as exc2:
                    # Log first few failures with full detail
                    if upserted == 0 and i == 0:
                        log.warning(f"    Single insert failed: {exc2}")
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


def _load_existing_urls_from_supabase(log) -> set:
    """Load source_urls already in reddit_staging to avoid re-processing."""
    if not (HAS_SUPABASE and SUPABASE_KEY):
        return set()
    try:
        sb = create_client(SUPABASE_URL, SUPABASE_KEY)
        urls = set()
        batch_size = 1000
        offset = 0
        while True:
            result = (sb.table("reddit_staging")
                      .select("source_url")
                      .range(offset, offset + batch_size - 1)
                      .execute())
            rows = result.data or []
            if not rows:
                break
            urls.update(row["source_url"] for row in rows if row.get("source_url"))
            offset += batch_size
        log.info(f"  Loaded {len(urls)} existing URLs from Supabase (skip re-processing)")
        return urls
    except Exception as e:
        log.warning(f"  Could not load existing URLs from Supabase: {e}")
        return set()


def run_recent(log):
    """Fetch recent posts via Arctic Shift API (last 7 days)."""
    log.info("=" * 60)
    log.info("MODE: Recent posts (Arctic Shift API — last 7 days)")
    log.info(f"Subreddits: {', '.join(ALL_SUBREDDITS)}")
    log.info("=" * 60)

    known_urls = load_known_urls(KNOWN_URLS_FILE)
    known_urls |= _load_existing_urls_from_supabase(log)

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
        log.info(f"All entries queued for human review (auto-promotion disabled)")
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
             f"mod-removed:{stats['mod_removed']}  no-keyword:{stats['no_keyword']}")
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
    known_urls |= _load_existing_urls_from_supabase(log)

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
        log.info(f"All entries queued for human review (auto-promotion disabled)")
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
             f"mod-removed:{stats['mod_removed']}  no-keyword:{stats['no_keyword']}")
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


def run_backfill_images(log):
    """Backfill missing image URLs for existing staging rows."""
    log.info("=" * 60)
    log.info("MODE: Backfill missing image URLs")
    log.info("=" * 60)

    if not HAS_SUPABASE or not SUPABASE_KEY:
        log.error("SUPABASE_KEY required for image backfill")
        return

    sb = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Count total rows needing backfill
    all_null = (sb.table("reddit_staging")
                .select("id", count="exact")
                .is_("image_url", "null")
                .not_.is_("source_url", "null")
                .execute())
    total = all_null.count or 0
    log.info(f"Found {total} rows with missing image_url")

    fixed = 0
    processed = 0
    batch_size = 200

    while True:
        # Always query from start — fixed rows drop out of the null filter
        rows = (sb.table("reddit_staging")
                .select("id, source_url")
                .is_("image_url", "null")
                .not_.is_("source_url", "null")
                .limit(batch_size)
                .execute()).data or []

        if not rows:
            break

        fixed_this_batch = 0
        for row in rows:
            processed += 1
            source_url = row.get("source_url") or ""
            permalink = source_url
            if "reddit.com" in source_url:
                parts = source_url.split("reddit.com", 1)
                if len(parts) == 2:
                    permalink = parts[1]

            img_url = _extract_image_url_from_reddit_json(permalink)
            if img_url:
                sb.table("reddit_staging").update({"image_url": img_url}).eq("id", row["id"]).execute()
                fixed += 1
                fixed_this_batch += 1
                log.info(f"  [{processed}/{total}] Fixed: {permalink[:60]}...")
            else:
                log.info(f"  [{processed}/{total}] No image: {permalink[:60]}...")

            # Rate-limit: Reddit allows ~60 req/min unauthenticated
            if processed % 30 == 0:
                log.info(f"  ... rate-limit pause ({processed} done, {fixed} fixed)")
                time.sleep(5)
            else:
                time.sleep(1)

        # If nothing was fixed this batch, remaining rows are truly imageless — stop
        if fixed_this_batch == 0:
            log.info(f"No images found in last batch of {len(rows)} — stopping")
            break

    log.info(f"\nBackfill complete: fixed {fixed}/{total} rows")


def run_promote_only(log):
    """Show pending review queue stats — auto-promotion is disabled.

    All items now require human review through the admin UI.
    Use the review queue at /fullcarts.html#admin to promote entries.
    """
    log.info("=" * 60)
    log.info("MODE: Review queue status")
    log.info("=" * 60)

    if not HAS_SUPABASE or not SUPABASE_KEY:
        log.error("SUPABASE_KEY required")
        return

    sb = create_client(SUPABASE_URL, SUPABASE_KEY)
    pending = sb.table("reddit_staging").select("id", count="exact").eq("status", "pending").execute()
    auto_tier = sb.table("reddit_staging").select("id", count="exact").eq("status", "pending").eq("tier", "auto").execute()
    review_tier = sb.table("reddit_staging").select("id", count="exact").eq("status", "pending").eq("tier", "review").execute()

    log.info(f"\nPending review: {pending.count or 0} total")
    log.info(f"  High confidence (auto tier): {auto_tier.count or 0}")
    log.info(f"  Needs review (review tier): {review_tier.count or 0}")
    log.info(f"\nAuto-promotion is disabled. Use the admin review queue to promote entries.")


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
    group.add_argument("--backfill-images", action="store_true",
                       help="Fetch missing image URLs from Reddit for staging rows")
    args = parser.parse_args()

    if args.backfill:
        run_backfill(log)
    elif args.promote_only:
        run_promote_only(log)
    elif args.backfill_images:
        run_backfill_images(log)
    else:
        run_recent(log)
