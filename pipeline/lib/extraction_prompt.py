"""Prompt templates for claim extraction from Reddit posts and news articles.

Each function returns a (system_prompt, user_message) tuple ready to send
to Claude Haiku via claude_client.
"""

# ── System Prompt ────────────────────────────────────────────────────────────

SYSTEM_PROMPT_TEXT = """You are a structured data extractor for a shrinkflation tracking platform.

Your job: Read a social media post or news article and extract any shrinkflation claim — a report that a product's size or quantity decreased while the price stayed the same or increased.

Return ONLY valid JSON (no markdown, no explanation) with this exact schema:

{
  "brand": string or null,
  "product_name": string or null,
  "category": string or null,
  "old_size": number or null,
  "old_size_unit": string or null,
  "new_size": number or null,
  "new_size_unit": string or null,
  "old_price": number or null,
  "new_price": number or null,
  "retailer": string or null,
  "upc": string or null,
  "observed_date": string or null,
  "change_description": string,
  "is_shrinkflation": boolean,
  "confidence": {
    "brand": number,
    "product_name": number,
    "size_change": number,
    "overall": number
  }
}

Rules:
- All confidence scores are 0.0 to 1.0
- Sizes must be numeric. Convert "fifteen ounces" to 15, "oz" to "oz", "grams" to "g", "count" to "ct", "fluid ounces" to "fl oz"
- Normalize units: oz, g, ml, fl oz, ct, lb, kg, L
- "observed_date" should be ISO format (YYYY-MM-DD) if mentioned, otherwise null
- If the post mentions a specific store (Walmart, Kroger, etc.), set "retailer"
- If a barcode/UPC number is visible or mentioned, set "upc"
- "change_description" should be a one-sentence summary of what changed
- "is_shrinkflation" is true only if: size/quantity decreased AND price stayed same or went up
- For posts that are NOT about a specific product change (memes, jokes, general complaints, discussions, questions), set:
  - "is_shrinkflation": false
  - "change_description": "not_a_product_report"
  - "confidence": {"brand": 0, "product_name": 0, "size_change": 0, "overall": 0}
- For posts about skimpflation (ingredient quality reduced, not size), set:
  - "is_shrinkflation": false
  - "change_description" should describe the quality change
  - confidence.overall should reflect how clear the claim is
- For stretchflation (same size package but less product inside, more air/filler), set:
  - "is_shrinkflation": true
  - "change_description" should mention "stretchflation" and describe the issue
  - confidence.overall should reflect how clear the evidence is
- For catalog entries (OFF, Kroger, Open Prices) where no change is being reported:
  - "is_shrinkflation": false
  - Extract all available product data (brand, name, size, price, UPC)
  - confidence.overall based on data completeness
- category should be one of: chips, cereal, cookies, crackers, yogurt, ice_cream, candy, beverages, frozen_meals, canned_goods, bread, pasta, condiments, snacks, dairy, produce, meat, other"""

SYSTEM_PROMPT_VISION = """You are a structured data extractor for a shrinkflation tracking platform.

Your job: Look at a product image (and any accompanying text) to extract shrinkflation evidence — specifically, information about a product's size, weight, or quantity that may have changed.

Return ONLY valid JSON (no markdown, no explanation) with this exact schema:

{
  "brand": string or null,
  "product_name": string or null,
  "category": string or null,
  "old_size": number or null,
  "old_size_unit": string or null,
  "new_size": number or null,
  "new_size_unit": string or null,
  "old_price": number or null,
  "new_price": number or null,
  "retailer": string or null,
  "upc": string or null,
  "observed_date": string or null,
  "change_description": string,
  "is_shrinkflation": boolean,
  "confidence": {
    "brand": number,
    "product_name": number,
    "size_change": number,
    "overall": number
  }
}

Rules:
- Look for size/weight/quantity information on packaging labels
- If comparing two packages (before/after), extract both sizes
- If only one package is shown, extract what you can see (new_size) and leave old_size null
- Read any visible UPC barcodes or price labels
- All confidence scores are 0.0 to 1.0
- Sizes must be numeric with normalized units: oz, g, ml, fl oz, ct, lb, kg, L
- "change_description" should describe what the image shows
- If the image is not related to a product (meme, screenshot, chart, etc.):
  - "is_shrinkflation": false
  - "change_description": "not_a_product_image"
  - "confidence": {"brand": 0, "product_name": 0, "size_change": 0, "overall": 0}
- category should be one of: chips, cereal, cookies, crackers, yogurt, ice_cream, candy, beverages, frozen_meals, canned_goods, bread, pasta, condiments, snacks, dairy, produce, meat, other"""


