"""Tests for extraction prompt construction and claim response parsing."""
import pytest

from pipeline.lib.extraction_prompt import (
    build_news_text_message,
    build_reddit_text_message,
    build_reddit_vision_message,
    parse_claim_response,
)


# ── build_reddit_text_message ────────────────────────────────────────────────


class TestBuildRedditTextMessage:
    def test_basic_post(self):
        msg = build_reddit_text_message(
            title="Doritos went from 9.5oz to 9.25oz!",
            selftext="Bought a bag yesterday and noticed it's smaller.",
            score=150,
            created_utc=1700000000.0,
        )
        assert "r/shrinkflation" in msg
        assert "Doritos went from 9.5oz to 9.25oz!" in msg
        assert "Bought a bag yesterday" in msg
        assert "Score: 150" in msg
        assert "2023-11-14" in msg  # date from timestamp

    def test_empty_selftext(self):
        msg = build_reddit_text_message(
            title="Check out this shrinkage",
            selftext="",
            score=10,
            created_utc=1700000000.0,
        )
        assert "Check out this shrinkage" in msg
        assert "Body:" not in msg

    def test_none_selftext(self):
        msg = build_reddit_text_message(
            title="Title only",
            selftext=None,
            score=5,
            created_utc=0,
        )
        assert "Title only" in msg
        assert "Body:" not in msg

    def test_long_body_truncated(self):
        long_body = "x" * 3000
        msg = build_reddit_text_message(
            title="Long post",
            selftext=long_body,
            score=1,
            created_utc=1700000000.0,
        )
        assert "[truncated]" in msg
        # Body should be capped at ~2000 chars
        body_start = msg.index("Body: ")
        body_text = msg[body_start + 6:]
        assert len(body_text) < 2100

    def test_zero_score(self):
        msg = build_reddit_text_message(
            title="Post", selftext="", score=0, created_utc=0,
        )
        assert "Score: 0" in msg

    def test_none_score(self):
        msg = build_reddit_text_message(
            title="Post", selftext="", score=None, created_utc=0,
        )
        assert "Score: 0" in msg


# ── build_reddit_vision_message ──────────────────────────────────────────────


class TestBuildRedditVisionMessage:
    def test_includes_image_instruction(self):
        msg = build_reddit_vision_message(
            title="Look at this",
            selftext="",
            score=10,
            created_utc=1700000000.0,
        )
        assert "image above" in msg.lower()

    def test_truncates_body_shorter_for_vision(self):
        long_body = "y" * 2000
        msg = build_reddit_vision_message(
            title="Vision post",
            selftext=long_body,
            score=1,
            created_utc=1700000000.0,
        )
        assert "[truncated]" in msg


# ── build_news_text_message ──────────────────────────────────────────────────


class TestBuildNewsTextMessage:
    def test_basic_article(self):
        msg = build_news_text_message(
            title="Shrinkflation hits cereal aisle",
            description="Major brands reducing box sizes while prices rise.",
            published="2024-01-15",
        )
        assert "News article" in msg
        assert "Shrinkflation hits cereal aisle" in msg
        assert "Major brands" in msg
        assert "2024-01-15" in msg

    def test_empty_description(self):
        msg = build_news_text_message(
            title="Headline only",
            description="",
            published="",
        )
        assert "Headline only" in msg
        assert "Article excerpt:" not in msg


# ── parse_claim_response ─────────────────────────────────────────────────────


