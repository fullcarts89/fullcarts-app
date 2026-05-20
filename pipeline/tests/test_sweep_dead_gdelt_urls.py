"""Tests for sweep_dead_gdelt_urls.

The script does three things worth locking with tests:

1. `classify_url(url)` is the URL-health verdict — pure (modulo `requests`),
   so we mock `requests.head` and assert the verdict for every status class
   the docstring promises to handle (404/410 = dead, ambiguous 4xx = dead,
   2xx/3xx = alive, 401/403/429 = alive-but-locked, timeout/conn-error = dead).

2. `find_pending_gdelt_claims(sb)` walks the claims table joined to
   raw_items. We assert it returns the [{claim_id, url}] shape and skips
   rows where the joined raw_item is missing or its source_url is null
   (which can happen if PostgREST's `!inner` semantics ever loosen).

3. The main loop's dry-run vs apply contract: dry-run must NOT call
   update() or raise_flag(); apply mode must call each exactly once per
   dead URL and zero times for alive URLs.
"""
from unittest.mock import MagicMock, patch

import pytest
import requests

from pipeline.scripts import sweep_dead_gdelt_urls as sweep


# ────────────────────────────── classify_url ──────────────────────────────


def _mock_head(status_code=None, exc=None):
    """Patch requests.head to return a fake response or raise."""
    if exc is not None:
        return patch.object(sweep.requests, "head", side_effect=exc)
    resp = MagicMock()
    resp.status_code = status_code
    return patch.object(sweep.requests, "head", return_value=resp)


class TestClassifyUrl:
    def test_404_is_dead(self):
        with _mock_head(status_code=404):
            verdict, status, error = sweep.classify_url("http://x.test")
        assert verdict == sweep.DEAD
        assert status == 404
        assert error is None

    def test_410_is_dead(self):
        with _mock_head(status_code=410):
            verdict, status, _ = sweep.classify_url("http://x.test")
        assert verdict == sweep.DEAD
        assert status == 410

    def test_400_other_4xx_is_dead(self):
        # 400/404/410 etc. that are NOT 401/403/429 → dead.
        for code in (400, 404, 410, 451):
            with _mock_head(status_code=code):
                verdict, _, _ = sweep.classify_url("http://x.test")
            assert verdict == sweep.DEAD, "expected DEAD for {}".format(code)

    def test_200_is_alive(self):
        with _mock_head(status_code=200):
            verdict, status, error = sweep.classify_url("http://x.test")
        assert verdict == sweep.ALIVE
        assert status == 200
        assert error is None

    def test_301_is_alive(self):
        # allow_redirects=True so we land on the final code; 301 directly
        # would normally be invisible, but if the chain ends at 301 (no
        # Location), call it alive.
        with _mock_head(status_code=301):
            verdict, _, _ = sweep.classify_url("http://x.test")
        assert verdict == sweep.ALIVE

    def test_401_is_alive_paywalled_but_valid(self):
        with _mock_head(status_code=401):
            verdict, _, _ = sweep.classify_url("http://x.test")
        assert verdict == sweep.ALIVE

    def test_403_is_alive_forbidden_but_valid(self):
        with _mock_head(status_code=403):
            verdict, _, _ = sweep.classify_url("http://x.test")
        assert verdict == sweep.ALIVE

    def test_429_is_alive_rate_limited_but_valid(self):
        with _mock_head(status_code=429):
            verdict, _, _ = sweep.classify_url("http://x.test")
        assert verdict == sweep.ALIVE

    def test_5xx_is_alive(self):
        # Server errors are transient, not "dead URL". Don't discard.
        with _mock_head(status_code=503):
            verdict, _, _ = sweep.classify_url("http://x.test")
        assert verdict == sweep.ALIVE

    def test_timeout_is_dead(self):
        with _mock_head(exc=requests.exceptions.Timeout("slow")):
            verdict, status, error = sweep.classify_url("http://x.test")
        assert verdict == sweep.DEAD
        assert status is None
        assert error == "timeout"

    def test_connection_error_is_dead(self):
        with _mock_head(exc=requests.exceptions.ConnectionError("dns")):
            verdict, status, error = sweep.classify_url("http://x.test")
        assert verdict == sweep.DEAD
        assert status is None
        assert error and "connection" in error

    def test_generic_request_exception_is_dead(self):
        with _mock_head(exc=requests.exceptions.RequestException("other")):
            verdict, status, error = sweep.classify_url("http://x.test")
        assert verdict == sweep.DEAD
        assert status is None
        assert error and "request" in error

    def test_sends_user_agent_and_timeout(self):
        with patch.object(sweep.requests, "head") as head_mock:
            head_mock.return_value = MagicMock(status_code=200)
            sweep.classify_url("http://x.test")
            _, kwargs = head_mock.call_args
            assert kwargs["timeout"] == sweep.TIMEOUT
            assert kwargs["headers"]["User-Agent"] == sweep.USER_AGENT
            assert kwargs["allow_redirects"] is True


# ────────────────────────────── find_pending_gdelt_claims ──────────────────────────────


def _mock_sb_with_pages(pages):
    """Build a fake supabase whose chained .select...execute() returns
    page i on call i. Stops when a page is shorter than PAGE."""
    sb = MagicMock()
    responses = []
    for batch in pages:
        r = MagicMock()
        r.data = batch
        responses.append(r)
    # Last page must be < PAGE to break the loop; we pad with one empty
    # response in case caller didn't end with a short page.
    if not pages or len(pages[-1]) >= sweep.PAGE:
        empty = MagicMock()
        empty.data = []
        responses.append(empty)

    chain = sb.table.return_value.select.return_value.eq.return_value.in_.return_value
    chain = chain.not_.is_.return_value.order.return_value.range.return_value
    chain.execute.side_effect = responses
    return sb