def build_reddit_text_message(title, selftext, score, created_utc):
    # type: (str, str, int, float) -> str
    """Build a user message for text-based Reddit post extraction.

    Args:
        title: Reddit post title.
        selftext: Reddit post body text.
        score: Reddit upvote score (proxy for community agreement).
        created_utc: Unix timestamp of the post.

    Returns:
        Formatted user message string.
    """
    from datetime import datetime, timezone

    post_date = ""
    if created_utc:
        try:
            dt = datetime.fromtimestamp(float(created_utc), tz=timezone.utc)
            post_date = dt.strftime("%Y-%m-%d")
        except (ValueError, OSError):
            pass

    parts = []
    parts.append("Subreddit: r/shrinkflation")
    if post_date:
        parts.append("Post date: %s" % post_date)
    parts.append("Score: %d" % (score or 0))
    parts.append("")
    parts.append("Title: %s" % (title or "").strip())

    body = (selftext or "").strip()
    if body:
        # Truncate very long posts to save tokens
        if len(body) > 2000:
            body = body[:2000] + "... [truncated]"
        parts.append("")
        parts.append("Body: %s" % body)

    return "\n".join(parts)


def build_reddit_vision_message(title, selftext, score, created_utc):
    # type: (str, str, int, float) -> str
    """Build the text portion of a vision extraction message.

    The image will be added separately by the caller.
    """
    from datetime import datetime, timezone

    post_date = ""
    if created_utc:
        try:
            dt = datetime.fromtimestamp(float(created_utc), tz=timezone.utc)
            post_date = dt.strftime("%Y-%m-%d")
        except (ValueError, OSError):
            pass

    parts = []
    parts.append("Subreddit: r/shrinkflation")
    if post_date:
        parts.append("Post date: %s" % post_date)
    parts.append("Score: %d" % (score or 0))
    parts.append("")
    parts.append("Title: %s" % (title or "").strip())

    body = (selftext or "").strip()
    if body:
        if len(body) > 1000:
            body = body[:1000] + "... [truncated]"
        parts.append("")
        parts.append("Body: %s" % body)

    parts.append("")
    parts.append("The image above was posted with this text. Extract any shrinkflation evidence from both the image and text.")

    return "\n".join(parts)


def build_news_text_message(title, description, published, body=None, source_name=None):
    # type: (str, str, str, Optional[str], Optional[str]) -> str
    """Build a user message for news article extraction.

    Args:
        title: Article headline.
        description: Article summary/snippet.
        published: Publication date string.
        body: Full article body text (if fetched).
        source_name: Name of the news source.

    Returns:
        Formatted user message string.
    """
    parts = []
    source_label = "News article"
    if source_name:
        source_label = "News article from %s" % source_name
    parts.append("Source: %s" % source_label)
    if published:
        parts.append("Published: %s" % published)
    parts.append("")
    parts.append("Headline: %s" % (title or "").strip())

    # Prefer full body text over short description
    body_text = (body or "").strip()
    if body_text:
        if len(body_text) > 4000:
            body_text = body_text[:4000] + "... [truncated]"
        parts.append("")
        parts.append("Article body:\n%s" % body_text)
    else:
        desc = (description or "").strip()
        if desc:
            if len(desc) > 2000:
                desc = desc[:2000] + "... [truncated]"
            parts.append("")
            parts.append("Article excerpt: %s" % desc)

    parts.append("")
    parts.append(
        "IMPORTANT: If this article mentions MULTIPLE specific products that "
        "have been shrinkflated, return a JSON array of claim objects (one per "
        "product). If only one product is mentioned, return a single JSON "
        "object as usual."
    )

    return "\n".join(parts)


