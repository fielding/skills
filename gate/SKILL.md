---
name: gate
description: >-
  Move review and validation from the outer loop -- CI and human reviewers --
  to the inner loop: local, before the branch is ever shared. A
  language-agnostic, config-driven pre-submission code-gating pipeline. Runs the
  floor (build/lint/test/fmt/doc), an SSM audit, the conventions pack, optional
  mutation testing, and an AI-tells sweep against a stated intent; loops to
  green; pushes a loose branch; runs the review crew; folds findings; factors
  atomic commits once; opens the PR; runs independent label review; babysits the
  PR to merge; and retros the learnings. Every variable bit -- gate commands,
  conventions source, mutation tool, label protocol, loop limits, skips -- comes
  from the repo's AGENTS.md; the order is fixed. Use when the user says "gate
  this branch", "run the gate", "pre-submission gate", "ship-check", or "/gate".
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Skill, Agent
user-invocable: true
---

# Gate

A pre-submission gating pipeline. The point is to move review and validation
from the **outer loop** -- CI runs and human reviewers, after the branch is
shared -- into the **inner loop**: local, on a loose branch, before anyone else
sees it. By the time a PR opens, every automated and crew round has already run
and the diff is factored into atomic commits. The reviewers see clean work, not
a draft.

This skill does not write the feature. It assumes the change is already on a
branch -- freshly implemented, or rebased and adjusted onto a moved base. The
first deterministic action is the preflight check that gate's companion skills
are installed; then intent; then the floor.

## Two stances that define this flow

**The expensive steps happen once.** The PR is not opened, and the diff is not
factored into atomic commits, until every automated and crew round is clean.
Everything before that runs against a loose working branch. Opening a PR early
invites bot and human review churn on work that is still moving; splitting
commits early means re-splitting after every finding. Both are deferred on
purpose.

**Fixed order, configurable commands.** The *sequence* of stages is the
discipline and never changes. The *commands*, *limits*, and *skips* are
configuration, read from the repo. You cannot reorder the gate; you can tell it
what `build` means for this repo, how many rounds the floor loops, and which
stages to skip on a given run. This is the no-mistakes stance: the pipeline is
fixed so a tired operator cannot skip the floor by accident, but it is not
hardcoded to one repo's toolchain.

## Execution discipline: invoke, don't paraphrase

The pipeline marks stages ★ (calls another skill) and ⚙ (config-driven). Those
marks are binding, not decorative. The failure mode this section exists to kill is
*doing a rough version of a stage from memory instead of running it* -- auditing
"for SSM principles" without loading `state-space-minimization`, grepping for em
dashes instead of running `scrub-ai-tells`, eyeballing a commit message instead of
applying `atomic-changes`. That is how a gate silently becomes theater.

- **★ is a Skill-tool invocation.** Load the named skill and follow *it*. Do not
  reproduce its guidance from memory, and do not substitute an ad-hoc shortcut for
  the skill. If the skill's action turns out to be a no-op for this diff, still load
  it, apply its check, and record that it found nothing -- never skip the load. For the
  audit stages (2, 3, 5) that load happens inside the stage's finding subagent (see
  *Audit stages run the find in a subagent*), not on the main thread; the rule is
  unchanged, only where the skill loads.
- **A `bash` block runs verbatim.** Adapt only the bracketed `<placeholders>` and
  config-resolved values; do not run an approximation of the command.
- **Record each stage as you finish it:** the stage, whether you invoked a skill
  (which one) or ran a command (which), and the one-line outcome. That per-stage
  ledger is the run's audit trail and the closing summary table is built from it. A
  stage with no recorded skill-invocation-or-command did not actually run -- treat
  its result as unproven.

## Configuration: two layers, project and operator

Gate is **not** wired to any one project. It resolves its variable behavior from two
layers, both documented in **`references/config.md`**:

- **Project layer** -- the repo's `AGENTS.md` (root + any nested one for the module
  you touched): gate commands, conventions source, mutation tool, label protocol,
  reviewer notes, loop max-rounds, skip defaults. Shared, committed, benefits every
  contributor.
- **Operator layer** -- `~/.config/gate/config.toml`, personal and local-only: the
  retro knowledge-base routing keyed by repo remote slug. This is kept *out* of the
  repo on purpose, so personal routing never pollutes a multi-contributor AGENTS.md.

Read `references/config.md` once at the start of a run, resolve every variable bit
from both layers, and refer back whenever a stage says "from config." If the repo
has no AGENTS.md, gate falls back to language detection (below) and conservative
defaults, and tells the user what it assumed; if there is no operator config, domain
retro simply stays project-local.

