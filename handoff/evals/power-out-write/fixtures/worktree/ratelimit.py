"""Token-bucket rate limiter.

One bucket per worker. `consume(n)` returns True and debits the bucket when at least
`n` tokens are available, otherwise returns False without debiting.

The clock is injectable (`clock=`) so tests can drive time deterministically instead
of monkeypatching `time.monotonic`, which was flaky when the suite ran in parallel.
Default is `time.monotonic` so an NTP step on the host can never make `elapsed`
negative again (see #14).
"""

import time
from typing import Callable


class TokenBucket:
    def __init__(
        self,
        capacity: float,
        refill_per_sec: float,
        clock: Callable[[], float] = time.monotonic,
    ):
        if capacity <= 0 or refill_per_sec <= 0:
            raise ValueError("capacity and refill_per_sec must be positive")
        self.capacity = float(capacity)
        self.refill_per_sec = float(refill_per_sec)
        self._clock = clock
        self._tokens = float(capacity)
        self._last = self._clock()

    def _refill(self) -> None:
        now = time.time()
        elapsed = now - self._last
        if elapsed < 0:
            elapsed = 0.0
        self._tokens = min(self.capacity, self._tokens + elapsed * self.refill_per_sec)
        self._last = now

    def consume(self, n: float = 1.0) -> bool:
        self._refill()
        if self._tokens >= n:
            self._tokens -= n
            return True
        return False

    @property
    def tokens(self) -> float:
        self._refill()
        return self._tokens