def build_usda_size_change_message(payload):
    # type: (dict) -> str
    """Build a user message for a USDA-detected size change.

    The USDA variance analyzer already computed the before/after sizes.
    This just formats the data for Claude to validate and enrich.
    """
    parts = []
    parts.append("Source: USDA FoodData Central (government data)")
    parts.append("Data type: Package weight change detected across quarterly releases")
    parts.append("")

    brand = payload.get("brand_owner", payload.get("brand", ""))
    name = payload.get("description", payload.get("product_name", ""))
    gtin = payload.get("gtin_upc", payload.get("upc", ""))
    old_weight = payload.get("old_package_weight", payload.get("weight_before", ""))
    new_weight = payload.get("new_package_weight", payload.get("weight_after", ""))
    old_date = payload.get("old_release_date", payload.get("date_before", ""))
    new_date = payload.get("new_release_date", payload.get("date_after", ""))
    category = payload.get("branded_food_category", payload.get("category", ""))

    if brand:
        parts.append("Brand: %s" % brand)
    if name:
        parts.append("Product: %s" % name)
    if gtin:
        parts.append("UPC/GTIN: %s" % gtin)
    if category:
        parts.append("Category: %s" % category)
    parts.append("")
    if old_weight and new_weight:
        parts.append("Previous package weight: %s" % old_weight)
        parts.append("Current package weight: %s" % new_weight)
    if old_date and new_date:
        parts.append("Previous release: %s" % old_date)
        parts.append("Current release: %s" % new_date)

    parts.append("")
    parts.append(
        "This is GOVERNMENT DATA from the USDA. Extract the brand, product name, "
        "old and new sizes (as numbers with units), and classify the change. "
        "Confidence should be HIGH since this is official government data."
    )

    return "\n".join(parts)


def build_openfoodfacts_message(payload):
    # type: (dict) -> str
    """Build a user message for an Open Food Facts product record.

    OFF products are catalog entries, not change reports. The extractor
    should record the current product data for future comparison.
    """
    parts = []
    parts.append("Source: Open Food Facts (crowdsourced product database)")
    parts.append("Data type: Product catalog entry")
    parts.append("")

    code = payload.get("code", "")
    name = payload.get("product_name", "")
    brands = payload.get("brands", "")
    quantity = payload.get("quantity", payload.get("product_quantity", ""))
    quantity_unit = payload.get("product_quantity_unit", "")
    categories = payload.get("categories", "")

    if brands:
        parts.append("Brand: %s" % brands)
    if name:
        parts.append("Product: %s" % name)
    if code:
        parts.append("Barcode: %s" % code)
    if quantity:
        parts.append("Package size: %s %s" % (quantity, quantity_unit or ""))
    if categories:
        parts.append("Categories: %s" % str(categories)[:200])

    parts.append("")
    parts.append(
        "This is a product catalog entry. Extract the brand, product name, "
        "current size, and category. Set new_size to the current package size. "
        "Leave old_size null (this is a single observation, not a change report). "
        "Set is_shrinkflation to false. Set confidence based on data completeness."
    )

    return "\n".join(parts)


def build_kroger_message(payload):
    # type: (dict) -> str
    """Build a user message for a Kroger API product record."""
    parts = []
    parts.append("Source: Kroger Product API (grocery retailer)")
    parts.append("Data type: Current product listing")
    parts.append("")

    desc = payload.get("description", "")
    brand = payload.get("brand", "")
    upc = payload.get("upc", payload.get("productId", ""))
    size = payload.get("size", payload.get("itemInformation", {}).get("size", ""))
    price = None
    items = payload.get("items", [])
    if items and isinstance(items, list):
        price_info = items[0].get("price", {})
        price = price_info.get("regular", price_info.get("promo"))
    categories = payload.get("categories", [])

    if brand:
        parts.append("Brand: %s" % brand)
    if desc:
        parts.append("Product: %s" % desc)
    if upc:
        parts.append("UPC: %s" % upc)
    if size:
        parts.append("Size: %s" % size)
    if price:
        parts.append("Price: $%.2f" % float(price))
    if categories:
        parts.append("Categories: %s" % str(categories)[:200])

    parts.append("")
    parts.append(
        "This is a grocery product listing from Kroger. Extract the brand, "
        "product name, current size, price, and category. Set new_size to "
        "the current size. Leave old_size null. Set retailer to 'Kroger'. "
        "Set is_shrinkflation to false. Set confidence based on data completeness."
    )

    return "\n".join(parts)


