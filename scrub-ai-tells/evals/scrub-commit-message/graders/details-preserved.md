---
type: regex
target: last_message
pattern: '^(?=[\s\S]*Add retry with backoff to the export uploader)(?=[\s\S]*503)(?=[\s\S]*RETRY_MAX_ATTEMPTS)(?=[\s\S]*RETRY_BASE_MS)(?=[\s\S]*\.part)(?=[\s\S]*Fixes: #4821)(?=[\s\S]*Co-Authored-By: Priya Natarajan <priya@example\.com>)'
weight: 2
---

Subject line, the 503 detail, both constants, the .part cleanup, the `Fixes:` label colon
(a label colon, which the skill says to leave alone) and the trailer must all survive.