## Language detection

The detected language drives three config resolutions: which **conventions pack**
stage 3 loads, the default **gate commands** for the floor, and the default
**mutation tool**. Detect from the manifest / file mix:

- `Cargo.toml` / `*.rs` -> Rust -> `rust-conventions` pack, cargo floor,
  `cargo-mutants`.
- `package.json` / `tsconfig.json` / `*.ts` -> TypeScript -> (ts pack, planned),
  npm/pnpm floor, Stryker.
- `pyproject.toml` / `*.py` -> Python -> (py pack, planned), pytest/ruff floor,
  mutmut.

A repo's AGENTS.md gate config always overrides detection. Detection is the
fallback when config is silent.

## `gate init`: scaffold the project layer

A separate **mode**, not a pipeline stage. Run in a repo, `gate init` writes a
starting `## Gate` config block into the repo's **AGENTS.md** (the project layer; see
`references/config.md`), so a new repo does not hand-author its gate config from
scratch.

1. **Detect** -- use language detection (above) to resolve the floor commands,
   conventions pack, and mutation tool; read any existing AGENTS.md.
2. **Generate** a `## Gate` block: the detected floor commands, the conventions
   source, the mutation toggle (off by default), a *commented* label-protocol
   placeholder (gate skips stage 11 without one), and loop max-rounds (floor,
   crew+fold, `ci-max-rounds`).
3. **Propose, then apply.** AGENTS.md is committed and shared, so show the generated
   block -- or a diff against an existing `## Gate` section -- and apply only on
   confirmation. Never a silent write. **Idempotent:** a re-run augments missing keys
   and never clobbers a value already set.

`gate init` touches only the project layer. The operator layer
(`~/.config/gate/config.toml`) is personal and is never written by init.

## Run controls

- **Disposable worktree.** Run the whole pipeline in a disposable worktree so the
  working tree stays clean and a crash leaves nothing half-applied. The backend,
  lifecycle, and the cleanup safety rule are specified in "Worktree backend" below.
- **Early-exit on empty diff.** After the optional rebase, if there is nothing to
  gate (`git diff <base>...HEAD` is empty), bail with a note. Nothing downstream
  has anything to act on.
- **Per-run `--skip <stages>`.** A run may skip named stages (`--skip mutation,hygiene`).
  Skips are per-run on top of the config skip-defaults. You cannot skip the floor
  or intent.
- **Configurable loops.** Two loop points each take a `max-rounds` from config:
  the floor loop (stages 1-5) and the crew+fold loop (stages 7-8). See those
  stages.
- **Progress display.** If the agent has a task/todo list (e.g. Claude Code's
  `TaskCreate`/`TaskUpdate`), seed it at preflight with one task per stage that will
  run -- preflight, intent, the floor, ... retro -- and flip each to `in_progress`
  then `completed` as you go. The harness renders this as a live checklist, so the
  operator watches the gates complete in real time. Skip a stage -> mark its task
  cancelled, not silently dropped. Agents without a task list fall back to a printed
  stage table at each checkpoint.

## Worktree backend (the disposable run tree)

Gate runs the whole pipeline in a disposable worktree. Two backends, picked by
availability, with an identical lifecycle. This is gate's own outer worktree;
review-crew still worktrees its own reviewers inside it.

**Preferred: `treehouse`** -- a pre-warmed worktree pool, so the build cache stays
hot across runs (it matters: the floor re-runs every loop round). If `treehouse` is
on PATH:

```bash
wt="$(treehouse get --lease --lease-holder gate)"   # durable lease; prints ONLY the path
cd "$wt" && git fetch --quiet origin
git checkout --detach <branch>                      # detached at the branch tip
```

The detach matters: `<branch>` is usually checked out in your main tree, and git
forbids the same branch in two worktrees. Work proceeds detached and **pushes go to
`HEAD:<branch>`** -- read the push commands in stages 6/9/10 that way (e.g.
`git push -u origin HEAD:<branch>`, `git push --force-with-lease origin HEAD:<branch>`).

**Fallback: plain `git worktree`** -- no warm pool, always available:

```bash
wt="$(git rev-parse --show-toplevel)/../.gate-wt-<branch>"
git worktree add --detach "$wt" <branch> && cd "$wt"
```

**Cleanup -- the sharp edge: never discard un-pushed work.**

- **Clean finish** (stage 6 has pushed, so the work is on the remote): release the
  tree. treehouse: `treehouse return "$wt" --force`. git: `git worktree remove "$wt"`.
