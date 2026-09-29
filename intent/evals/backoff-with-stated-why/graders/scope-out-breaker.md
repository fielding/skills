---
type: llm
focus: { source: file, path: "intent.md" }
---

This is the intent.md for an uncommitted change on branch fix/retry-backoff. The diff touches
only pulse/http_client.py and the new tests/test_http_client.py; breaker.py, README.md and
test_breaker.py are unchanged. The user's stated Scope-Out: breaker.py / circuit-breaker
thresholds are deliberately untouched and are a separate conversation with Priya (the vendor
key rotation is also out: config, not this diff).

PASS if Scope Out lists breaker.py (or the circuit breaker) with its rationale, and
breaker.py is not described as changed or listed under In.

FAIL if breaker.py is missing from Scope Out, listed under In, or described as changed.
