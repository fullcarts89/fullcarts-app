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
import signal
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

# Reddit public JSON API — no credentials needed, used as fallback
# when Arctic Shift has no recent data (its archive lags by months).
REDDIT_LISTING_URL = "https://www.reddit.com/r/{subreddit}/{sort}.json"
REDDIT_SEARCH_URL = "https://www.reddit.com/r/{subreddit}/search.json"

# Retry config for API calls
MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 2  # seconds — exponential: 2, 4, 8

# Output for local fallback
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "."))
KNOWN_URLS_FILE = OUTPUT_DIR / "known_urls_public.txt"

# Confidence thresholds
TIER_AUTO_THRESHOLD = 3    # fields found → auto-accept
TIER_REVIEW_THRESHOLD = 1  # fields found → review queue

# Time budget: stop processing new posts before the CI timeout kills us.
# This leaves time for upsert, triage, and saving known_urls.
MAX_PROCESSING_MINUTES = int(os.getenv("MAX_PROCESSING_MINUTES", "50"))

# Global start time — set in main
_START_TIME = None

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
# Retry helper
# ---------------------------------------------------------------------------

def _request_with_retry(method: str, url: str, **kwargs) -> requests.Response | None:
    """Make an HTTP request with exponential backoff on failure.

    Returns the Response on success, or None after all retries exhausted.
    Handles 429 (rate-limit) and 403 (blocked) with longer waits.
    """
    log = logging.getLogger("fullcarts")
    kwargs.setdefault("timeout", 15)
    kwargs.setdefault("headers", {"User-Agent": USER_AGENT})

    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.request(method, url, **kwargs)

            if resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", RETRY_BACKOFF_BASE ** (attempt + 1)))
                log.warning(f"  Rate-limited (429), waiting {retry_after}s (attempt {attempt + 1})")
                time.sleep(retry_after)
                continue

            if resp.status_code == 403:
                wait = RETRY_BACKOFF_BASE ** (attempt + 1)
                log.warning(f"  Blocked (403) from {url[:60]}, waiting {wait}s (attempt {attempt + 1})")
                time.sleep(wait)
                continue

            resp.raise_for_status()
            return resp

        except requests.exceptions.RequestException as e:
            wait = RETRY_BACKOFF_BASE ** (attempt + 1)
            log.warning(f"  Request failed: {e} — retrying in {wait}s (attempt {attempt + 1}/{MAX_RETRIES})")
            time.sleep(wait)

    log.warning(f"  All {MAX_RETRIES} retries exhausted for {url[:80]}")
    return None


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

    resp = _request_with_retry("GET", ARCTIC_SHIFT_URL, params=params)
    if resp is None:
        return []
    try:
        return resp.json().get("data", [])
    except Exception as e:
        logging.getLogger("fullcarts").warning(f"Arctic Shift JSON parse failed: {e}")
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
# Reddit public JSON API fallback (for recent posts)
# ---------------------------------------------------------------------------
# Arctic Shift's archive lags behind by months, so recent posts (last 7 days)
# are often missing. Reddit's public JSON API provides real-time listings
# without authentication (rate-limited to ~60 req/min unauthenticated).

def _normalize_reddit_post(post_data: dict) -> dict:
    """Normalize a Reddit API post object to match Arctic Shift's format.

    Arctic Shift and Reddit's API use the same field names for most fields,
    but Reddit wraps each post in {"kind": "t3", "data": {...}}.
    """
    d = post_data.get("data", post_data) if "data" in post_data else post_data
    return d


def _fetch_reddit_listing(subreddit: str, sort: str = "new",
                          after_token: str = None, limit: int = 100) -> tuple[list, str | None]:
    """Fetch a page of posts from Reddit's public JSON listing API.

    Returns (posts, after_token). after_token is None when no more pages.
    """
    url = REDDIT_LISTING_URL.format(subreddit=subreddit, sort=sort)
    params = {"limit": min(limit, 100), "raw_json": 1}
    if after_token:
        params["after"] = after_token

    resp = _request_with_retry("GET", url, params=params)
    if resp is None:
        return [], None

    try:
        data = resp.json().get("data", {})
        children = data.get("children", [])
        posts = [_normalize_reddit_post(c) for c in children]
        next_after = data.get("after")
        return posts, next_after
    except Exception as e:
        logging.getLogger("fullcarts").warning(f"Reddit listing parse failed: {e}")
        return [], None