- **Crash before stage 6** (the work lives only in the tree): **leave it.** Never
  `return --force` / `worktree remove --force` a dirty tree -- that throws away the
  only copy. Surface the path so it can be salvaged or released by hand. (A `--lease`d
  treehouse tree is prune-protected, so it will not vanish on its own.)
- **Reap stragglers at run start**, safely: `treehouse prune` (dry-run by default;
  leased trees protected) or `git worktree prune`. A prior gate tree that is now clean
  (its work was pushed) may be released; a dirty one is surfaced, never auto-released.

## Finding ledger

Findings from the **non-crew** stages -- floor, SSM, conventions, mutation, hygiene,
and the stage-12 babysit fixes -- are recorded in a per-branch ledger, so a loop pass
or a re-invocation does not re-litigate what was already settled. (review-crew tracks
its own findings; the ledger covers the stages that do not.)

- **Location:** `/tmp/<branch>-gate-ledger.md` -- per-branch, survives the worktree
  teardown, same convention as `intent.md`.
- **Each entry:** the stage, the finding, its disposition (**fixed / dismissed /
  deferred**), a one-line rationale, and a commit or ticket ref where one applies.
- **Read it first** at the start of each loop pass and on re-invocation: do not
  re-raise a `dismissed` finding unless the code it concerned has since changed.
  Append new dispositions as you go.

The ledger is gate's working memory and its audit trail -- "here is everything gate
considered, and why." A dismissed finding is never silent; it is a ledger line. This
is what makes the floor loop (1-5) and the crew+fold loop (7-8) converge instead of
rediscovering the same findings each pass.

## Audit stages run the find in a subagent

Stages 2 (SSM), 3 (conventions), and 5 (hygiene) are **audits**: the skill each calls
produces findings, it does not edit the tree. That is the skills' own contract --
`state-space-minimization`, the conventions packs, and `scrub-ai-tells` all emit
findings and stop; applying is gate's job, not theirs. So split each stage into a find
half and an apply half:

- **Find -- in a subagent (`Agent` tool).** Spawn one subagent for the stage. Hand it
  `intent.md`, the diff (`git --no-pager diff <base>...HEAD`), and the resolved inputs
  the stage names below. Instruct it to load the named skill via its own Skill tool, run
  that skill's audit, and **return findings only** -- a structured list of `file:line`,
  the finding, and a suggested change. It makes no edits.
- **Apply -- on the main thread.** Take the returned findings through the disposition
  loop already defined above: read the ledger, restate each finding, confirm it with
  evidence (read the code, run a probe), apply if valid, record the disposition, and
  re-run the floor after each batch.

Why the split. Because the skill only finds, applying is gate's job either way; keeping
apply and the floor re-runs on the main thread keeps the orchestrator in control of the
working tree and the loop. The subagent is for the finding, where a clean context with
no stake in the code the main thread just wrote or fixed buys the same independence
stage 7 gets from the crew, applied to the cheaper audits, and without piling each
skill's load and probes into the main context. If the agent cannot spawn subagents, run
the audit inline on the main thread and note the lost independence, the same fallback
posture as stage 7.

## Running against an existing open PR

A common entry point: the branch already has an open PR and you are gating it in
place (rather than building toward a fresh PR). The stage *order* is unchanged and
nothing here is hand-waved -- detect the mode deterministically, then apply the
per-stage deltas below. Stages not listed run exactly as written.

**Detect.** Resolve the PR for the branch and capture its state up front:

```bash
gh pr view <branch-or-pr> --json number,state,baseRefName,headRefName,reviewDecision,labels,url
```

An `OPEN` PR for the branch puts you in this mode. Record the number, base, labels,
and review state; they drive the deltas.

**Per-stage deltas:**

- **Stage 0 intent** -- reconcile with the existing PR, do not author intent as if it
  has no stated purpose. Read the current title/body (`gh pr view <pr> --json title,body`)
  and fold it into `intent.md`. If they diverge, the PR body is a claim to reconcile,
  not ignore.
- **Stage 6 push** -- the branch is already pushed and the PR exists, so there is no
  loose-branch-without-a-PR to create. The "expensive once" stance is partly moot (the
  PR is already public), so still do every inner-loop round locally and push **once per
  clean round, not per fix**, to keep bot/human churn down.
- **Stage 7 crew** -- run in PR mode against the number so the crew gets PR context:
  `... review <owner/repo> <pr> --description-file /tmp/<branch>-intent.md --no-post`.
