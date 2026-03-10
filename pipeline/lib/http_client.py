"""Retry-aware, rate-limited HTTP session for the pipeline."""
import time
from typing import Optional

import requests
from requests.adapters import HTTPAdapter, Retry

from pipeline.config import DEFAULT_MAX_RETRIES, DEFAULT_TIMEOUT, USER_AGENT
from pipeline.lib.logging_setup import get_logger

log = get_logger("http")


class RateLimitedSession:
    """HTTP session with per-request rate limiting and automatic retries.

    Args:
        requests_per_second: Max requests per second (e.g. 0.67 = 1 req/1.5s).
        max_retries: Number of retries on 429/5xx errors.
        timeout: Default request timeout in seconds.
        user_agent: User-Agent header value.
    """

    def __init__(
        self,
        requests_per_second: float = 1.0,
        max_retries: int = DEFAULT_MAX_RETRIES,
        timeout: int = DEFAULT_TIMEOUT,
        user_agent: str = USER_AGENT,
    ):
        self._min_interval = 1.0 / requests_per_second if requests_per_second > 0 else 0
        self._last_request_time = 0.0
        self._timeout = timeout

        self._session = requests.Session()
        self._session.headers.update({"User-Agent": user_agent})

        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)

    def _throttle(self) -> None:
        """Wait if needed to respect rate limit."""
        if self._min_interval <= 0:
            return
        elapsed = time.monotonic() - self._last_request_time
        if elapsed < self._min_interval:
            wait = self._min_interval - elapsed
            time.sleep(wait)
        self._last_request_time = time.monotonic()

    def get(
        self, url: str, raise_for_status: bool = True, **kwargs
    ) -> Optional[requests.Response]:
        """Rate-limited GET request.  Returns None on unrecoverable error.

        Set raise_for_status=False to get the raw response even on 4xx/5xx
        (useful when the caller needs to inspect the status code, e.g. 401).
        """
        self._throttle()
        kwargs.setdefault("timeout", self._timeout)
        try:
            resp = self._session.get(url, **kwargs)
            if raise_for_status:
                resp.raise_for_status()
            return resp
        except requests.RequestException as exc:
            log.warning("GET %s failed: %s", url, exc)
            return None

    def post(self, url: str, **kwargs) -> Optional[requests.Response]:
        """Rate-limited POST request.  Returns None on unrecoverable error."""
        self._throttle()
        kwargs.setdefault("timeout", self._timeout)
        try:
            resp = self._session.post(url, **kwargs)
            resp.raise_for_status()
            return resp
        except requests.RequestException as exc:
            log.warning("POST %s failed: %s", url, exc)
            return None

    def close(self) -> None:
        self._session.close()