def _fetch_recent_reddit_one_sub(sub: str, after_utc: int, max_pages: int = 10) -> list:
    """Fetch recent posts for a subreddit from Reddit's public JSON API."""
    log = logging.getLogger("fullcarts")
    log.info(f"\n  --- r/{sub} (Reddit JSON fallback, max {max_pages} pages) ---")

    all_posts = []
    after_token = None

    for page in range(1, max_pages + 1):
        posts, after_token = _fetch_reddit_listing(sub, sort="new", after_token=after_token)
        if not posts:
            break

        # Filter to posts within the time window
        for post in posts:
            created = post.get("created_utc", 0)
            if created >= after_utc:
                all_posts.append(post)
            else:
                # Posts are sorted newest-first, so once we pass the cutoff, stop
                log.info(f"  r/{sub} page {page}: reached time cutoff, stopping")
                after_token = None
                break

        log.info(f"  r/{sub} page {page}: {len(posts)} posts (total: {len(all_posts)})")

        if not after_token:
            break

        # Rate limit: Reddit allows ~60 req/min unauthenticated
        time.sleep(1.5)

    log.info(f"  r/{sub}: {len(all_posts)} recent posts via Reddit JSON API")
    return all_posts


def fetch_recent_reddit_json(log, days: int = 7, subreddits: list = None) -> list:
    """Fetch recent posts from Reddit's public JSON API (sequential, rate-limited).

    Used as a fallback when Arctic Shift has no recent data.
    """
    subreddits = subreddits or ALL_SUBREDDITS
    after_utc = int(time.time()) - (days * 86400)
    all_posts = []

    # Sequential to respect Reddit's rate limits (no auth = strict limits)
    for sub in subreddits:
        try:
            posts = _fetch_recent_reddit_one_sub(sub, after_utc)
            all_posts.extend(posts)
        except Exception as e:
            log.warning(f"  r/{sub}: Reddit JSON fetch failed — {e}")

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