- **Stage 9 atomic commits -- CONDITIONAL on review activity.** Force-pushing rewritten
  history onto a PR that already has review threads detaches them and re-triggers bots.
  So check first, deterministically:

  ```bash
  pr=<pr#>; repo=<owner/repo>
  reviews=$(gh pr view "$pr" --repo "$repo" --json reviews -q '.reviews | length' 2>/dev/null || echo 0)
  threads=$(gh api "repos/$repo/pulls/$pr/comments" -q 'length' 2>/dev/null || echo 0)
  if [ "${reviews:-0}" -gt 0 ] || [ "${threads:-0}" -gt 0 ]; then
    echo "ACTIVITY ($reviews reviews, $threads inline threads) -> append fixup commits, defer the atomic split"
  else
    echo "CLEAN -> atomic re-factor + force-with-lease"
  fi
  ```

  - **CLEAN** (no submitted reviews, no inline threads) -> factor into atomic commits and
    `git push --force-with-lease` as normal. Nothing to detach.
  - **ACTIVITY present** -> do **not** rewrite history. Append the gate's fixes as fixup
    commits on the existing branch and **defer the atomic split** (record a follow-up
    ticket; leave the existing commit structure intact). Preserving live review threads
    outranks a clean history on a PR people are already reviewing.

  Either branch: re-run stage 11 after the push, since any push stales the labels.
- **Stage 10 open PR** -- do **not** `gh pr create`; the PR exists. If intent materially
  diverged from the PR body, rewrite the body with **`voice`** + **`scrub-ai-tells`** and
  `gh pr edit <pr> --body-file <voiced>.md`; otherwise leave the body untouched. The
  presentation pass fires only when you are actually changing the body.
- **Stage 11 labels** -- this is the *common* path here: the PR already carries labels and
  every gate push stales them. Strip, re-review the new head SHA, re-add only on a clean
  review.

---

## The pipeline

★ = calls another skill. ⚙ = config-driven from the repo's AGENTS.md.

### Stage preflight: verify the toolchain ⚙

Gate orchestrates other skills. Before any work, confirm every skill the run will
invoke is actually installed -- a missing companion otherwise fails mid-run with
an opaque Skill-tool error, after the floor has already churned. This check is
fast and deterministic; it is the very first thing gate does, before the optional
rebase, and it cannot be skipped.

**1. Resolve which stages will run.** Apply the config skip-defaults and this
run's `--skip` (intent and the floor always run). A skill is only required if the
stage that calls it will run.

**2. Required skills** -- each is invoked by a stage that will run:

| Skill | Used by | When required |
|-------|---------|---------------|
| `intent` | stage 0 | always |
| `state-space-minimization` | stage 2 | unless skipped |
| conventions pack | stage 3 | the pack for the **detected language** (below) |
| `scrub-ai-tells` | stages 5, 10 | always (stage 10 runs even if 5 is skipped) |
| `atomic-changes`, `git-factor` | stage 9 | always |
| `voice` | stage 10 | always |

**3. Conditional skills** -- check only when relevant; **warn, do not abort**:

- **Conventions pack** -- only the detected language's pack is required. Rust ->
  `rust-conventions` (hard-required). TypeScript/Python -> the pack is *planned*;
  if absent, warn that stage 3's language layer is skipped (SSM + repo AGENTS.md
  still apply) and continue.
- **`code-review`** -- only if the repo's AGENTS.md declares a label protocol
  (stage 11). This is the **repo's** code-review skill, checked in the repo, not
  the global store. No protocol -> stage 11 skipped -> not required.
- **`review-crew`** -- stage 7's *premium* implementation, not required, and probed
  differently from the others: the store holds only its `SKILL.md` wrapper, while stage
  7 runs the uv project that wrapper points at. Probe that project now so a broken
  Implementation A surfaces here, not as an intermittent stage-7 fallback:

  ```bash
  store="${SKILLS_DIR:-$HOME/.agents/skills}"
  rc_path=$(grep -oE '`[^`]*/[^`]*review-crew`' "$store/review-crew/SKILL.md" 2>/dev/null | head -1 | tr -d '`')
  rc_path="${rc_path/#\~/$HOME}"
  if [ -n "$rc_path" ] && [ -f "$rc_path/pyproject.toml" ]; then
    echo "review-crew: runnable project at $rc_path -- stage 7 uses the real crew (A)"
  else
    echo "review-crew: no runnable uv project -- stage 7 uses the built-in panel (B)"
  fi
  ```

  If it reports the built-in panel while you expected the crew, fix the install before
  running; the crew is the point of the stage. Either way, never *block* the run on
  review-crew.
- **`retro`** -- stage 13, post-merge, built separately. If absent, warn that the
  retro stage will be skipped; never block a run on it.

**4. Run the check -- this Bash *is* the gate, not a fallback.** Do not decide
"the skills look available" from your loaded-skill list: that list only contains
skills already invoked this session, so it cannot confirm a companion gate has not
called yet. Run the check below verbatim. It probes the store on disk and prints
the exact install line for anything missing, resolving each skill's source repo
from the lockfile:

```bash
store="${SKILLS_DIR:-$HOME/.agents/skills}"
lock="$HOME/.agents/.skill-lock.json"
# always-on companions + the detected language's pack (rust-conventions for Rust).
# set -- + for s in "$@" word-splits correctly in BOTH bash and zsh (an unquoted
# $var does NOT split under zsh -- do not regress to `for s in $required`).
set -- intent state-space-minimization scrub-ai-tells atomic-changes git-factor voice rust-conventions
missing=""; lines=""
for s in "$@"; do
  if [ ! -e "$store/$s" ]; then
    missing="$missing $s"
    src=$(grep -A4 "\"$s\"" "$lock" 2>/dev/null | grep -m1 '"source"' | sed -E 's/.*: *"([^"]+)".*/\1/')
    lines="$lines
  npx skills add ${src:-<source-repo>} -s $s -g -y"
  fi
