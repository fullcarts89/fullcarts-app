"""Tests for Claude response parsing and image URL extraction."""
import pytest

from pipeline.lib.claude_client import _parse_json_response, _extract_text
from pipeline.scripts.extract_claims_vision import _extract_image_url


# ── JSON Response Parsing ────────────────────────────────────────────────────


class TestParseJsonResponse:
    def test_plain_json(self):
        result = _parse_json_response('{"brand": "Test", "score": 0.5}')
        assert result["brand"] == "Test"
        assert result["score"] == 0.5

    def test_json_with_code_block(self):
        text = '```json\n{"brand": "Test"}\n```'
        result = _parse_json_response(text)
        assert result["brand"] == "Test"

    def test_json_with_plain_code_block(self):
        text = '```\n{"brand": "Test"}\n```'
        result = _parse_json_response(text)
        assert result["brand"] == "Test"

    def test_json_with_whitespace(self):
        text = '\n  {"brand": "Test"}  \n'
        result = _parse_json_response(text)
        assert result["brand"] == "Test"

    def test_invalid_json(self):
        result = _parse_json_response("This is not JSON at all")
        assert result is None

    def test_empty_string(self):
        result = _parse_json_response("")
        assert result is None

    def test_nested_json(self):
        text = '{"confidence": {"brand": 0.9, "overall": 0.8}}'
        result = _parse_json_response(text)
        assert result["confidence"]["brand"] == 0.9


# ── Text Extraction from API Response ────────────────────────────────────────


class TestExtractText:
    def test_normal_response(self):
        data = {
            "content": [
                {"type": "text", "text": '{"brand": "Test"}'}
            ]
        }
        assert _extract_text(data) == '{"brand": "Test"}'

    def test_no_text_content(self):
        data = {"content": [{"type": "image", "data": "..."}]}
        assert _extract_text(data) is None

    def test_empty_content(self):
        data = {"content": []}
        assert _extract_text(data) is None

    def test_missing_content(self):
        data = {}
        assert _extract_text(data) is None


# ── Image URL Extraction ─────────────────────────────────────────────────────


class TestExtractImageUrl:
    def test_iredd_url(self):
        payload = {"url": "https://i.redd.it/abc123.jpg"}
        assert _extract_image_url(payload) == "https://i.redd.it/abc123.jpg"

    def test_imgur_url(self):
        payload = {"url": "https://i.imgur.com/xyz789.png"}
        assert _extract_image_url(payload) == "https://i.imgur.com/xyz789.png"

    def test_non_image_url(self):
        payload = {"url": "https://www.reddit.com/r/shrinkflation/comments/abc"}
        assert _extract_image_url(payload) is None

    def test_preview_images(self):
        payload = {
            "url": "https://example.com",
            "preview": {
                "images": [{
                    "source": {
                        "url": "https://preview.redd.it/abc.jpg?width=1024&amp;auto=webp"
                    }
                }]
            }
        }
        result = _extract_image_url(payload)
        assert result is not None
        assert "preview.redd.it" in result
        assert "&amp;" not in result  # Should be unescaped

    def test_gallery_metadata(self):
        payload = {
            "url": "https://example.com",
            "media_metadata": {
                "img1": {
                    "s": {
                        "u": "https://preview.redd.it/img1.jpg?width=640&amp;format=png"
                    }
                }
            }
        }
        result = _extract_image_url(payload)
        assert result is not None
        assert "&amp;" not in result

    def test_no_image_at_all(self):
        payload = {"title": "Text only post", "selftext": "No images here"}
        assert _extract_image_url(payload) is None

    def test_empty_payload(self):
        assert _extract_image_url({}) is None

    def test_thumbnail_fallback(self):
        payload = {
            "url": "https://example.com/article",
            "thumbnail": "https://b.thumbs.redditmedia.com/abc.jpg",
        }
        result = _extract_image_url(payload)
        assert result is not None
        assert "thumbs.redditmedia.com" in result

    def test_thumbnail_self(self):
        """'self' and 'default' thumbnails are not real images."""
        payload = {"url": "https://example.com", "thumbnail": "self"}
        assert _extract_image_url(payload) is None

    def test_webp_url(self):
        payload = {"url": "https://i.redd.it/photo.webp"}
        assert _extract_image_url(payload) == "https://i.redd.it/photo.webp"