def _extract_image_url(post: dict, skip_reddit_fallback: bool = False) -> str | None:
    """Return a direct image URL from an Arctic Shift post dict, or None.

    Handles direct image links, gallery posts (media_metadata),
    preview images, and optionally falls back to Reddit's JSON API.
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
    # Fetch directly from Reddit's JSON API (slow — skipped during backfill)
    if not skip_reddit_fallback:
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
                has_vision: bool = False,
                skip_reddit_fallback: bool = False) -> dict:
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
        "image_url": _extract_image_url(post, skip_reddit_fallback=skip_reddit_fallback),
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

    resp = _request_with_retry(
        "GET", ARCTIC_SHIFT_COMMENTS_URL,
        params={
            "link_id": post_id,
            "parent_id": "",  # top-level only
            "limit": 10,
            "sort": "asc",
            "fields": "author,body,distinguished",
        },
    )
    if resp is None:
        return False
    try:
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

def _time_remaining() -> float:
    """Seconds remaining before the processing budget expires."""
    if _START_TIME is None:
        return float("inf")
    elapsed = time.time() - _START_TIME
    return max(0, MAX_PROCESSING_MINUTES * 60 - elapsed)


def process_posts(posts: list, known_urls: set, log, skip_vision: bool = False) -> tuple:
    """Process a list of posts, return (entries, new_urls, stats)."""
    global _sigterm_new_urls

    entries = []
    new_urls = set()
    # Point the global at this set so the SIGTERM handler can see URLs
    # accumulated during processing (not just after we return).
    _sigterm_new_urls = new_urls
    stats = {"seen": 0, "skipped_dup": 0, "mod_removed": 0, "auto": 0, "review": 0, "discard": 0, "no_keyword": 0}

    for post in posts:
        # Time budget: stop processing so we have time to save results
        if _time_remaining() < 120:  # 2-minute buffer for upsert/save
            remaining = len(posts) - stats["seen"]
            log.warning(f"  Time budget reached ({MAX_PROCESSING_MINUTES}min). "
                        f"Stopping with {remaining} posts unprocessed.")
            stats["timed_out"] = remaining
            break

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

        # Early discard: general sub posts with no extractable fields are noise
        if not is_dedicated and parsed["fields_found"] == 0:
            stats["discard"] += 1
            new_urls.add(url)
            continue

        # Vision analysis: only for dedicated subs where posts are likely
        # relevant. General subs produce too many weak matches to justify
        # the cost and latency of vision calls.
        image_url = _extract_image_url(post, skip_reddit_fallback=skip_vision)
        vision_result = None
        if is_dedicated and not skip_vision and HAS_VISION and should_analyze(parsed, image_url):
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
            entry = build_entry(post, parsed, tier, has_vision=bool(vision_result),
                                skip_reddit_fallback=skip_vision)
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


def _detect_staging_columns(sb) -> set | None:
    """Query reddit_staging to discover which columns actually exist.

    Returns a set of column names, or None if detection fails.
    """
    try:
        # Fetch one row (or empty result) to see the column names
        result = sb.table("reddit_staging").select("*").limit(1).execute()
        if result.data:
            return set(result.data[0].keys())
        # Empty table — try inserting nothing to get column info from schema
        # Fall back to a known safe set
        return None
    except Exception:
        return None


def _strip_unknown_columns(entries: list, known_columns: set | None, log) -> list:
    """Remove keys from entries that don't exist as columns in the DB.

    This prevents 400 errors when migrations haven't been applied yet.
    """
    if known_columns is None:
        return entries

    # Never strip core fields — only strip enrichment fields that might
    # not exist if a migration hasn't been applied
    sample = entries[0] if entries else {}
    unknown = set(sample.keys()) - known_columns - {"id", "created_at"}
    if not unknown:
        return entries

    log.warning(f"  Stripping columns not in DB: {sorted(unknown)}")
    return [{k: v for k, v in e.items() if k not in unknown} for e in entries]


def _upsert_via_rest(entries: list, log) -> int:
    """Fallback: upsert directly via PostgREST HTTP API using requests.

    Bypasses supabase-py entirely in case the library version is sending
    incompatible headers or parameters.
    """
    if not SUPABASE_KEY:
        return 0

    url = f"{SUPABASE_URL}/rest/v1/reddit_staging"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=minimal",
    }
    params = {"on_conflict": "source_url"}

    upserted = 0
    for i in range(0, len(entries), 50):
        batch = entries[i:i + 50]
        try:
            resp = requests.post(url, json=batch, headers=headers,
                                 params=params, timeout=30)
            if resp.status_code in (200, 201):
                upserted += len(batch)
            else:
                log.warning(f"  REST fallback batch {i // 50 + 1} failed: "
                            f"{resp.status_code} {resp.text[:300]}")
                # Try one by one to isolate bad entries
                for entry in batch:
                    try:
                        resp = requests.post(url, json=entry, headers=headers,
                                             params=params, timeout=15)
                        if resp.status_code in (200, 201):
                            upserted += 1
                        elif upserted == 0:
                            log.warning(f"    Single REST upsert failed: "
                                        f"{resp.status_code} {resp.text[:200]}")
                            log.warning(f"    Entry keys: {list(entry.keys())}")
                            # Log a sample value to help diagnose type issues
                            for k, v in entry.items():
                                if v is not None:
                                    log.warning(f"      {k}: {type(v).__name__} = {str(v)[:80]}")
                    except Exception as exc2:
                        log.warning(f"    Single REST request failed: {exc2}")
        except Exception as exc:
            log.warning(f"  REST fallback request error: {exc}")

    return upserted


def upsert_to_supabase(sb: "SupabaseClient", entries: list, log) -> int:
    """Upsert entries to reddit_staging table. Returns count upserted."""
    if not entries:
        return 0

    # Detect which columns actually exist in the DB and strip any that
    # don't. This prevents 400 errors when migrations haven't been applied.
    known_cols = _detect_staging_columns(sb)
    entries = _strip_unknown_columns(entries, known_cols, log)

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
            # default_to_null=False prevents supabase-py from sending a
            # `columns` query param that can break newer PostgREST versions.
            sb.table("reddit_staging").upsert(
                batch, on_conflict="source_url",
                ignore_duplicates=False,
                default_to_null=False,
            ).execute()
            upserted += len(batch)
        except Exception as exc:
            if not first_error_logged:
                # Log the full error including response body
                exc_msg = str(exc)
                resp_body = ""
                if hasattr(exc, "response") and exc.response is not None:
                    resp_body = getattr(exc.response, "text", "")[:500]
                log.warning(f"  Supabase upsert batch {i // 50 + 1} failed: "
                            f"{exc_msg[:200]}")
                if resp_body:
                    log.warning(f"  Response body: {resp_body}")
                first_error_logged = True

            # Try one by one
            for entry in batch:
                try:
                    sb.table("reddit_staging").upsert(
                        entry, on_conflict="source_url",
                        ignore_duplicates=False,
                        default_to_null=False,
                    ).execute()
                    upserted += 1
                except Exception as exc2:
                    if upserted == 0 and i == 0:
                        log.warning(f"    Single upsert failed: {exc2}")
                        log.warning(f"    Entry keys: {list(entry.keys())}")

    # If supabase-py upserts all failed, try the raw REST API as fallback
    if upserted == 0 and entries:
        log.warning(f"  All supabase-py upserts failed. "
                    f"Trying direct REST API fallback...")
        upserted = _upsert_via_rest(entries, log)
        if upserted > 0:
            log.info(f"  REST fallback succeeded: {upserted} entries upserted")

    return upserted


# ---------------------------------------------------------------------------
# Auto-triage: reduce manual review queue
# ---------------------------------------------------------------------------
# Thresholds (adjustable)
TRIAGE_AUTO_PROMOTE_SCORE = 70   # confidence_score >= this → auto-promote
TRIAGE_AUTO_DISMISS_SCORE = 25   # confidence_score < this → auto-dismiss


def triage_staging(sb: "SupabaseClient", log) -> dict:
    """Auto-promote and auto-dismiss staging entries to shrink the review queue.

    Runs after upsert. Only touches status='pending' entries.

    Auto-PROMOTE (confidence_score >= 70, tier='auto'):
      - Must have brand, old_size, new_size, explicit_from_to
      - new_size must be < old_size (actually shrinkflation)
      - Uses promote_staging.promote_entry() for the full pipeline

    Auto-DISMISS (confidence_score < 25):
      - Low signal entries unlikely to be useful

    Returns dict with counts: {promoted, dismissed, remaining}
    """
    stats = {"promoted": 0, "dismissed": 0, "remaining": 0, "promote_failed": 0}

    # --- Auto-dismiss low-confidence entries ---
    try:
        result = (sb.table("reddit_staging")
                  .select("id")
                  .eq("status", "pending")
                  .lt("confidence_score", TRIAGE_AUTO_DISMISS_SCORE)
                  .execute())
        dismiss_ids = [r["id"] for r in (result.data or [])]
    except Exception as exc:
        log.warning(f"  Triage: failed to query low-confidence entries: {exc}")
        dismiss_ids = []

    for i in range(0, len(dismiss_ids), 100):
        batch = dismiss_ids[i:i + 100]
        try:
            sb.table("reddit_staging").update({
                "status": "dismissed",
                "reviewed_by": "auto-triage",
            }).in_("id", batch).execute()
            stats["dismissed"] += len(batch)
        except Exception as exc:
            log.warning(f"  Triage: dismiss batch failed: {exc}")

    # --- Auto-promote high-confidence entries ---
    try:
        result = (sb.table("reddit_staging")
                  .select("*")
                  .eq("status", "pending")
                  .eq("tier", "auto")
                  .gte("confidence_score", TRIAGE_AUTO_PROMOTE_SCORE)
                  .eq("explicit_from_to", True)
                  .execute())
        candidates = result.data or []
    except Exception as exc:
        log.warning(f"  Triage: failed to query auto-promote candidates: {exc}")
        candidates = []

    # Lazy import to avoid circular deps
    try:
        from backend.jobs.promote_staging import promote_entry
        has_promoter = True
    except ImportError:
        has_promoter = False
        log.info("  Triage: promote_staging not available, skipping auto-promote")

    if has_promoter:
        for entry in candidates:
            # Safety checks: must have brand + both sizes + shrinkage
            brand = entry.get("brand")
            old_size = entry.get("old_size")
            new_size = entry.get("new_size")
            if not brand or not old_size or not new_size:
                continue
            if float(new_size) >= float(old_size):
                continue  # Not shrinkflation
            try:
                ok = promote_entry(sb, entry)
                if ok:
                    stats["promoted"] += 1
                else:
                    stats["promote_failed"] += 1
            except Exception as exc:
                log.warning(f"  Triage: promote failed for {entry.get('id', '?')}: {exc}")
                stats["promote_failed"] += 1

    # --- Count remaining ---
    try:
        result = (sb.table("reddit_staging")
                  .select("id", count="exact")
                  .eq("status", "pending")
                  .execute())
        stats["remaining"] = result.count or 0
    except Exception:
        stats["remaining"] = -1

    return stats


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
    """Fetch recent posts, trying Arctic Shift first then Reddit JSON fallback."""
    global _sigterm_known_urls

    log.info("=" * 60)
    log.info("MODE: Recent posts (last 7 days)")
    log.info(f"Subreddits: {', '.join(ALL_SUBREDDITS)}")
    log.info(f"Time budget: {MAX_PROCESSING_MINUTES} minutes")
    log.info("=" * 60)

    known_urls = load_known_urls(KNOWN_URLS_FILE)
    known_urls |= _load_existing_urls_from_supabase(log)
    _sigterm_known_urls = known_urls  # expose to SIGTERM handler

    # Try Arctic Shift first (best for bulk data, but lags behind real-time)
    log.info("\nFetching recent posts from Arctic Shift...")
    all_posts = fetch_recent_arctic_shift(log, days=7)

    # Fallback: if Arctic Shift returned few/no posts, use Reddit's public
    # JSON API. Arctic Shift's archive often lags months behind, so recent
    # posts may not be available there.
    if len(all_posts) < 5:
        log.info(f"\nArctic Shift returned only {len(all_posts)} posts — "
                 f"falling back to Reddit public JSON API...")
        reddit_posts = fetch_recent_reddit_json(log, days=7)
        all_posts.extend(reddit_posts)
        log.info(f"  Combined total: {len(all_posts)} posts "
                 f"(Arctic Shift + Reddit JSON)")

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

        # Auto-triage: promote high-confidence, dismiss low-confidence
        log.info("\nRunning auto-triage to reduce manual review queue...")
        triage = triage_staging(sb, log)
        log.info(f"  Auto-promoted: {triage['promoted']}  "
                 f"Auto-dismissed: {triage['dismissed']}  "
                 f"Remaining for review: {triage['remaining']}")
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
    if stats.get("timed_out"):
        log.warning(f"  TIMED OUT: {stats['timed_out']} posts left unprocessed "
                    f"(will be picked up next run)")
    elapsed = time.time() - (_START_TIME or time.time())
    log.info(f"  Total elapsed: {elapsed / 60:.1f} minutes")


def run_backfill(log, skip_vision: bool = False):
    """Historical backfill via Arctic Shift archive API."""
    global _sigterm_known_urls

    log.info("=" * 60)
    log.info("MODE: Historical backfill (Arctic Shift archive)")
    log.info(f"Subreddits: {', '.join(ALL_SUBREDDITS)}")
    log.info(f"Time budget: {MAX_PROCESSING_MINUTES} minutes")
    log.info("=" * 60)

    known_urls = load_known_urls(KNOWN_URLS_FILE)
    known_urls |= _load_existing_urls_from_supabase(log)
    _sigterm_known_urls = known_urls

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

    if skip_vision:
        log.info("Vision analysis SKIPPED (--skip-vision). Use --backfill-images later to enrich.")
    entries, new_urls, stats = process_posts(all_posts, known_urls, log, skip_vision=skip_vision)

    # Save to Supabase
    if HAS_SUPABASE and SUPABASE_KEY:
        sb = create_client(SUPABASE_URL, SUPABASE_KEY)
        upserted = upsert_to_supabase(sb, entries, log)
        log.info(f"\nSupabase: upserted {upserted} entries to reddit_staging")

        # Auto-triage: promote high-confidence, dismiss low-confidence
        log.info("\nRunning auto-triage to reduce manual review queue...")
        triage = triage_staging(sb, log)
        log.info(f"  Auto-promoted: {triage['promoted']}  "
                 f"Auto-dismissed: {triage['dismissed']}  "
                 f"Remaining for review: {triage['remaining']}")
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


def run_triage_only(log):
    """Run auto-triage on existing pending entries without scraping."""
    log.info("=" * 60)
    log.info("MODE: Auto-triage existing pending entries")
    log.info(f"  Promote threshold: confidence_score >= {TRIAGE_AUTO_PROMOTE_SCORE}")
    log.info(f"  Dismiss threshold: confidence_score < {TRIAGE_AUTO_DISMISS_SCORE}")
    log.info("=" * 60)

    if not HAS_SUPABASE or not SUPABASE_KEY:
        log.error("SUPABASE_KEY required for triage")
        return

    sb = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Show current queue size
    try:
        result = (sb.table("reddit_staging")
                  .select("id", count="exact")
                  .eq("status", "pending")
                  .execute())
        log.info(f"\nPending entries before triage: {result.count or 0}")
    except Exception:
        pass

    triage = triage_staging(sb, log)
    log.info(f"\nTriage complete:")
    log.info(f"  Auto-promoted: {triage['promoted']}")
    log.info(f"  Auto-dismissed: {triage['dismissed']}")
    if triage.get("promote_failed"):
        log.info(f"  Promote failures: {triage['promote_failed']}")
    log.info(f"  Remaining for manual review: {triage['remaining']}")


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

    _START_TIME = time.time()

    # SIGTERM handler: GitHub Actions sends SIGTERM on cancellation.
    # Save known_urls so the next run can skip already-processed posts.
    _sigterm_known_urls = set()
    _sigterm_new_urls = set()

    def _handle_sigterm(signum, frame):
        log.warning("SIGTERM received — saving known URLs before exit")
        combined = _sigterm_known_urls | _sigterm_new_urls
        if combined:
            save_known_urls(KNOWN_URLS_FILE, combined)
            log.info(f"  Saved {len(combined)} known URLs on SIGTERM")
        raise SystemExit(1)

    signal.signal(signal.SIGTERM, _handle_sigterm)

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
    group.add_argument("--triage-only", action="store_true",
                       help="Run auto-triage on existing pending entries (no scraping)")
    parser.add_argument("--skip-vision", action="store_true",
                        help="Skip Claude vision analysis during backfill (use --backfill-images later)")
    args = parser.parse_args()

    if args.backfill:
        run_backfill(log, skip_vision=args.skip_vision)
    elif args.promote_only:
        run_promote_only(log)
    elif args.backfill_images:
        run_backfill_images(log)
    elif args.triage_only:
        run_triage_only(log)
    else:
        run_recent(log)