done
if [ -z "$missing" ]; then
  echo "Preflight OK -- all required skills present."
else
  echo "Gate is missing required skills:$missing"
  printf '%s\n' "$lines"
fi
```

**Do not auto-install.** Skills run with full agent permissions, so installing one
is the user's call. If anything required is missing, **STOP before stage pre**,
surface the missing set and the commands, and let the user install and re-run.
Once green, proceed. (If the operator keeps a `skill-bundle` manifest,
`skill-bundle verify gate` is the same check and `skill-bundle install gate`
installs the whole set in one shot -- but the decision to install stays theirs.)

### Stage pre (optional): rebase and reconcile

Only if a parent merged or the base moved. Cherry-pick the branch onto the new
base (see **Stack rebase mechanics** in `references/fold-mechanics.md`), reconcile
paths and signatures the merged parent altered, then continue. Skip when the
branch is already based correctly. After this, run the empty-diff early-exit
check.

### Stage 0: intent ★

Invoke the **`intent`** skill. It reads the recent agent transcript(s) for this
change and writes a plain, factual `intent.md` to a stable per-branch path
(`/tmp/<branch>-intent.md`). The file leads with `Intent: <one-liner>` and then
What / Why / Scope (in + out-with-rationale) / Decisions.

This is **plain context, not prose**. It is NOT voiced or scrubbed here -- that
is stage 10's job. The one-liner and the `## Why` heading matter downstream:
review-crew (stage 7) extracts them verbatim, and the fold (stage 8) triages
findings against the stated Scope and Decisions. Thread `intent.md` as context
into every stage that reasons about purpose.

### Stage 1: the floor ⚙

The floor: build, lint, test, format-check, doc. Nothing downstream matters until
it is green. The commands come from config (the repo's AGENTS.md gate keys; see
`references/config.md`), defaulting to the detected language's toolchain. For a
Rust repo with the usual aliases, for instance:

```bash
<build> && <lint> && <test> && <fmt-check> && <doc>
```

Fix failures, re-run, continue. (The stage is named "the floor," not "the gate,"
so the pipeline and its first stage do not share a name.)

### Stage 2: SSM audit ★

Run the **`state-space-minimization`** audit in a finding subagent (see *Audit stages
run the find in a subagent*): hand it `intent.md` and the diff, have it load the skill
and return SSM's findings. Do not audit "for SSM principles" from memory. Then, on the
main thread, work the returned findings: restate each, confirm with evidence (read the
code, run a probe), apply if valid, re-run the floor after each batch.

SSM carries the language-agnostic state-shrinking principles (parse-don't-validate,
drop speculative tolerance, validate at the boundary, no dead or speculative code), so
the conventions stage does not restate them. Common hits: speculative tolerance,
defensive code on type-guaranteed invariants, validation in the wrong layer, public
surface wider than callers need.

### Stage 3: conventions ⚙★

Conventions are **distributed across three layers**, which keeps gate itself
language- and project-free:

1. **General principles** -- already carried by SSM (stage 2).
2. **Language idiom** -- the conventions pack for the detected language:
   **`rust-conventions`** for Rust; the TypeScript and Python packs are planned.
   The pack states the general principles in the language's idiom plus the
   language-specific mechanisms (e.g. for Rust: `.expect` over `.unwrap`,
   associated types over boxed jokers, the clippy restriction-lint gotchas).
3. **Project specifics** -- the repo's **AGENTS.md** (root + the nested one for the
   module you touched), located via the conventions-source key in config. This is where
   a project's own conventions, crates, naming, and reviewer expectations live.

