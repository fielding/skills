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

This check is only about the occurrence count stated for the release workflow. Whether its
steps are listed, which tools it is attributed to, and the other candidates are graded
elsewhere.

PASS if the release workflow's stated occurrence count is three or four. Any phrasing whose
range includes 3 or 4 passes: "3x", "4x", "four sessions", "3-4 times", "4-5 occurrences",
"seen 4 times across ...".

FAIL if the count given for the release workflow is "once", "2x", "10x", or any figure or
range that excludes both 3 and 4, or if no occurrence count is stated for it at all.
