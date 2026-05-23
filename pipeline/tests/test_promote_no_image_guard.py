"""No-image guard in promote_claims.

The guard blocks NEW published_changes creation when the originating claim
is a reddit post that lacks a stored image. Reddit is anonymous anecdote;
without a photograph we have no corroborating evidence to publish on.

Non-reddit sources (news, gdelt, kroger_change, usda_size_change, etc.)
are allowed even without an image because they carry third-party catalog
or journalism evidence on their own.

Fold-ins to existing events are exempt entirely from the guard — the
event already has its own image corroboration from prior sources.
"""
import pytest

from pipeline.scripts.promote_claims import should_block_new_event_no_image


REDDIT_RAW = "11111111-1111-1111-1111-111111111111"
NEWS_RAW   = "22222222-2222-2222-2222-222222222222"
GDELT_RAW  = "33333333-3333-3333-3333-333333333333"
KROGER_RAW = "44444444-4444-4444-4444-444444444444"
USDA_RAW   = "55555555-5555-5555-5555-555555555555"

SOURCE_MAP = {
    REDDIT_RAW: "reddit",
    NEWS_RAW:   "news",
    GDELT_RAW:  "gdelt",
    KROGER_RAW: "kroger_change",
    USDA_RAW:   "usda_size_change",
}


class TestRedditWithoutImageIsBlocked:
    def test_reddit_no_image_blocked(self):
        claim = {"raw_item_id": REDDIT_RAW, "image_storage_path": None}
        assert should_block_new_event_no_image(claim, SOURCE_MAP, {}) is True

    def test_reddit_with_archived_image_allowed(self):
        claim = {
            "raw_item_id": REDDIT_RAW,
            "image_storage_path": "abc.webp",
        }
        assert should_block_new_event_no_image(claim, SOURCE_MAP, {}) is False

    def test_reddit_with_socialimage_allowed(self):
        # Edge case: a Reddit raw_item that somehow gained a socialimage
        # (e.g. via the rescue script). Treat as having evidence.
        claim = {"raw_item_id": REDDIT_RAW, "image_storage_path": None}
        socialimg = {REDDIT_RAW: True}
        assert should_block_new_event_no_image(claim, SOURCE_MAP, socialimg) is False

    def test_reddit_empty_string_storage_path_blocked(self):
        claim = {"raw_item_id": REDDIT_RAW, "image_storage_path": ""}
        assert should_block_new_event_no_image(claim, SOURCE_MAP, {}) is True


class TestNonRedditSourcesAlwaysAllowed:
    """The guard scopes to reddit. News, gdelt, kroger_change, and
    usda_size_change all carry third-party evidence and are exempt."""

    @pytest.mark.parametrize("raw_id", [NEWS_RAW, GDELT_RAW, KROGER_RAW, USDA_RAW])
    def test_no_image_still_allowed(self, raw_id):
        claim = {"raw_item_id": raw_id, "image_storage_path": None}
        assert should_block_new_event_no_image(claim, SOURCE_MAP, {}) is False

    @pytest.mark.parametrize("raw_id", [NEWS_RAW, GDELT_RAW])
    def test_socialimage_still_allowed(self, raw_id):
        claim = {"raw_item_id": raw_id, "image_storage_path": None}
        socialimg = {raw_id: True}
        assert should_block_new_event_no_image(claim, SOURCE_MAP, socialimg) is False


class TestUnknownSource:
    """If we can't identify the source_type from the preload map, the guard
    must not fire (conservative — we never want to block on a lookup miss
    because that would let the rule silently expand to unexpected sources)."""

    def test_missing_raw_id_does_not_block(self):
        claim = {"image_storage_path": None}
        assert should_block_new_event_no_image(claim, {}, {}) is False

    def test_unknown_source_type_does_not_block(self):
        # A raw_item_id present in the claim but absent from source_map
        # (e.g., a brand-new source_type the preload didn't catch).
        claim = {"raw_item_id": "deadbeef-...", "image_storage_path": None}
        assert should_block_new_event_no_image(claim, {}, {}) is False
