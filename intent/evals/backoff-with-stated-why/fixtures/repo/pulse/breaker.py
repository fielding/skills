"""Per-account circuit breaker. Opens after `threshold` consecutive failures."""

import time


class Breaker:
    def __init__(self, threshold: int = 5, cooldown_s: float = 60.0) -> None:
        self.threshold = threshold
        self.cooldown_s = cooldown_s
        self._failures = 0
        self._opened_at: float | None = None

    def allow(self) -> bool:
        if self._opened_at is None:
            return True
        if time.monotonic() - self._opened_at >= self.cooldown_s:
            self._opened_at = None
            self._failures = 0
            return True
        return False

    def record(self, ok: bool) -> None:
        if ok:
            self._failures = 0
            return
        self._failures += 1
        if self._failures >= self.threshold:
            self._opened_at = time.monotonic()
