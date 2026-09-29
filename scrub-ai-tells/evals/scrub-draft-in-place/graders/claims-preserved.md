---
type: llm
focus: { source: file, path: "draft.md" }
weight: 2
---

This is draft.md after the scrub. The original made these claims, which the user wrote and
which must survive with the same meaning (rephrasing is fine, softening or deleting is not):

1. The old exporter silently dropped rows with null timestamps, so weekly counts never matched
   the dashboard.
2. The new pipeline streams (keeps memory flat) and handles pagination for the user.
3. It exports any saved filter to CSV or JSONL, supports scheduled exports via `tix sync`, and
   resumes after a network failure.
4. p95 export latency went from 1.4s to 300ms per page; a 40k-ticket export finishes in under
   two minutes.
5. `--since` accepts any ISO date; `--out` may be omitted, in which case output goes to stdout.
6. Each page is fetched exactly once.

This check is only about those six claims. Whether anything new was added, and whether the
code block is intact, are graded elsewhere.

PASS if all six claims are still present with the same meaning.

FAIL if any claim above is missing or weakened (e.g. "may have dropped rows", the latency
numbers removed, the "exactly once" guarantee gone or hedged).