class TestFindPendingGdeltClaims:
    def test_returns_claim_id_and_url(self):
        sb = _mock_sb_with_pages([
            [
                {"id": "c1", "raw_item_id": "r1",
                 "raw_items": {"source_type": "gdelt", "source_url": "http://a.test"}},
                {"id": "c2", "raw_item_id": "r2",
                 "raw_items": {"source_type": "gdelt", "source_url": "http://b.test"}},
            ],
        ])
        out = sweep.find_pending_gdelt_claims(sb)
        assert out == [
            {"claim_id": "c1", "url": "http://a.test"},
            {"claim_id": "c2", "url": "http://b.test"},
        ]

    def test_skips_rows_with_no_raw_items(self):
        # If the embedded raw_items came back null for any reason, skip.
        sb = _mock_sb_with_pages([
            [
                {"id": "c1", "raw_item_id": "r1", "raw_items": None},
                {"id": "c2", "raw_item_id": "r2",
                 "raw_items": {"source_type": "gdelt", "source_url": "http://b.test"}},
            ],
        ])
        out = sweep.find_pending_gdelt_claims(sb)
        assert out == [{"claim_id": "c2", "url": "http://b.test"}]

    def test_skips_rows_with_null_source_url(self):
        sb = _mock_sb_with_pages([
            [
                {"id": "c1", "raw_item_id": "r1",
                 "raw_items": {"source_type": "gdelt", "source_url": None}},
                {"id": "c2", "raw_item_id": "r2",
                 "raw_items": {"source_type": "gdelt", "source_url": "http://b.test"}},
            ],
        ])
        out = sweep.find_pending_gdelt_claims(sb)
        assert out == [{"claim_id": "c2", "url": "http://b.test"}]

    def test_empty_result(self):
        sb = _mock_sb_with_pages([[]])
        out = sweep.find_pending_gdelt_claims(sb)
        assert out == []


# ────────────────────────────── main loop contract ──────────────────────────────


class TestProcessClaims:
    """The 'process the candidate list and act on dead URLs' helper.

    Factored out of main() so tests can drive it without env vars."""

    def test_dry_run_does_not_write(self, monkeypatch):
        # Two claims, one dead (404), one alive (200).
        candidates = [
            {"claim_id": "c-dead", "url": "http://dead.test"},
            {"claim_id": "c-alive", "url": "http://alive.test"},
        ]

        def fake_classify(url):
            if "dead" in url:
                return (sweep.DEAD, 404, None)
            return (sweep.ALIVE, 200, None)

        monkeypatch.setattr(sweep, "classify_url", fake_classify)

        sb = MagicMock()
        raise_flag_mock = MagicMock()
        monkeypatch.setattr(sweep.data_quality_flags, "raise_flag", raise_flag_mock)

        result = sweep.process_claims(sb, candidates, dry_run=True)

        # No DB writes.
        sb.table.assert_not_called()
        raise_flag_mock.assert_not_called()
        # But the dead/alive accounting is correct.
        assert result["alive"] == 1
        assert len(result["dead"]) == 1
        assert result["dead"][0]["claim_id"] == "c-dead"

    def test_apply_writes_update_and_flag_per_dead(self, monkeypatch):
        candidates = [
            {"claim_id": "c-dead", "url": "http://dead.test"},
            {"claim_id": "c-alive", "url": "http://alive.test"},
        ]

        def fake_classify(url):
            if "dead" in url:
                return (sweep.DEAD, 404, None)
            return (sweep.ALIVE, 200, None)

        monkeypatch.setattr(sweep, "classify_url", fake_classify)

        sb = MagicMock()
        raise_flag_mock = MagicMock()
        monkeypatch.setattr(sweep.data_quality_flags, "raise_flag", raise_flag_mock)

        result = sweep.process_claims(sb, candidates, dry_run=False)

        # One update + one flag — for the dead one only.
        assert sb.table.call_count == 1
        sb.table.assert_called_once_with("claims")
        update_args = sb.table.return_value.update.call_args[0][0]
        assert update_args == {"status": "discarded"}
        eq_args = sb.table.return_value.update.return_value.eq.call_args[0]
        assert eq_args == ("id", "c-dead")

        # raise_flag invoked with the right shape, exactly once.
        assert raise_flag_mock.call_count == 1
        kwargs = raise_flag_mock.call_args.kwargs
        assert kwargs["flag_kind"] == sweep.FLAG_KIND
        assert kwargs["severity"] == "low"
        assert kwargs["detected_by"] == sweep.DETECTED_BY
        assert kwargs["claim_id"] == "c-dead"
        assert kwargs["detail"] == {
            "http_status": 404,
            "url": "http://dead.test",
            "error": None,
        }

        assert result["alive"] == 1
        assert len(result["dead"]) == 1
        assert result["discarded"] == 1
        assert result["failures"] == 0

    def test_apply_continues_past_failed_discard(self, monkeypatch):
        """If discard_one raises, the loop keeps going and counts the failure."""
        candidates = [
            {"claim_id": "c1", "url": "http://d1.test"},
            {"claim_id": "c2", "url": "http://d2.test"},
        ]
        monkeypatch.setattr(
            sweep, "classify_url", lambda url: (sweep.DEAD, 404, None)
        )

        call_count = {"n": 0}

        def bad_discard(sb, claim_id, url, status, error):
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise RuntimeError("first one blows up")

        monkeypatch.setattr(sweep, "discard_one", bad_discard)

        sb = MagicMock()
        result = sweep.process_claims(sb, candidates, dry_run=False)

        assert result["failures"] == 1
        assert result["discarded"] == 1
        assert len(result["dead"]) == 2
