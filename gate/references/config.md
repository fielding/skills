# Gate configuration: two layers

Gate hardcodes no specifics. What it needs comes from two config layers, resolved
together:

1. **Project layer** -- the repository's `AGENTS.md` (root, plus the nested one for
   the module you touched). Shared and committed; benefits every contributor. Holds
   the *project's* facts: floor commands, conventions source, mutation toggle, label
   protocol, reviewers, loop limits, skip defaults. Documented under "Project facts"
   below.
2. **Operator layer** -- `~/.config/gate/config.toml`, personal to you, never in any
   repo. Holds the *operator's* routing that must not pollute a shared file -- today
   the retro knowledge-base destinations. Documented under "Operator config" below.

Where both could touch the same concern, the operator layer only ever *adds*
personal routing; it never overrides a project's declared rules.

## Operator config: ~/.config/gate/config.toml

Personal, per-operator, local-only -- never committed, not even to the public
`~/.agents`. It lives in your home, so it survives reclones and a shared repo never
sees it. It exists precisely so personal routing -- where *you* send the knowledge a
run distills -- never lands in a multi-contributor repo's `AGENTS.md`.

### Knowledge-base routing (retro, stage 13)
Which external knowledge base, if any, a run's *domain* learnings also route to,
keyed by the repo's remote slug with glob support:

```toml
[[knowledge_base]]
match = "acme/*"                                  # glob on <owner>/<repo>
path  = "~/notes/team-kb"
peer_reviewed = true                              # high-signal: peers review here
```

- gate resolves the repo's remote slug (`git remote get-url origin` -> `owner/repo`)
  and matches it against each `match` glob.
- **Match** -> retro's domain half *additionally* distills to that `path`, on top of
  the always-written `<project>/.handoff/retro/retro-<date>.md`. `peer_reviewed = true`
  marks the source as high-signal (reviewed by peers), which retro can weight.
- **No match, or no file at all** -> domain retro stays project-local only. There is
  no default external destination; absence means nothing routes out.
- One `acme/*` entry covers every team repo at once -- no per-repo setup.

### Handoff storage (handoff, retro)
Where `handoff` and `retro` store the per-project `.handoff` docs. Optional; absence
is the portable default.

```toml
[handoff]
vault_root = "~/notes/Projects"   # project notes root; unset -> repo-local .handoff/
```

- **Set** -> docs live at `<vault_root>/<proj>/handoff/` with an in-repo `.handoff`
  symlink pointing there (so they survive reclones and stay editor-/Obsidian-visible);
  bulky ancillary artifacts go one level up, to `<vault_root>/<proj>/`.
- **Unset** -> a plain gitignored `<repo>/.handoff/`, fully self-contained, no symlink.
- Whichever of `handoff`/`retro` writes first resolves this identically, so the two
  never disagree on the location.

### Skill-half routing (retro)
Where retro routes the *skill half* of a session's learnings (lessons about your own
tooling). Optional; absence makes the skill half report-only.

```toml
[retro]
skills_root  = "~/src/my-skills"     # your authored-skills tree
skills_repo  = "you/my-skills"       # where in-place skill edits get pushed
proposal_cmd = "tix add \"{title}\" -p 3 -b \"{body}\""  # how proposals file (optional)
trusted_reviewers = ["alice", "bob"] # reviewers whose direct feedback ratifies a convention (optional)
```

- **Ownership is by path, not a list.** A skill whose source sits under `skills_root`
  is yours: retro may edit it in place and push to `skills_repo`. A skill anywhere
  else is upstream: retro files a proposal, never edits.
- **`proposal_cmd`** is the command retro runs to file a lower-confidence change
  (`{title}`/`{body}` substituted). Unset -> retro records the proposal in its run
  report instead.
- **`trusted_reviewers`** gates *convention* entries (conventions-pack gaps, house
  conventions). Direct feedback from a listed reviewer clears retro's source bar
  outright: it can land as an in-place pack edit or a KB house convention. Feedback
  from anyone else, or a pattern retro merely observed, is downgraded to a proposal
  or the project note. Unset -> every convention takes the downgrade path (strictest
  default: no convention lands without a human name behind it).
- **All unset** -> retro still runs: it writes the domain note and reports proposed
  skill changes, editing nothing. That is the portable default.

