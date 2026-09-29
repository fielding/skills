"""Thin HTTP client for the vendor metrics API."""

import random
import time

import requests

MAX_ATTEMPTS = 5
BASE_DELAY_S = 0.25
MAX_DELAY_S = 8.0


class TransientError(Exception):
    """A response the caller may retry (429 or 5xx)."""


def backoff_delay(attempt: int, rng: random.Random | None = None) -> float:
    """Full-jitter exponential backoff: uniform(0, min(MAX_DELAY_S, BASE_DELAY_S * 2**attempt))."""
    pick = (rng or random).uniform
    ceiling = min(MAX_DELAY_S, BASE_DELAY_S * (2**attempt))
    return pick(0.0, ceiling)


def fetch(url: str, session: requests.Session | None = None) -> dict:
    """GET `url` as JSON, retrying transient failures with jittered exponential backoff."""
    session = session or requests.Session()
    last: Exception | None = None
    for attempt in range(MAX_ATTEMPTS):
        try:
            return _get(session, url)
        except TransientError as exc:
            last = exc
            if attempt < MAX_ATTEMPTS - 1:
                time.sleep(backoff_delay(attempt))
    raise RuntimeError(f"gave up on {url} after {MAX_ATTEMPTS} attempts") from last


def _get(session: requests.Session, url: str) -> dict:
    resp = session.get(url, timeout=10)
    if resp.status_code == 429 or resp.status_code >= 500:
        raise TransientError(f"{resp.status_code} from {url}")
    resp.raise_for_status()
    return resp.json()
