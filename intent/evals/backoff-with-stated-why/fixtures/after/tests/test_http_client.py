import random

from pulse.http_client import BASE_DELAY_S, MAX_DELAY_S, backoff_delay


def test_delay_stays_under_exponential_ceiling():
    rng = random.Random(7)
    for attempt in range(6):
        for _ in range(200):
            d = backoff_delay(attempt, rng)
            assert 0.0 <= d <= min(MAX_DELAY_S, BASE_DELAY_S * (2**attempt))


def test_delay_is_capped():
    rng = random.Random(11)
    assert all(backoff_delay(20, rng) <= MAX_DELAY_S for _ in range(500))
