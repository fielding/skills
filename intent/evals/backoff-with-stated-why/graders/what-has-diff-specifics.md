---
type: llm
focus: { source: file, path: "intent.md" }
weight: 2
---

This is the intent.md for an uncommitted change on branch fix/retry-backoff. The diff is the
only source of these specifics: pulse/http_client.py replaces RETRY_ATTEMPTS=3 /
RETRY_DELAY_S=0.5 with MAX_ATTEMPTS=5, BASE_DELAY_S=0.25, MAX_DELAY_S=8.0; adds
backoff_delay(attempt, rng) implementing full-jitter exponential backoff
(uniform(0, min(cap, base*2**attempt))); fetch() sleeps backoff_delay(attempt) between
attempts and skips the sleep after the final attempt; a new tests/test_http_client.py checks
the delay ceiling and cap. The user's own summary was only "reworked the retry logic in
pulse/http_client.py so retries back off with jitter instead of sleeping a fixed 500ms".

PASS if the What section contains at least three specifics that only the diff shows (e.g. 5
attempts, the 8 s cap, the 0.25 s base, the backoff_delay function or its formula, the sleep
skipped after the last attempt, the new test file), not just a paraphrase of the user's
"reworked the retry logic".

FAIL if What is only the user's own summary with fewer than three diff-derived specifics, or
if the What section or the file is missing.
