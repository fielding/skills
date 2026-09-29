import unittest

from ratelimit import TokenBucket


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


if __name__ == "__main__":
    unittest.main()