The layer is where future personal routing goes, so the project layer stays
shared-clean.

## Project facts (the repo's AGENTS.md)

Gate has no required schema or parser for this layer. The repo's AGENTS.md is prose
for humans and agents both; gate reads it the way a reviewer would. The "keys" below
are the *facts* gate needs to find, not a strict format. A repo can state them
however its AGENTS.md is organized. When the repo uses a structured `## Gate`
section, follow it; otherwise infer the facts from the conventions/tooling prose.

### Floor commands (stage 1)
The build / lint / test / format-check / doc commands for this repo.
- **Look for:** a gate/CI/Makefile section, declared cargo or npm aliases, a
  "how to test" note.
- **Fallback:** the detected language's standard toolchain (Rust: `cargo build`,
  `cargo clippy`, `cargo test`, `cargo fmt --check`, `cargo doc`; TS:
  `npm run build/lint/test`; Python: `pytest` + `ruff`). Tell the user what was
  assumed.

### Conventions source (stage 3)
Where the project's own conventions live, beyond the language pack.
- **Look for:** the AGENTS.md conventions prose itself, plus any pointer it gives
  (a `code-review` references dir, a `CONVENTIONS.md`, nested AGENTS.md).
- **Fallback:** the detected language's conventions pack alone (`rust-conventions`,
  future ts/py). The repo's declared rules always override the pack.

### Mutation tool + toggle (stage 4)
Which mutation tool to run, and whether mutation runs at all.
- **Look for:** a declared mutation command, or a statement that mutation testing
  is/ isn't part of the gate.
- **Fallback:** off unless config enables it (it is heavy). When on, the detected
  language's default tool: `cargo-mutants` / Stryker / mutmut.

### Hygiene toggle (stage 5)
Whether the code-diff AI-tells sweep runs.
- **Fallback:** on. It is cheap and catches em dashes / AI filler in code and
  comments.

### Loop max-rounds (stages 1-5, 7-8, and the stage-12 CI auto-fix)
The cap on each loop point: the floor loop, the crew+fold loop, and the babysit CI
mechanical auto-fix.
- **Look for:** a declared retry/round limit in the gate section.
- **Fallback:** floor loop converges naturally (cap ~3); crew+fold defaults to 1
  round, optionally 2; `ci-max-rounds` defaults to 2 (then stop and surface).

### Skip defaults (run controls)
Stages this repo skips by default (on top of the per-run `--skip`).
- **Fallback:** none. Per-run `--skip` still applies. Intent and the floor are
  never skippable.

### Review-crew settings (stage 7)
Base branch convention, extra reviewers, repo-specific review guidance.
- **Look for:** how the repo names its trunk/base, any `REVIEW.md` /
  `.review-crew.md` (review-crew auto-loads these -- gate need not wire them).
- **Fallback:** trunk is the repo default branch; `intent.md` via
  `--description-file`; never `--intent-extractor-cmd`.

### Label protocol (stage 11)
The PR review label names and the gating rule (strip-first, CI-gate, add-on-clean),
and which diffs trigger which label (e.g. SQL diffs -> the SQL label).
- **Look for:** an explicit PR label protocol section.
- **Fallback:** **skip stage 11 entirely.** Gate invents no labels. No declared
  protocol means no label review.

### Reviewer notes (stages 8, 12)
Who reviews and what each tends to focus on, so fold/babysit can weight feedback.
- **Look for:** named reviewers and their emphases; the review-bot names the repo
  uses.
- **Fallback:** treat all findings on their evidence; no reviewer-specific
  weighting. Watch whatever bots actually comment on the PR.

## When there is no AGENTS.md

Gate falls back entirely to language detection and the conservative defaults
above, runs the language-detected floor and conventions pack, skips mutation and
the label review, and **tells the user every assumption it made** so they can
correct it or add an AGENTS.md gate section. A missing AGENTS.md weakens the gate;
it does not break it.

## The stance

Fixed stage *order*; configurable *commands*, *limits*, and *skips*. Config can
change what a stage runs, how many times a loop turns, and whether an optional
stage runs at all. Config can never reorder the pipeline or skip intent or the
floor. That is the no-mistakes discipline: the sequence is the safety property;
the values are the flexibility.