Run the conventions audit in a finding subagent (see *Audit stages run the find in a
subagent*): hand it `intent.md`, the diff, the language-pack name, and the
conventions-source path, and have it load the pack via its Skill tool, read the named
AGENTS.md files, and return findings where the diff violates layer 2 or 3. Where the
language pack and the repo AGENTS.md disagree, the repo wins (it has declared its own
rules). Then apply the returned findings on the main thread as in stage 2.

### Stage 4: mutation testing ⚙

Optional, config-toggle (heavy; off unless config or `--skip`'s inverse enables
it). Run the language's mutation tool from config (`cargo-mutants` / Stryker /
mutmut) against the changed files. Record caught / unviable / missed / timeout.
Fix every survivor by adding a distinguishing test or simplifying the source. Two
patterns recur: error-path invariants survive when every boundary mock is
infallible (add a deliberately-failing impl to drive the `Err` branch); loop
stop-conditions survive or hang under a `==` flip (drive the failing path AND
wrap the loop in a timeout so a broken early-return trips the deadline). For thin
wrappers, near-zero viable mutants is the expected signal, not a gap. Mutation
testing is "better than nothing," not proof of correctness.

### Stage 5: hygiene sweep ★

Config-toggle. Run the **`scrub-ai-tells`** audit on the **code diff** in a finding
subagent (see *Audit stages run the find in a subagent*): hand it the diff and have it
load the skill and return the tells it finds -- em dashes, AI-tell filler in code,
comments, or test names. The grep below is a pre-filter for the loudest tell, *not* the
stage: a clean grep does not discharge the stage, the subagent still loads and runs
`scrub-ai-tells` itself.

```bash
git --no-pager diff <base>...HEAD | grep -nE "—|–"
```

Apply the returned fixes on the main thread, then re-check. This must be empty here
(and later on the PR body and commit messages). This is the *code* hygiene pass; the
*presentation* scrub (the PR body) rides with voice at stage 10.

> **[LOOP 1-5 until green, capped at the floor `max-rounds` from config.]**
> Run the floor through the hygiene sweep, apply fixes, re-run from the floor.
> Each pass should converge; if it hits the configured cap still dirty, stop and
> surface what is still failing rather than looping forever.

### Stage 6: push the loose branch (no PR)

```bash
git add <explicit paths> && git commit -m "wip: <summary>"   # loose; atomic split is stage 9
git push -u origin <branch>
```

Pushing is what lets the crew branch its worktrees off the remote ref. **No PR is
opened**, so the PR review bots and the humans are not involved yet. (Beware
`git add -A` -- it sweeps untracked tool-artifact trees into the commit; stage
explicit paths and keep artifact dirs in `.gitignore`.)

### Stage 7: adversarial review ★

The point of this stage is an **independent, adversarial review** of the pushed diff
against `intent.md`, producing findings and a verdict on the ladder **MERGE >
APPROVE_WITH_NOTES > BLOCK**. The value is cross-reviewer diversity (a second
perspective catches what the first is blind to) and *disagreement as signal* (where
reviewers conflict is where to dig). Two implementations; **the choice is decided by the
probe below, never by feel.** Either way the output is findings + a verdict, so stage 8
(fold) is unchanged.

**Pick the implementation deterministically.** review-crew is not auto-loaded, so its
absence from your loaded-skill list means nothing; do not decide from that list. Run this
probe. It resolves the crew's uv project from the path the installed review-crew skill
declares (the single source of truth) and confirms it is runnable:

```bash
store="${SKILLS_DIR:-$HOME/.agents/skills}"
rc_path=$(grep -oE '`[^`]*/[^`]*review-crew`' "$store/review-crew/SKILL.md" 2>/dev/null | head -1 | tr -d '`')
rc_path="${rc_path/#\~/$HOME}"
if [ -n "$rc_path" ] && [ -f "$rc_path/pyproject.toml" ]; then
  echo "REVIEW_CREW=$rc_path"
else
  echo "REVIEW_CREW=ABSENT"
fi
```

- **`REVIEW_CREW=<path>`** -> **Implementation A**, using `<path>` as the `--project`
  value. This is the expected case whenever review-crew is installed.
- **`REVIEW_CREW=ABSENT`** -> **Implementation B**.

Once the probe selects A, a `uv run` failure is a hard error to fix and surface, **not** a
reason to switch to B. Falling back to B is only ever correct when the probe printed
`ABSENT`; a silent downgrade on a runnable install is the exact failure this stage exists
to prevent.

**Implementation A -- `review-crew`** (the full adversarial debate; selected when the
probe prints `REVIEW_CREW=<path>`). Load **`review-crew`** for the invocation details and
run it in branch mode against the branch you pushed, using the probe's `<path>` as
`--project` and passing `intent.md` as the description file:

```bash
uv run --project <path> review \
       --branch <branch> --repo <owner/repo> --base <base> \
       --description-file /tmp/<branch>-intent.md --no-post
