---
type: llm
focus: { source: file, path: ".tix/issues.jsonl" }
weight: 2
---

This is the tix store after the run: one JSON object per line. Issue records look like
`{"type":"issue","id":"<prefix>-<hex>","title":"...", ...}` and dependency records look like
`{"type":"dep","src_id":"<id>","dst_id":"<id>","kind":"blocks","state":"active"}`, where
src_id BLOCKS dst_id (src must finish before dst becomes ready).

The user asked for three issues: (A) exponential-backoff retry in fetch.py, (B) a --retries
CLI flag, (C) README docs for the flag; and said "B depends on A being done first" and that
this is the only ordering constraint.

PASS if there are exactly three issue records whose titles clearly correspond to A, B and C,
and exactly one dep record with kind "blocks" whose src_id is the id of the A (retry/backoff)
issue and whose dst_id is the id of the B (--retries flag) issue.

FAIL if the dependency is reversed (B blocks A), if it links C to anything, if there are
extra or missing issues, if there are additional dep records, or if the file is missing.
