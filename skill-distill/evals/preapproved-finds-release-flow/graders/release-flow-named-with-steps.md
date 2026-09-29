---
type: llm
focus: last_message
weight: 2
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

This check is only about whether the release workflow surfaced with its steps. Its count, its
tool attribution, the worktree habit, and one-off handling are graded elsewhere.

PASS if the release workflow is a named candidate (any name that clearly refers to it:
"release", "cut a release", "ship a version", "tag and publish") and at least three of its
five steps are listed: version bump, changelog entry, run tests, tag, push the tag.

FAIL if the release workflow is not presented as a candidate, or if fewer than three of its
five steps are listed for it.