```

review-crew has its own intent system: it scans the description file for an
`Intent:`/`Goal:`/`Purpose:` line or a `## Why` heading and, finding one, uses it
**verbatim** at high confidence -- which short-circuits its model extractor and runs
intent-alignment against *our* stated intent. That is why stage 0 leads with `Intent:`
and a `## Why`. So:

- **Pass `intent.md` via `--description-file`.** Do it.
- **Do NOT use `--intent-extractor-cmd`.** The verbatim match preempts it.
- `--instruct` is optional per-run reviewer *steering*, not the intent path.
- review-crew auto-loads the repo's own review guidance (`REVIEW.md`, `.review-crew.md`,
  `CLAUDE.md`, vendored code-review), so project conventions reach the reviewers.

The verdict + findings live in `pr-comment.md` (the `review.json` `findings` array is
often empty). It runs in the background for minutes; watch for the session dir.

**Implementation B -- built-in review panel** (the portable fallback; selected only when
the probe printed `REVIEW_CREW=ABSENT`). First, say so plainly -- print:

> ⓘ review-crew not found -- running a built-in subagent review panel instead.
>   (The full adversarial review crew is coming soon.)

Then run the panel described in **`references/review-panel.md`** (loaded only on this
fallback path): an independent set of subagent reviewers -- distinct lenses, distinct
models where available -- over the diff + `intent.md`, reconciled into findings + a
verdict on the same ladder. That output feeds stage 8 exactly like review-crew's.

If the agent cannot spawn subagents at all, **skip this stage with a loud note** that
the adversarial pass did not run -- never silently.

### Stage 8: fold the findings

Triage every finding **evidence-first**, with `intent.md` as the reference. Three
tiers (the no-mistakes classification):

- **auto-fix** -- a clear, low-risk correction the evidence supports: apply it,
  re-gate (re-run the floor + mutants on the affected area).
- **ask-user** -- a finding that conflicts with a stated Decision or Scope-Out, or
  is a genuine judgment call: surface it with the evidence and the intent
  reference; let the user rule.
- **block** -- a correctness or safety problem: must be fixed before proceeding.

A dismissed finding gets a one-line rationale (and a tracked ticket if deferred),
never silence -- record every disposition in the finding ledger so the next crew+fold
round does not re-raise it. Because there is no PR yet, you are amending the loose
branch, not rebuilding atomic commits.

> **[LOOP 7-8 as one unit, for the crew+fold `max-rounds` from config.]**
> crew -> fold -> re-run crew to confirm a BLOCK clears. Default one round; config
> may raise it. The two stages move together: a fold is only proven by the next
> crew round coming back clean.

### Stage 9: atomic commits, once ★

If the branch already has an open PR, this stage is **conditional** -- see
"Running against an existing open PR"; the rest of this stage describes the
fresh-PR path.

Only now, with the crew rounds clean, factor the loose diff into atomic commits --
so the split happens exactly once instead of after every finding. Invoke
**`atomic-changes`** via the Skill tool (the canonical commit form: the closed verb
set, transformation-priority ordering, body rules) and **`git-factor`** for the
mechanical split. Load `atomic-changes` even when the diff is already one commit:
the skill verifies the message conforms (verb set, subject, body rules) -- do not
pass an existing message by eye because it "looks well-written."

The hard-won mechanics -- splitting a file's changes per commit, never resolving an
autosquash conflict by copying the final file in, verifying each commit standalone,
confirming the rebuilt tip is net-identical, and slicing the safe Remove/Fix/Refactor
commits into their own PR -- live in **`references/fold-mechanics.md`**. Read it
before factoring a stacked branch; that is where this flow bites hardest.

### Stage 10: open the PR ★

If the branch already has an open PR, **do not create one** -- see "Running against
an existing open PR" for the edit-in-place path. The rest of this stage is the
fresh-PR path.

Now turn `intent.md` into the user-facing PR body. **This is the presentation
pass** -- the first time voice and scrub touch the intent:

1. Invoke **`voice`** to rewrite `intent.md`'s What/Why into the PR body in the
   user's register.
2. Invoke **`scrub-ai-tells`** on that body (em-dash sweep included).
3. Create the PR:

