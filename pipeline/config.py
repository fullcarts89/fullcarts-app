"""
Shared configuration for the FullCarts ingestion pipeline.
All secrets come from environment variables — never hardcode.
"""
import os

# ── Supabase ──────────────────────────────────────────────────────────────────
SUPABASE_URL = os.getenv(
    "SUPABASE_URL", "https://ntyhbapphnzlariakgrw.supabase.co"
)
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")  # service_role key

# ── Kroger API ────────────────────────────────────────────────────────────────
KROGER_CLIENT_ID = os.getenv("KROGER_CLIENT_ID", "")
KROGER_CLIENT_SECRET = os.getenv("KROGER_CLIENT_SECRET", "")
KROGER_TOKEN_URL = "https://api.kroger.com/v1/connect/oauth2/token"
KROGER_API_BASE = "https://api.kroger.com/v1"
# Comma-separated store location IDs for price checks
KROGER_STORE_IDS = os.getenv("KROGER_STORE_IDS", "01400376,01400943").split(",")
KROGER_SEARCH_TERMS = [
    "potato chips", "breakfast cereal", "cookies", "crackers",
    "yogurt", "ice cream", "juice", "soda", "frozen meals",
    "canned soup", "pasta sauce", "candy bars", "granola bars", "bread",
]
KROGER_BRANDS = [
    "Frito-Lay", "General Mills", "Kellogg's", "Mondelez",
    "PepsiCo", "Unilever", "Nestle", "Conagra", "Kraft Heinz", "Mars",
]
KROGER_DISCOVERY_MAX_REQUESTS = int(
    os.getenv("KROGER_DISCOVERY_MAX_REQUESTS", "5000")
)

# ── Scraper identity ──────────────────────────────────────────────────────────
SCRAPER_VERSION = "pipeline-v1.0"
USER_AGENT = "FullCartsBot/2.0 (https://fullcarts.org; data pipeline)"

# ── Reddit ────────────────────────────────────────────────────────────────────
TARGET_SUBREDDIT = "shrinkflation"
REDDIT_JSON_DELAY = 1.5        # seconds between Reddit JSON API requests
ARCTIC_SHIFT_DELAY = 0.3       # seconds between Arctic Shift requests
ARCTIC_SHIFT_BASE = "https://arctic-shift.photon-reddit.com/api"

# ── News ──────────────────────────────────────────────────────────────────────
NEWS_QUERIES = [
    "shrinkflation",
    "shrinkflation grocery",
    "product downsizing",
    "package size reduction food",
]
NEWS_RSS_DELAY = 1.0           # seconds between RSS feed fetches

# ── GDELT ─────────────────────────────────────────────────────────────────────
GDELT_DOC_API = "https://api.gdeltproject.org/api/v2/doc/doc"
GDELT_QUERIES = [
    "shrinkflation",
    "package size reduction",
    "product downsizing",
]
GDELT_MAX_RECORDS = 250
GDELT_DELAY = 1.0             # seconds between GDELT queries

# ── Open Food Facts ───────────────────────────────────────────────────────────
OFF_API_BASE = "https://world.openfoodfacts.org/api/v2"
OFF_SEARCH_URL = "https://world.openfoodfacts.org/cgi/search.pl"
OFF_DELAY = 0.6                # 100 req/min limit → 0.6s between requests
OFF_CATEGORIES = [
    "snacks", "cereals", "beverages", "dairy", "frozen-foods",
    "candy", "confections", "chips", "cookies", "crackers",
    "yogurt", "ice-cream", "juice", "soft-drinks", "canned-goods",
    "pasta", "condiments",
]

# ── USDA ──────────────────────────────────────────────────────────────────────
USDA_FDC_BASE = "https://fdc.nal.usda.gov/fdc-datasets"
# Only releases with package_weight data (column first populated in Oct 2022).
# Earlier releases (2019-04 through 2022-04) lack package_weight entirely.
USDA_RELEASES = [
    ("2022-10-28", "FoodData_Central_branded_food_csv_2022-10-28.zip"),
    ("2023-04-20", "FoodData_Central_branded_food_csv_2023-04-20.zip"),
    ("2023-10-26", "FoodData_Central_branded_food_csv_2023-10-26.zip"),
    ("2024-04-18", "FoodData_Central_branded_food_csv_2024-04-18.zip"),
    ("2024-10-31", "FoodData_Central_branded_food_csv_2024-10-31.zip"),
    ("2025-04-24", "FoodData_Central_branded_food_csv_2025-04-24.zip"),
    ("2025-12-18", "FoodData_Central_branded_food_csv_2025-12-18.zip"),
]

# ── Open Prices ───────────────────────────────────────────────────────────────
OPEN_PRICES_API_BASE = "https://prices.openfoodfacts.org/api/v1"
OPEN_PRICES_DELAY = 1.0        # seconds between requests (be respectful)
OPEN_PRICES_PAGE_SIZE = 100    # items per page (API max)

# ── FRED (Federal Reserve Economic Data) ─────────────────────────────────────
# FRED API key is optional — the public CSV endpoint works without one.
# Register at: https://fred.stlouisfed.org/docs/api/api_key.html
FRED_API_KEY = os.getenv("FRED_API_KEY", "")
FRED_API_BASE = "https://api.stlouisfed.org/fred"
FRED_CSV_BASE = "https://fred.stlouisfed.org/graph/fredgraph.csv"
FRED_DELAY = 0.6  # seconds between requests (~100 req/min, well under 120 limit)

# (series_id, human_readable_name, category_slug)
FRED_SERIES = [
    ("CPIAUCNS",       "CPI: All Items (Urban Consumers)",       "all_items"),
    ("CPIUFDNS",       "CPI: Food at Home",                      "food_at_home"),
    ("CPIFABNS",       "CPI: Cereals and Bakery Products",       "cereals_bakery"),
    ("CUSR0000SAF112", "CPI: Meats, Poultry, Fish, and Eggs",    "meats_poultry"),
    ("CUSR0000SAF113", "CPI: Dairy and Related Products",        "dairy"),
    ("CUSR0000SAF114", "CPI: Fruits and Vegetables",             "fruits_vegetables"),
    ("CUSR0000SAF115", "CPI: Nonalcoholic Beverages",            "nonalcoholic_beverages"),
    ("CUSR0000SAF116", "CPI: Other Food at Home",                "other_food_at_home"),
    ("CUSR0000SEFV",   "CPI: Food Away from Home",               "food_away_from_home"),
]

# ── UPC / Barcode Resolution ──────────────────────────────────────────────────
# UPCitemdb free trial tier: 100 lookups/day, 6 requests/minute
UPCITEMDB_TRIAL_URL = "https://api.upcitemdb.com/prod/trial/lookup"
UPCITEMDB_DAILY_LIMIT = 100

# Brocade.io: free barcode lookup API, no authentication required
BROCADE_API_URL = "https://brocade.io/api/items"

# Seconds between UPCitemdb requests (free tier limit: 6/min → 10s gap)
UPC_RESOLUTION_DELAY = 10

# ── Rate limiting defaults ────────────────────────────────────────────────────
DEFAULT_MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30           # seconds

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
