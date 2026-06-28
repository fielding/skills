---
name: retro
description: >-
  End-of-session self-improvement, run as gate's stage 13 or on demand. Reviews a
  work session for durable, general learnings and routes them in two halves: the
  SKILL half (gotchas about your own skills/pipeline -- crew strands, convention
  gaps, gate mechanics) folds back into the skill sources or files a proposal; the
  DOMAIN half (project knowledge -- house conventions, reviewer rulings, data
  patterns) always writes a per-project retro note and, only when your operator
  config matches the repo, additionally distills into that knowledge base.
  Generalized and project-agnostic: routing is config-driven, so it runs for any
  project without cross-contaminating any one KB. Invoke at the end of a session,
  after a gate run, or on "retro", "session retrospective", "what did we learn",
  "distill the session".
allowed-tools: Bash, Read, Edit, Write, Grep, Glob
---

# Retro

The closing ritual for a work session: turn what the session *taught* into durable
updates, so the next session starts ahead of this one. The bar is **durable and
general**, not "everything that happened." Most of a session is execution; only a
little of it is a lesson.

Retro learnings split into two halves with different homes. Keeping them separate is
the whole point -- it is what lets retro run on *any* project without a personal or
employer-specific knowledge base ever receiving the wrong project's learnings.

- **Skill half** -- what the session taught about *your own tooling*: a review-crew
  strand, a gap in a conventions pack, a gate mechanic that bit, an SSM or
  fold/atomic hazard. Project-agnostic. Homes in *your* space (the skill sources, or
  your proposal tracker), never a project KB.
- **Domain half** -- what the session taught about *this project*: a house
  convention, a reviewer ruling, a data-model or design pattern, a lint gotcha. Homes
  in a per-project retro note always, plus a configured knowledge base when (and only
  when) your operator config maps this repo to one.

## Phase 0: resolve routing (no hard project gate)

retro does **not** gate on any particular project -- it runs everywhere; routing is
what changes. Resolve these first:

1. **Repo slug** -- `git remote get-url origin` -> `owner/repo`.
2. **Operator routing** -- read `~/.config/gate/config.toml` (the operator layer; see
   gate's `references/config.md`). Two things come from it, both optional:
   - **KB routing** -- match the slug against each `[[knowledge_base]]` `match` glob. A
     hit yields a `path` (an external KB) and `peer_reviewed` flag; no hit (or no file)
     means the domain half stays project-local only. There is **no default external
     destination.**
   - **Skill-half routing** -- the `[retro]` section's `skills_root` (your authored-
     skills tree), `skills_repo` (where in-place edits get pushed), and `proposal_cmd`
     (how proposals are filed), all used in Phase 3. Absent means report-only for the
     skill half.
3. **Project retro note path** -- resolve the `.handoff` location exactly as
   `handoff`'s SKILL.md does (so both skills agree no matter which writes first): if
   `.handoff` already exists, use it; else read `vault_root` from the `[handoff]`
   section of the operator config and, when set, create `<vault_root>/<proj>/handoff/`
   + the in-repo `.handoff` symlink, else a plain gitignored `<repo-root>/.handoff/`.
   The note lives in a `retro/` subdir so it never clutters the canonical cold-start
   docs: `<.handoff>/retro/retro-<YYYY-MM-DD>.md`.

## Phase 1: scan the session for candidates (greedy)

Collect candidates into the two halves. Be greedy here; Phase 2 is where things get
cut. If invoked detached from the session that did the work, reconstruct from the
git log, the PR thread, and any gate-run artifacts (review-crew's `pr-comment.md`,
the floor/mutation output).

**Skill-half buckets** (about your tooling):
- **review-crew behavior** -- a strand, a verdict quirk, an artifact location, a
  failure mode.
- **conventions-pack gaps** -- a language idiom the pack should state but didn't.
- **gate mechanics** -- a stage that mis-fired, a config fallback that was wrong, a
  loop that didn't converge, a worktree/cleanup snag.
- **fold / atomic / SSM hazards** -- a stacked-commit fold trap, an autosquash trap,
  a state-space insight that generalizes past this diff.
- **floor / toolchain discoveries** -- the real build/lint/test command for a
  toolchain gate didn't know.

**Domain-half buckets** (about this project):
- **house conventions** -- a rule about how this project's code is written, discovered
  or reaffirmed.