def build_open_prices_message(payload):
    # type: (dict) -> str
    """Build a user message for an Open Prices receipt record."""
    parts = []
    parts.append("Source: Open Prices (crowdsourced receipt data)")
    parts.append("Data type: Receipt-level price observation")
    parts.append("")

    code = payload.get("product_code", payload.get("barcode", ""))
    product = payload.get("product", {})
    name = ""
    brand = ""
    if isinstance(product, dict):
        name = product.get("product_name", "")
        brand = product.get("brands", "")

    price = payload.get("price", "")
    currency = payload.get("currency", "")
    price_date = payload.get("date", payload.get("created", ""))
    location = payload.get("location", {})
    store = ""
    if isinstance(location, dict):
        store = location.get("osm_name", location.get("name", ""))

    if brand:
        parts.append("Brand: %s" % brand)
    if name:
        parts.append("Product: %s" % name)
    if code:
        parts.append("Barcode: %s" % code)
    if price:
        parts.append("Price: %s %s" % (price, currency))
    if price_date:
        parts.append("Date: %s" % str(price_date)[:10])
    if store:
        parts.append("Store: %s" % store)

    parts.append("")
    parts.append(
        "This is a receipt-level price observation. Extract the brand, product "
        "name, price, barcode, and store. Set new_price to the observed price. "
        "Leave size fields null unless the product name contains size info. "
        "Set is_shrinkflation to false. Set confidence based on data completeness."
    )

    return "\n".join(parts)


def parse_claim_response(response):
    # type: (dict) -> dict
    """Validate and normalize a parsed claim response from Claude.

    Ensures all expected fields exist with correct types.
    Returns a cleaned dict ready for insertion into the claims table.
    """
    if not isinstance(response, dict):
        return _empty_claim()

    # Extract and validate confidence
    raw_conf = response.get("confidence", {})
    if not isinstance(raw_conf, dict):
        raw_conf = {}

    confidence = {
        "brand": _clamp_float(raw_conf.get("brand", 0)),
        "product_name": _clamp_float(raw_conf.get("product_name", 0)),
        "size_change": _clamp_float(raw_conf.get("size_change", 0)),
        "overall": _clamp_float(raw_conf.get("overall", 0)),
    }

    return {
        "brand": _safe_str(response.get("brand")),
        "product_name": _safe_str(response.get("product_name")),
        "category": _safe_str(response.get("category")),
        "old_size": _safe_numeric(response.get("old_size")),
        "old_size_unit": _safe_str(response.get("old_size_unit")),
        "new_size": _safe_numeric(response.get("new_size")),
        "new_size_unit": _safe_str(response.get("new_size_unit")),
        "old_price": _safe_numeric(response.get("old_price")),
        "new_price": _safe_numeric(response.get("new_price")),
        "retailer": _safe_str(response.get("retailer")),
        "upc": _safe_str(response.get("upc")),
        "observed_date": _safe_date(response.get("observed_date")),
        "change_description": _safe_str(response.get("change_description"))
        or "extraction_failed",
        "is_shrinkflation": bool(response.get("is_shrinkflation", False)),
        "confidence": confidence,
    }


def _empty_claim():
    # type: () -> dict
    """Return a claim dict representing a failed extraction."""
    return {
        "brand": None,
        "product_name": None,
        "category": None,
        "old_size": None,
        "old_size_unit": None,
        "new_size": None,
        "new_size_unit": None,
        "old_price": None,
        "new_price": None,
        "retailer": None,
        "upc": None,
        "observed_date": None,
        "change_description": "extraction_failed",
        "is_shrinkflation": False,
        "confidence": {
            "brand": 0,
            "product_name": 0,
            "size_change": 0,
            "overall": 0,
        },
    }


def _clamp_float(value, min_val=0.0, max_val=1.0):
    # type: (Any, float, float) -> float
    """Clamp a value to [min_val, max_val], returning 0 on invalid input."""
    try:
        f = float(value)
        return max(min_val, min(max_val, f))
    except (TypeError, ValueError):
        return 0.0


def _safe_str(value):
    # type: (Any) -> Optional[str]
    """Return a stripped string or None."""
    if value is None:
        return None
    s = str(value).strip()
    return s if s else None


def _safe_date(value):
    # type: (Any) -> Optional[str]
    """Return a valid YYYY-MM-DD date string, or None.

    Claude sometimes returns partial dates like '2024' or 'January 2024'.
    Only accept strings that parse as a full date.
    """
    import re
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    # Accept YYYY-MM-DD format only
    if re.match(r"^\d{4}-\d{2}-\d{2}$", s):
        return s
    # Try to parse YYYY-MM as YYYY-MM-01
    if re.match(r"^\d{4}-\d{2}$", s):
        return s + "-01"
    # Year-only or other formats → None
    return None


def _safe_numeric(value):
    # type: (Any) -> Optional[float]
    """Return a float or None."""
    if value is None:
        return None
    try:
        f = float(value)
        return f if f > 0 else None
    except (TypeError, ValueError):
        return None
