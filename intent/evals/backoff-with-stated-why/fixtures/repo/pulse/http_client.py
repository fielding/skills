"""Thin HTTP client for the vendor metrics API."""

import time

import requests

RETRY_ATTEMPTS = 3
RETRY_DELAY_S = 0.5


class TransientError(Exception):
    """A response the caller may retry (429 or 5xx)."""


def fetch(url: str, session: requests.Session | None = None) -> dict:
    """GET `url` as JSON, retrying transient failures a fixed number of times."""
    session = session or requests.Session()
    last: Exception | None = None
    for _ in range(RETRY_ATTEMPTS):
        try:
            return _get(session, url)
        except TransientError as exc:
            last = exc
            time.sleep(RETRY_DELAY_S)
    raise RuntimeError(f"gave up on {url}") from last


def _get(session: requests.Session, url: str) -> dict:
    resp = session.get(url, timeout=10)
    if resp.status_code == 429 or resp.status_code >= 500:
        raise TransientError(f"{resp.status_code} from {url}")
    resp.raise_for_status()
    return resp.json()
