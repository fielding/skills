---
type: llm
focus: last_message
---

Idempotency lives in the database, so the database write is the handler's real work; a 200
sent before the persist has completed tells the provider "delivered" for an event that may
never land.

This check is only about awaiting. The dedupe mechanism and its position relative to other
work are graded elsewhere.

PASS if the persist (the INSERT into `webhook_events`) is awaited before the response is sent,
and no later step depends on a write that was fired without being awaited.

FAIL if the insert is fire-and-forget (called without `await` and the response sent
regardless), if the response is sent and the write happens afterwards, or if a later step
depends on a write that was not awaited.
