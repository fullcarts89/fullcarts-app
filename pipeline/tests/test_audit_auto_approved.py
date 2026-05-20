"""Audit script's filter must match the historic auto_approve_claims.py
filter byte-for-byte. The reconstruction is the whole point of the audit;
if the predicate drifts, the cohort is wrong.
"""
from pipeline.scripts.audit_auto_approved import _passes_hard_filters


def _claim(**overrides):
    """Sensible defaults that pass every filter; tests override one
    field at a time."""
    base = {
        "image_storage_path": "claim-images/abc.jpg",
        "old_size_unit": "g",
        "confidence": {
            "overall": 95,
            "brand": 0.95,
            "size_change": 0.95,
            "product_name": 0.95,
        },
    }
    base.update(overrides)
    return base


class TestHardFilters:
    def test_accepts_canonical_claim(self):
        assert _passes_hard_filters(_claim()) is None

    def test_rejects_no_image(self):
        c = _claim(image_storage_path=None)
        assert _passes_hard_filters(c) == "no image"

    def test_rejects_empty_image_path(self):
        c = _claim(image_storage_path="")
        assert _passes_hard_filters(c) == "no image"

    def test_rejects_non_cpg_unit(self):
        c = _claim(old_size_unit="in")  # pizza diameter, e.g. Little Caesars
        reason = _passes_hard_filters(c)
        assert reason is not None
        assert "CPG allowlist" in reason

    def test_unit_check_is_case_insensitive(self):
        c = _claim(old_size_unit="G")  # uppercase
        assert _passes_hard_filters(c) is None

    def test_unit_check_tolerates_whitespace(self):
        c = _claim(old_size_unit="  oz  ")
        assert _passes_hard_filters(c) is None

    def test_accepts_fl_oz(self):
        # "fl oz" has a space and was a real allowlist member.
        c = _claim(old_size_unit="fl oz")
        assert _passes_hard_filters(c) is None

    def test_rejects_low_brand_score(self):
        c = _claim(confidence={"overall": 95, "brand": 0.7, "size_change": 0.9, "product_name": 0.9})
        reason = _passes_hard_filters(c)
        assert reason is not None
        assert "brand" in reason

    def test_rejects_low_size_change_score(self):
        c = _claim(confidence={"overall": 95, "brand": 0.9, "size_change": 0.7, "product_name": 0.9})
        reason = _passes_hard_filters(c)
        assert reason is not None
        assert "size_change" in reason

    def test_rejects_low_product_name_score(self):
        # Product name floor is 0.80, so 0.75 fails.
        c = _claim(confidence={"overall": 95, "brand": 0.9, "size_change": 0.9, "product_name": 0.75})
        reason = _passes_hard_filters(c)
        assert reason is not None
        assert "product_name" in reason

    def test_rejects_missing_sub_scores(self):
        c = _claim(confidence={})
        reason = _passes_hard_filters(c)
        assert reason is not None
        assert "brand" in reason

    def test_rejects_confidence_not_a_dict(self):
        c = _claim(confidence="invalid")
        reason = _passes_hard_filters(c)
        assert reason == "missing sub-scores"

    def test_boundary_brand_score_exact_floor(self):
        # 0.85 exactly should pass (the original used >=, not >).
        c = _claim(confidence={"overall": 95, "brand": 0.85, "size_change": 0.85, "product_name": 0.80})
        assert _passes_hard_filters(c) is None

    def test_boundary_product_name_just_below_floor(self):
        # product_name floor is 0.80 (lower than the other two).
        c = _claim(confidence={"overall": 95, "brand": 0.85, "size_change": 0.85, "product_name": 0.79})
        reason = _passes_hard_filters(c)
        assert reason is not None
        assert "product_name" in reason
