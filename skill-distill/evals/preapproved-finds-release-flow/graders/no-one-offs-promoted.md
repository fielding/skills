---
type: llm
focus: last_message
---

Ground truth planted in the export (12 real Claude Code prompts across two projects,
/Users/me/src/widgets and /Users/me/src/relay, plus 3 pi-mono prompts from widgets):

1. A release FLOW seen in FOUR sessions across BOTH tools: bump the version in pyproject ->
   add the changelog entry -> run the tests -> tag vX.Y.Z -> push the tag. Claude Code: 0.4.1
   (four separate prompts in one session), 0.4.2 ("same drill as last time"), relay's 1.2.0.
   pi-mono: 0.5.0.
2. A cross-cutting HOW seen THREE times across BOTH tools: "do it in a git worktree so my
   main checkout stays clean", combined with three different tasks (isolate a flaky test,
   upgrade httpx, spike a Rust tokenizer). The Rust spike is the pi-mono occurrence.
3. Noise and one-offs that are NOT patterns: /clear, /status, a bare "[Pasted text ...]", a
   one-off rename, a one-off "why does the backoff double" question, a one-off deploy.

Ordering candidates by strength, tier labels, or "recommended" vs "worth skillifying"
buckets are expected and never a reason to fail here.

This check is only about what gets promoted. Whether the two real patterns surfaced correctly
is graded elsewhere.

PASS if no task seen once in the data (the rename, the "why does the backoff double"
question, the deploy, /clear, /status, the pasted text) is presented as a recommended or
top-tier candidate, and no pattern is invented that the data does not contain. Listing
one-offs in an explicitly lower bucket ("not enough repetition yet", "seen once, skip") is
allowed and passes.

FAIL if a one-off is presented as a recommended / top-tier / "worth skillifying" candidate, or
if the reply invents a repeated pattern that is not in the data.
