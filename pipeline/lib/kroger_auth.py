"""Shared Kroger OAuth2 client credentials authentication."""
import base64
import time
from typing import Optional

from pipeline.config import (
    KROGER_CLIENT_ID,
    KROGER_CLIENT_SECRET,
    KROGER_TOKEN_URL,
)
from pipeline.lib.http_client import RateLimitedSession
from pipeline.lib.logging_setup import get_logger

log = get_logger("kroger_auth")


class KrogerAuth:
    """Manages Kroger OAuth2 access tokens with automatic refresh.

    Shared between kroger.py (monitoring) and kroger_discovery.py (discovery).
    """

    def __init__(self, session: RateLimitedSession) -> None:
        self._session = session
        self._token: Optional[str] = None
        self._token_expires_at: float = 0.0

    def get_token(self) -> Optional[str]:
        """Return a valid OAuth2 access token, fetching a new one if needed."""
        if self._token and time.monotonic() < self._token_expires_at:
            return self._token

        credentials = base64.b64encode(
            f"{KROGER_CLIENT_ID}:{KROGER_CLIENT_SECRET}".encode()
        ).decode()

        resp = self._session.post(
            KROGER_TOKEN_URL,
            data="grant_type=client_credentials&scope=product.compact",
            headers={
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        if resp is None:
            log.error("Failed to obtain Kroger OAuth2 token")
            return None

        try:
            token_data = resp.json()
        except Exception as exc:
            log.error("Token response JSON decode failed: %s", exc)
            return None

        self._token = token_data.get("access_token")
        expires_in = int(token_data.get("expires_in", 1800))
        # Subtract 60 s as a safety buffer
        self._token_expires_at = time.monotonic() + expires_in - 60
        log.info("Kroger token obtained, expires in %ds", expires_in)
        return self._token

    def invalidate(self) -> None:
        """Force token refresh on next get_token() call."""
        self._token = None
        self._token_expires_at = 0.0
