"""
Shared configuration for FullCarts backend.
All secrets come from environment variables — never hardcode.
"""
import os

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ntyhbapphnzlariakgrw.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")  # service_role key

# Anthropic API (for vision analysis of product images)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Reddit API (optional — only for PRAW scraper)
REDDIT_CLIENT_ID     = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT    = os.getenv("REDDIT_USER_AGENT", "FullCartsBot/1.0 (fullcarts.org)")

# Scraper settings
TARGET_SUBREDDITS = [
    "shrinkflation", "Frugal", "personalfinance", "grocery",
    "mildlyinfuriating", "EatCheapAndHealthy", "Costco", "traderjoes",
]
PRIMARY_SUBREDDIT = "shrinkflation"

# Confidence thresholds
TIER_AUTO_THRESHOLD   = 3  # fields_found >= 3 + brand + explicit → auto
TIER_REVIEW_THRESHOLD = 1  # fields_found >= 1 → review

# Rate limiting
REDDIT_PUBLIC_DELAY = 2.0   # seconds between Reddit JSON requests
PULLPUSH_DELAY      = 1.5   # seconds between Pullpush requests