- **reviewer rulings** -- a decision by a named reviewer, especially one overriding a
  prior position. Attribute it.
- **lint / CI gotchas** -- a project lint that cost a round-trip and the fix.
- **data-model / design patterns** -- a schema or architecture decision worth keeping.

**User preferences** about how the operator wants work done go to **auto-memory**
(`type: feedback` or `user`), not to either half's files.

## Phase 2: filter to what is worth keeping

Keep a candidate only if **all** hold; else drop it.

- **Durable** -- still true next month, not a fact about today's diff.
- **General** -- applies beyond the one PR. A one-off name is project trivia (the
  handoff), not a convention.
- **Novel** -- not already captured. Grep the target (the skill source, the KB, the
  project note) first. If it recurred, bump a `Seen: Nx` counter and add the new
  source rather than duplicating.
- **Non-obvious** -- would not be guessed from reading the code or existing docs.
  Terse is the house style; do not pad a skill or a KB with a weak finding.

Verify each survivor against its source before writing (read the file, re-run the
probe). A retro that adds a wrong "convention" is worse than one that adds nothing.

## Phase 3: route and apply

Apply directly -- git history and the Phase 5 report are the reversibility. The one
hard rule: when a survivor **conflicts** with an existing entry, flag the conflict
for the operator; never silently overwrite.

### Skill half

For each survivor, find the skill it belongs to and route by *who owns it* -- decided
by one rule, not a hardcoded list: **is the skill's source under your `skills_root`?**
(`[retro] skills_root` in the operator config, e.g. `~/src/my-skills`.)

- **A skill you author** (source under `skills_root`): if the finding is
  **high-confidence and clearly general**, edit the skill source in place, commit in
  the repo's `atomic-changes` form, and push to `skills_repo` so it propagates.
  Otherwise -- lower confidence, or plausibly a one-project quirk -- file a proposal
  instead (see below) rather than editing.
- **A skill you do not own** (source anywhere else, another author's repo): **never
  edit it.** File a proposal only; it is upstream and theirs to change.
- **A self-tracking skill** (one that delta-tracks its own findings, e.g. review-crew):
  do not churn it. File a proposal for anything about its wiring.

**Filing a proposal.** If `[retro] proposal_cmd` is set, run it (e.g. `cd ~/.agents &&
tix add "<skill>: <change>" -p 3 -b "<finding + evidence + why general>"`). If it is
unset, or `skills_root` is unset so editing in place is impossible, **do not invent a
tracker**: record the proposed change in the Phase 4 report instead, with enough detail
to act on later. The report is always a valid destination.

### Domain half

- **Always** append the survivor to the per-project note
  `<.handoff>/retro/retro-<date>.md`, in a simple dated, sourced form. This is the
  project-local trail and happens for every project, matched or not.
- **If Phase 0 matched a `knowledge_base`**, *additionally* distill the survivor into
  that KB at its `path`, in the KB's own entry format (**Rule** / **Why** /
  **Example** / **Source** / **Seen: Nx**), in the matching section. `peer_reviewed =
  true` raises the value of these learnings (reviewed by peers) -- include readily;
  for an unreviewed source, hold a higher novelty/durability bar. Bump `Seen`
  counters on recurrence; flag genuine reversals (`Settled:` / `⚠ Tension:`) rather
  than overwriting.
- **Never** write to a KB the slug did not match. No match means project-local only.

### Commit form and hygiene

Skill edits and KB/note writes are internal tooling, so **em dashes are fine** here;
do not spend effort scrubbing them (the no-em-dash rule is for content presented to
others as the operator's own). Keep every edit in its target's existing voice and
density; do not balloon a skill or a KB with a weak finding.

## Phase 4: report

One short summary, grouped by destination: what landed where (skill edits committed,
proposals filed, project-note appends, KB entries), and what was **considered and
dropped** (so the operator can override a drop). Flag any conflicts surfaced. Then
stop -- do not re-run the gate or any other skill.

## Notes

- **No project is special.** Any project-specific destination is just a
  `knowledge_base` match in your operator config; a repo that matches nothing routes
  domain learnings to its own project note only. `handoff` and `gate` stage 13 both
  invoke this skill.
- This is the bookend to `gate`: gate spends a session doing the work; retro banks
  the lessons. Invoked as gate's stage 13, or directly at a session's end.
