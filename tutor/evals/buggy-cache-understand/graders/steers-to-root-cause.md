---
type: llm
focus: trace
weight: 2
---

The actual defect in cache.py: `memoize` keeps one cache dict (`_store`, a mutable default
argument) shared by every decorated function, and keys entries by call arguments only. So
`monthly_revenue("2026-01")` and `monthly_refunds("2026-01")` read and write the same entry
and return each other's values; the per-function `ttl` is irrelevant to that collision.

PASS if the session frames the problem to be understood around that mechanism — by naming the
shared store / key collision, or by steering the learner toward it with questions or
predictions about what the cache key is and whether the two functions share storage. The
checklist file counts as part of the session.

FAIL if the session points the learner primarily at something else (only the TTL, thread
safety, time.time drift) or gives no direction about the cause at all.
