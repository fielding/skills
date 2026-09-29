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

This check is only about the git-worktree habit. The release workflow and one-off handling
are graded elsewhere.

PASS if the git-worktree habit ("do it in a worktree so the main checkout stays clean") is a
named candidate, listed as a HOW / preference / cross-cutting habit or as an ordinary
candidate, with a stated count of two or three (any range that includes 2 or 3 passes).

FAIL if no worktree candidate appears, or if its stated count is one, is four or more, or is a
range that excludes both 2 and 3.
