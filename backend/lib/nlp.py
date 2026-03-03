"""
NLP / text parsing for shrinkflation signal extraction.
Shared between all scrapers and the admin approval pipeline.

Extracts: brand, product name, old/new sizes, old/new prices, units.
Assigns confidence tiers (auto / review / discard).
"""
import re
from backend.config import TIER_AUTO_THRESHOLD, TIER_REVIEW_THRESHOLD

# ---------------------------------------------------------------------------
# Known brands (120+)
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
    "jimmy dean", "johnsonville", "hillshire",
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
    "red bull",
]

# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

UNIT_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*"
    r"(oz|fl\.?\s*oz|ounce[s]?|lb[s]?|pound[s]?|g|gram[s]?|kg|ml|"
    r"liter[s]?|l|ct|count|pack|piece[s]?|sheet[s]?|roll[s]?|"
    r"sq\.?\s*ft|pt|pint[s]?|qt|quart[s]?|gal|gallon[s]?)",
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
# Unit normalization
# ---------------------------------------------------------------------------

UNIT_MAP = {
    "fl oz": "fl oz", "fl. oz": "fl oz", "ounce": "oz",
    "pound": "lb", "gram": "g", "liter": "l",
    "pint": "pt", "quart": "qt", "gallon": "gal",
    "sheet": "sheets", "roll": "rolls", "piece": "ct",
    "sq ft": "sq ft", "sq. ft": "sq ft",
}


def normalize_unit(u: str) -> str:
    """Normalize unit string to a canonical form."""
    if not u:
        return "oz"
    u = u.lower().strip().rstrip("s")
    return UNIT_MAP.get(u, u)


# ---------------------------------------------------------------------------
# Category guesser
# ---------------------------------------------------------------------------

_CATEGORY_RULES = [
    ("Beverages", r"juice|soda|water|drink|coffee|tea|milk|creamer|gatorade|powerade|lemonade|beer|wine|energy drink"),
    ("Snacks",    r"chip[s]?|cookie|cracker|pretzel|popcorn|candy|chocolate|gum|snack|goldfish|cheeto|dorito|frito|pringles|oreo|ritz|wheat thin"),
    ("Cereal",    r"cereal|oat|granola|cheerio|frosted flake|special k|raisin bran"),
    ("Paper Goods", r"paper towel|toilet paper|tissue|napkin|bounty|charmin|scott|cottonelle|kleenex"),
    ("Household", r"soap|shampoo|conditioner|detergent|cleaner|dish|laundry|tide|dawn|lysol|clorox|toothpaste|deodorant"),
    ("Frozen",    r"ice cream|frozen|pizza|bagel bite|hot pocket|totino|digiorno|stouffer|lean cuisine"),
    ("Bakery",    r"bread|bagel|muffin|roll|bun|tortilla|wrap|pita|croissant|english muffin"),
    ("Dairy",     r"yogurt|cheese|butter|cream cheese|sour cream|cottage cheese|milk|egg"),
    ("Pantry",    r"sauce|ketchup|mustard|mayo|dressing|salsa|soup|broth|pasta|rice|bean|canned"),
    ("Meat",      r"chicken|beef|pork|turkey|bacon|sausage|hot dog|deli|meat|fish|shrimp|salmon"),
    ("Spreads",   r"peanut butter|jam|jelly|honey|syrup|spread|nutella"),
]


def guess_category(text: str) -> str:
    t = text.lower()
    for category, pattern in _CATEGORY_RULES:
        if re.search(pattern, t):
            return category
    return "Other"


# ---------------------------------------------------------------------------
# Main parser
# ---------------------------------------------------------------------------

def parse_text(text: str) -> dict:
    """Extract shrinkflation signals from freeform text.

    Returns dict with keys:
        brand, product_hint, old_size, new_size, old_unit, new_unit,
        old_price, new_price, fields_found, explicit_from_to
    """
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

    # Brand detection
    for brand in KNOWN_BRANDS:
        if brand in text_lower:
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

        if old_val > new_val:
            result["old_size"] = old_val
            result["new_size"] = new_val
            result["old_unit"] = old_unit
            result["new_unit"] = new_unit
            result["explicit_from_to"] = True
            result["fields_found"] += 2
        elif new_val > old_val:
            result["old_size"] = new_val
            result["new_size"] = old_val
            result["old_unit"] = new_unit
            result["new_unit"] = old_unit
            result["explicit_from_to"] = True
            result["fields_found"] += 2

    if not result["explicit_from_to"]:
        units = UNIT_PATTERN.findall(text)
        if len(units) >= 2:
            old_val = float(units[0][0])
            old_unit = normalize_unit(units[0][1])
            new_val = float(units[-1][0])
            new_unit = normalize_unit(units[-1][1])
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

    # Product hint (cleaned title)
    first_line = text.strip().split("\n")[0][:120]
    cleaned = re.sub(r"^\[?META\]?\s*", "", first_line, flags=re.IGNORECASE)
    cleaned = re.sub(r"^\[?Discussion\]?\s*", "", cleaned, flags=re.IGNORECASE)
    result["product_hint"] = cleaned.strip()

    return result


def confidence_tier(parsed: dict) -> str:
    """Assign auto / review / discard based on extracted signal strength."""
    f = parsed["fields_found"]
    if f >= TIER_AUTO_THRESHOLD and parsed["brand"] and parsed["explicit_from_to"]:
        return "auto"
    if f >= TIER_REVIEW_THRESHOLD:
        return "review"
    return "discard"


def has_shrink_keywords(text: str) -> bool:
    """Check if text contains shrinkflation-related keywords."""
    return bool(SHRINK_KEYWORDS.search(text))
