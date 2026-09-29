import unittest

from ratelimit import TokenBucket


class FakeClock:
    def __init__(self, start: float = 0.0):
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


class TokenBucketTests(unittest.TestCase):
    def test_consume_within_capacity(self):
        bucket = TokenBucket(capacity=3, refill_per_sec=1)
        self.assertTrue(bucket.consume())
        self.assertTrue(bucket.consume())
        self.assertTrue(bucket.consume())
        self.assertFalse(bucket.consume())

    def test_rejects_non_positive_config(self):
        with self.assertRaises(ValueError):
            TokenBucket(capacity=0, refill_per_sec=1)

    def test_refill_after_sleep(self):
        clock = FakeClock()
        bucket = TokenBucket(capacity=2, refill_per_sec=2, clock=clock)
        self.assertTrue(bucket.consume(2))
        self.assertFalse(bucket.consume())
        clock.advance(1.0)  # 1s at 2 tokens/s -> back to capacity
        self.assertAlmostEqual(bucket.tokens, 2.0)
        self.assertTrue(bucket.consume(2))


if __name__ == "__main__":
    unittest.main()
