---
name: intent
description: >-
  Capture the intent of a code change as plain, factual context: What it does,
  Why, what is in/out of Scope, and the Decisions reviewers shouldn't
  re-litigate. Stage 0 of the `gate` code pre-submission pipeline. Downstream
  stages (lint/test gate, state-space-minimization, mutation testing,
  conventions, review-crew, fold-findings) review the change against this stated
  purpose, and it becomes the PR body later. Use when the user says "establish
  intent", "capture the intent", "what is this change for", "/intent", or before
  running the gate pipeline on a fresh branch. Produces plain context, NOT
  voiced or scrubbed prose -- voice and AI-tell scrubbing happen later, at the
  open-PR stage. AI-written is fine here.
user-invocable: true
---

# Intent

Stage 0 of the `gate` pre-submission pipeline. Capture WHY a change was made as
plain, factual context so every downstream stage can review the change against
its stated purpose -- and so the human never has to re-explain it.

**This is not user-facing prose.** Do NOT apply voice or scrub AI tells here.
Keep it plain, clear, factual. AI phrasing is fine. (Voicing/scrubbing happens
later, at the open-PR stage.) The job here is accuracy and completeness, not
style.

## Output

A plain `intent.md` at a stable per-branch path so later stages can find it:
`/tmp/<branch>-intent.md` (use the current `git branch --show-current`; replace
`/` in the branch name with `-`).

```
# Intent: <short title>
## What
<what the change does -- factual, from the diff + transcript>
## Why
<goal / motivation -- from the transcript, or asked if absent>
## Scope
- In: <what this change covers>
- Out: <deliberately deferred, each with a one-line rationale>
## Decisions
- <settled tradeoff/decision + why -- so reviewers don't re-litigate it>
```

Keep it tight. Every line should be something a reviewer can act on. No filler,
no hedging, no "this PR aims to."

## Capture (priority order)

### 1. PRIMARY -- the recent agent transcript(s) for THIS change

Whoever just wrote the code already expressed the WHY in conversation. Read the
**most recent relevant session(s)** whose `cwd` matches the current repo, newest
first. **Claude Code is the primary / most recent tool**; Codex and pi are also
supported.

Use the vendored reader (self-contained -- no skill-distill dependency):

```
python3 {skill-dir}/scripts/read-recent-session.py            # newest matching session
python3 {skill-dir}/scripts/read-recent-session.py --list --count 5   # pick the right one
python3 {skill-dir}/scripts/read-recent-session.py --count 2 --max-chars 6000
```

Notes on the reader:
- Matches sessions by the transcript's recorded `cwd` (inside the repo root),
  not the lossy encoded directory name.
- Excludes Claude Code subagent sidechains by default (`subagents/` transcripts
  are the agent talking to itself, not the human-stated WHY). Pass
  `--include-subagents` only if the top-level session is thin.
- The current intent-capture session is itself the newest match -- skip it and
  use the session that actually contains the change discussion. `--list` makes
  this easy: read the timestamps/branches and choose the one for THIS change.
- Already applies a light secret-redact pass on its output.

Read the transcript and summarize + disambiguate it into What / Why / Scope /
Decisions. Pull Scope-Out and Decisions from moments where the user or agent
explicitly deferred something or chose between options.

### 2. FALLBACK -- no usable transcript

Derive the **What** from the diff + commit messages + branch name:

```
git diff master...HEAD          # or the merge base
git log master..HEAD --oneline
git branch --show-current
```

Then ask the user a few **targeted** questions for only the non-inferable parts:
- Why / the goal behind it
- What is deliberately out of scope
- Any key decisions a reviewer might otherwise second-guess

### 3. Never ask what the diff already shows

If the diff makes the What obvious, state it -- don't ask. Only ask about intent
that isn't recoverable from code: motivation, deferred scope, and tradeoffs.

## Redact step

Before writing `intent.md`, apply a **light secret-redact**: strip obvious pasted
secrets -- API keys, tokens, `op://` references, bearer/Authorization values,
JWTs, `KEY=`/`TOKEN=`/`SECRET=` assignments -- so they never land in the file,
even internally. The reader does this on its output; do the same for anything you
add by hand. When unsure, redact.

## How downstream stages use it

`intent.md` is the shared contract for the rest of `gate`:
- **lint/test gate, conventions** -- sanity baseline; intent frames what "done"
  means for this change.
- **state-space-minimization, mutation testing** -- check the change actually
  covers its stated Scope (and nothing creeps in from Scope-Out).
- **review-crew** -- reviews the diff *against* the stated What/Why instead of
  guessing the goal; Decisions tell reviewers what's already settled.
- **fold-findings** -- reconciles crew findings with the declared Scope/Decisions.
- **open-PR stage** -- takes this plain `intent.md` and *then* voices + scrubs it
  into the user-facing PR body.

So: be accurate and complete here. Style is somebody else's stage.
