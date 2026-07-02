# skills

A curated set of my agent skills, the ones polished enough to share. They install
across whatever agent tool I'm in front of (Claude Code, Codex, Cursor, ...) through
the [skills CLI](https://skills.sh):

```sh
skills add fielding/skills
```

Want a safety net on top of that? Install through
[`chopz`](https://github.com/fielding/chopz) (`npx @fielding/chopz`), a
zero-dependency wrapper over the same CLI that adds allowlisted bundles,
content-hash pinning, a heuristic red-flag scanner, and one-command restore. It
forwards anything it doesn't handle straight to `skills`, so it's the only command
you need. For example, `npx @fielding/chopz add fielding/skills -s gate` installs
`gate` plus its same-repo dependencies, pinned, and surfaces any cross-repo ones
for you to approve rather than pulling them silently.

Each subfolder is one skill: a `SKILL.md` the agent loads, plus any scripts it needs.
When a skill needs human setup, those notes live in its own folder.

## Skills

- **gate**: a language-agnostic, config-driven pre-submission gating pipeline. It
  pulls review and validation out of the outer loop (CI, the humans waiting on a PR)
  and into the inner loop: local, before the branch ever leaves your machine. Runs
  the floor (build/lint/test/fmt/doc), an SSM audit, the conventions pack, optional
  mutation testing, and an AI-tells sweep against a stated intent; loops to green;
  runs a review crew; folds findings; factors atomic commits once; opens the PR; and
  babysits it to merge.
- **anti-slop**: a fast first-pass reality check on an unfamiliar codebase: is this
  real software, or a confident-looking mirage? Fans out per-topic subagents over a
  3-layer engine (universal checks → language pack → optional domain pack), normalizes
  severity, and produces a one-page VERDICT with a 0-100 Substance Score and go/no-go.
  Great for vetting vibe-coded / LLM-generated repos before you trust them.
- **intent**: capture the intent of a change as plain, factual context (What / Why /
  Scope / Decisions). Stage 0 of `gate`; downstream stages review against it, and it
  becomes the PR body.
- **retro**: end-of-session self-improvement: distill durable, general learnings and
  route them (tooling lessons back into your skills; project knowledge to a per-project
  note and, optionally, a configured knowledge base). Config-driven, so it runs on any
  project without cross-contaminating a KB.
- **handoff**: write the project state a fresh agent needs to pick up where the last
  one left off. STATUS / DECISIONS / CONTEXT / NEXT into a `.handoff/` dir. Portable by
  default; point it at a notes vault if you keep one.
- **rust-conventions**: a Rust idiom pack (the general principles in Rust's idiom plus
  the language-specific mechanisms). Loaded by `gate`'s conventions stage; useful on its
  own.
- **scrub-ai-tells**: strip the AI-tell filler (em dashes, hedging, telltale phrasing)
  from prose, code, comments, and test names.
- **skill-distill**: mine your agent session history (Claude Code, Codex, pi, Cursor)
  for the workflows you keep doing by hand, the ones worth promoting into a real skill.
- **tix**: command reference and workflow for the [`tix`](https://github.com/fielding/tix)
  issue tracker (per-repo `.tix/` stores). The reference behind a "use tix in every repo"
  habit.
- **tutor**: teach yourself (or be taught) a codebase, change, or concept *properly*:
  problem-first, incremental, verified at every step against a written Understanding
  Checklist. Not a one-shot explanation. A session that ends when you can explain it back.
- **typescript-conventions**: a TypeScript idiom pack (the general principles in
  TypeScript's idiom plus the language-specific mechanisms). Loaded by `gate`'s
  conventions stage for TS repos; useful on its own.

## Configuration

`gate`, `retro`, and `handoff` are config-driven. They share an optional operator
config at `~/.config/gate/config.toml` (personal, local, never committed) where
you point `retro` at a knowledge base, set a notes-vault root for `handoff`, and the
like. (Yes, the file lives under `gate/` even though the other two read it too; it's
the shared operator layer.)

None of it is required. The skills fall back to portable defaults when it's
absent. The full schema, including both the per-repo `AGENTS.md` project layer and
this operator layer, is in
[`gate/references/config.md`](gate/references/config.md).

## Companions not in this repo

`gate` composes a few skills that live elsewhere:

- **dkubb's** `atomic-changes`, `state-space-minimization`, and `git-factor`: install
  from [his repos](https://github.com/dkubb/skills). They're load-bearing in how I
  commit and shrink state.
- **review-crew**: the adversarial multi-model reviewer `gate`'s stage 7 prefers.
  **Coming soon** (the script isn't public yet). Until then, `gate` falls back to a
  built-in subagent review panel that captures the core value (multiple independent
  reviewers, with disagreement treated as signal) so the stage still runs.
- a personal **voice** skill is also separate and not included here. `gate` degrades
  gracefully without these. Its preflight tells you what's missing rather than failing
  mid-run.

## License

MIT. See [LICENSE](LICENSE).
