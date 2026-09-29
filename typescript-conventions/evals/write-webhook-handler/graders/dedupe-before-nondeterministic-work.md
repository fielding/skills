---
type: llm
focus: last_message
---

Idempotency runs first. If a retry can reach classification, an outbound call, or a job
enqueue before the dedupe check, the same event can be judged twice and produce two different
outcomes; the insert-and-catch has to come before anything nondeterministic or external.

This check is only about ordering. The dedupe mechanism itself and whether the write is
awaited are graded elsewhere.

PASS if the dedupe/insert step runs before any nondeterministic or external work
(classification, outbound calls, job enqueueing, other side effects), so a retry replays the
original outcome rather than being re-judged.

FAIL if any nondeterministic or external work happens before the dedupe/insert, or if the
handler enqueues, calls out, or classifies the event and only then records it.