```bash
git push --force-with-lease origin <branch>
gh pr create --base <base> --head <branch> --body-file <voiced-body>.md
```

For a stacked PR the base is the parent branch; switch it to the trunk once the
parent merges. The PR now exists, so the review bots auto-comment and the humans
review.

### Stage 11: independent label review ⚙★

If the repo's AGENTS.md declares a **PR label protocol** (the label names and the
gating rule come from config; gate hardcodes none), run the repo's **`code-review`**
skill from a **separate subagent**, following that protocol: strip the review label
first, gate on CI, add the label only on a clean review. The subagent reviews the
PR **head SHA in a fresh worktree**, never the authoring working tree -- that is the
independence rule. If the diff touches SQL, run the repo's `sql` skill the same way
for the SQL label. Never add a label from the main authoring session; manage each
independently. Any push after labeling stales the labels -- re-run this stage after
a stage-12 fold. (If the repo declares no label protocol, skip this stage.)

### Stage 12: babysit ⚙

Watch the PR to merge. Two feeds drive this loop -- CI checks and reviewer comments
-- and gate auto-fixes only the **mechanical** failures, surfacing everything else.

**CI watch + mechanical auto-fix.** Watch checks to green or merge
(`gh pr checks <N> --watch`). On a red check, pull the failing job's log and classify
before touching anything:

- **Mechanical** -- a lint or format failure, a clean rebase onto a moved base, an
  obviously flaky check that passes on retry. Fix it locally, **re-run the floor**
  (never push an unverified fix), push, and re-enter. A moved base means rebase via
  `references/fold-mechanics.md`, re-gate, push.
- **Non-mechanical** -- a real test failure, a logic error, or anything ambiguous.
  **Stop and surface it** with the log. Gate does not guess at logic fixes on a live
  PR.

Bounded by `ci-max-rounds` from config (default 2): if a mechanical fix has not
cleared the check within the cap, stop and surface rather than loop. Never auto-fix
in a way that overrides a human review thread.

**Reviewer comments.** Pull bot + human comments (`gh api .../pulls/<N>/comments` and
`.../issues/<N>/comments`). Triage **evidence-first**: a verbal suggestion does not
beat a lint or a settled Decision in `intent.md`; push back with evidence when
warranted. Apply, re-gate (re-run the floor), fold into the introducing commit, reply
on each thread citing the commit.

After any push: re-run stage 11 (labels stale on a push) and record every disposition
in the finding ledger. Loop until merged.

(The repo's AGENTS.md reviewer notes name the bots and the humans and what each
tends to focus on; gate hardcodes none of them.)

### Stage 13: retro ★

Post-merge, invoke the **`retro`** skill via the Skill tool. It reviews the session
for durable, general learnings and routes them in two halves: the **skill half**
folds tooling lessons back into the skills gate composed (or files a proposal), and
the **domain half** writes a per-project retro note plus -- only when your operator
config maps this repo to a knowledge base -- distills into that KB. Routing is
config-driven, so this is safe on any project; it never cross-contaminates a KB. This
closes the self-improving loop: gate sharpens its own toolset from each run.

---

## Skip semantics

A stage marked ⚙ or ★ can be skipped per-run with `--skip <stages>` or by a config
skip-default, **except** preflight, intent (stage 0), and the floor (stage 1),
which always run.
Mutation (4) and hygiene (5) are the usual config-toggled stages. Skipping a stage
inside the floor loop just shortens the loop; skipping stage 11 is right for a repo
with no label protocol.

## Out of scope (deliberately not built)

- **Forge abstraction.** gate uses `gh` (GitHub) directly. Multi-forge support was
  considered and dropped: it would be a single-backend seam today (only GitHub is
  used), which is speculative scaffolding by the same rule the pipeline enforces
  elsewhere. Revisit only with a concrete second forge in hand.
- no-mistakes' **daemon architecture** -- bare-repo gate, post-receive hook, SQLite
  state, IPC, TUI, self-update. That is its Go binary; gate is a skill and the agent
  is the executor, so none of that plumbing applies.

(The finding ledger, CI mechanical auto-fix, and `gate init` were phase-2 additions
and are documented above, not here.)

## References

- **`references/config.md`** -- the repo-AGENTS.md keys gate reads, with fallbacks.
- **`references/fold-mechanics.md`** -- the stacked-PR atomic-commit and rebase
  mechanics (the expensive-once split, per-commit slicing, standalone verification,
  the safe-layer slice into its own PR).
- **`references/review-panel.md`** -- stage 7's built-in subagent review panel, the
  portable fallback when `review-crew` is not installed (loaded only on that path).
