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

This check is only about tool attribution for the release workflow. Its steps, its count, and
the other candidates are graded elsewhere.

PASS if the reply connects the release workflow to both sources in some form: it says the
pattern appeared in both Claude Code and pi-mono / "both tools" / "cross-tool", OR it cites
evidence for it from both history.jsonl and a pi session file.

FAIL if the reply never connects the release workflow to pi-mono, or attributes it to Claude
Code only. Mentioning pi-mono elsewhere, for a different candidate, does not count.