class TestParseClaimResponse:
    def test_valid_response(self):
        response = {
            "brand": "Doritos",
            "product_name": "Nacho Cheese Tortilla Chips",
            "category": "chips",
            "old_size": 9.5,
            "old_size_unit": "oz",
            "new_size": 9.25,
            "new_size_unit": "oz",
            "old_price": 4.29,
            "new_price": 4.49,
            "retailer": "Walmart",
            "upc": "028400064545",
            "observed_date": "2024-01-15",
            "change_description": "Doritos bag shrunk from 9.5oz to 9.25oz",
            "is_shrinkflation": True,
            "confidence": {
                "brand": 0.95,
                "product_name": 0.90,
                "size_change": 0.85,
                "overall": 0.88,
            },
        }
        result = parse_claim_response(response)
        assert result["brand"] == "Doritos"
        assert result["product_name"] == "Nacho Cheese Tortilla Chips"
        assert result["old_size"] == 9.5
        assert result["new_size"] == 9.25
        assert result["confidence"]["overall"] == 0.88
        assert result["is_shrinkflation"] is True

    def test_null_fields(self):
        response = {
            "brand": None,
            "product_name": None,
            "old_size": None,
            "change_description": "not_a_product_report",
            "is_shrinkflation": False,
            "confidence": {"brand": 0, "product_name": 0, "size_change": 0, "overall": 0},
        }
        result = parse_claim_response(response)
        assert result["brand"] is None
        assert result["product_name"] is None
        assert result["old_size"] is None
        assert result["confidence"]["overall"] == 0

    def test_missing_confidence(self):
        response = {"brand": "Test", "change_description": "test"}
        result = parse_claim_response(response)
        assert result["confidence"]["overall"] == 0
        assert result["confidence"]["brand"] == 0

    def test_confidence_clamped(self):
        response = {
            "brand": "Test",
            "change_description": "test",
            "confidence": {"brand": 1.5, "overall": -0.2},
        }
        result = parse_claim_response(response)
        assert result["confidence"]["brand"] == 1.0
        assert result["confidence"]["overall"] == 0.0

    def test_non_dict_input(self):
        result = parse_claim_response("not a dict")
        assert result["brand"] is None
        assert result["change_description"] == "extraction_failed"
        assert result["confidence"]["overall"] == 0

    def test_none_input(self):
        result = parse_claim_response(None)
        assert result["change_description"] == "extraction_failed"

    def test_empty_dict(self):
        result = parse_claim_response({})
        assert result["brand"] is None
        assert result["change_description"] == "extraction_failed"
        assert result["is_shrinkflation"] is False

    def test_string_numbers(self):
        """Claude sometimes returns numbers as strings."""
        response = {
            "brand": "Cheerios",
            "old_size": "15",
            "new_size": "13.5",
            "old_price": "4.99",
            "change_description": "Cheerios shrunk",
            "confidence": {"overall": "0.85"},
        }
        result = parse_claim_response(response)
        assert result["old_size"] == 15.0
        assert result["new_size"] == 13.5
        assert result["old_price"] == 4.99
        assert result["confidence"]["overall"] == 0.85

    def test_negative_size_ignored(self):
        response = {
            "old_size": -5,
            "new_size": 0,
            "change_description": "bad data",
            "confidence": {"overall": 0.5},
        }
        result = parse_claim_response(response)
        assert result["old_size"] is None
        assert result["new_size"] is None

    def test_whitespace_strings_become_none(self):
        response = {
            "brand": "  ",
            "product_name": "",
            "change_description": "test",
            "confidence": {"overall": 0.5},
        }
        result = parse_claim_response(response)
        assert result["brand"] is None
        assert result["product_name"] is None

    def test_non_dict_confidence(self):
        response = {
            "brand": "Test",
            "change_description": "test",
            "confidence": "high",
        }
        result = parse_claim_response(response)
        assert result["confidence"]["overall"] == 0


# ── parse_claim_response: JSON parsing edge cases ────────────────────────────


class TestParseJsonEdgeCases:
    """Test the _parse_json_response helper indirectly through integration."""

    def test_all_fields_populated(self):
        """Verify every field in the schema can be populated."""
        response = {
            "brand": "Brand X",
            "product_name": "Product Y",
            "category": "snacks",
            "old_size": 16,
            "old_size_unit": "oz",
            "new_size": 14,
            "new_size_unit": "oz",
            "old_price": 3.99,
            "new_price": 3.99,
            "retailer": "Target",
            "upc": "123456789012",
            "observed_date": "2024-06-15",
            "change_description": "Product Y shrunk 2oz",
            "is_shrinkflation": True,
            "confidence": {
                "brand": 0.99,
                "product_name": 0.95,
                "size_change": 0.90,
                "overall": 0.93,
            },
        }
        result = parse_claim_response(response)
        assert result["brand"] == "Brand X"
        assert result["category"] == "snacks"
        assert result["old_size_unit"] == "oz"
        assert result["new_size_unit"] == "oz"
        assert result["retailer"] == "Target"
        assert result["upc"] == "123456789012"
        assert result["observed_date"] == "2024-06-15"
