---
name: handoff
description: Document current project state for seamless agent handoff. Use when the user says "handoff", "document this", "prepare for handoff", "save context", "write it down", "update the project docs", "pretend the power went out", "prepare for another agent", or when a significant chunk of work is done and the user wants to preserve context. Also trigger when the user says "what were we doing" or "catch me up" to READ existing handoff docs.
allowed-tools: Bash, Read, Edit, Write, Grep, Glob
---

# Handoff

Create and maintain project documentation that lets any agent (or the same agent
after context loss) pick up work instantly. The framing: the power went out and we
lost all context -- what does the next agent need to not start from zero?

## Storage: resolve the handoff location

The handoff docs live in a `.handoff` location that resolves the same way every time,
portable by default and personal only when you opt in. Resolve it before reading or
writing anything:

1. **`.handoff` already exists** (symlink or dir) -> use it as-is. This is the common
   path; no config read, no setup. Follow a symlink to its target.
2. **`.handoff` does not exist** -> derive the project name, then create it:
   - **Project name:** `git remote get-url origin` -> the repo name (e.g.
     `git@github.com:owner/widget.git` -> `widget`). Fallback: the current
     directory's basename.
   - Read `vault_root` from the operator config (`~/.config/gate/config.toml`, the
     shared operator layer; `[handoff]` section). Then:
     - **`vault_root` set** (e.g. `~/notes/Projects`): the docs live outside the repo
       so they survive reclones. Create `<vault_root>/<proj>/handoff/`, symlink
       `.handoff` -> there, and gitignore `.handoff`.
     - **`vault_root` unset** (the portable default): create a plain `<repo>/.handoff/`
       and gitignore it. No symlink -- the docs already sit in the repo.

The symlink is not a feature to manage; it is simply what "docs stored outside the
repo" looks like from inside the repo. A public user with no config gets a clean,
self-contained `.handoff/` and never touches a vault or a symlink.

```toml
# ~/.config/gate/config.toml  (personal, local-only, never committed)
[handoff]
# Where project notes live. Set -> docs at <vault_root>/<proj>/handoff/ with an
# in-repo .handoff symlink; ancillary artifacts go to <vault_root>/<proj>/.
# Unset -> a plain gitignored <repo>/.handoff/. That is the whole personalization.
vault_root = "~/notes/Projects"
```

## What it produces

The resolved `.handoff` holds the canonical cold-start docs at its **top level**, and
nothing else. Keep these four lean and scannable:

- **STATUS.md** -- current state only: what's done, in progress, blocked, as of right
  now. Not a changelog. Rewrite it each handoff; do not append. If it has grown a
  history, cut the dead state or move it to `archive/`.
- **DECISIONS.md** -- architectural and design decisions: what was chosen, what was
  rejected, why. The things that aren't obvious from reading the code.
- **CONTEXT.md** -- domain knowledge, gotchas, environment quirks. Stuff that would
  cost an agent several rounds of exploration to rediscover (e.g. "zig 0.15 removed
  usingnamespace", "libgit2 is system-linked, not vendored").
- **NEXT.md** -- the next actions, each with enough context (and the WHY) that a
  cold-start agent can execute it without asking. This is the **seed** for whatever
  issue tracker the project uses: on resume, an agent converts these into tickets per
  the project's own `AGENTS.md`. Handoff just writes the list; the tracker is
  downstream and not handoff's concern.

### Keep the top level clean

Only the four files above (plus retro's `retro/` subdir) belong at the top level.
Everything bulkier -- deep research, audits, runbooks, vote tallies, patches -- is
history or ancillary, not cold-start material. Route it:
- **`vault_root` set:** to the project notes root, `<vault_root>/<proj>/` (one level
  up from `handoff/`).
- **`vault_root` unset:** to a clearly separated subdir (`.handoff/notes/`,
  `.handoff/archive/`), never mixed in with the four canonical files.

### Sync targets

If any of these exist at the repo root, update them with conventions or instructions
discovered during the work: `AGENTS.md` (the cross-tool standard), `CLAUDE.md`,
`.cursorrules` / `.cursor/rules`, `COPILOT.md`. These are instructions *to* agents and
are committed; the handoff docs are state *from* agents and are gitignored. Keep them
distinct.

## How to write handoff docs

Write like you're leaving notes for a sharp coworker with zero context on today.
Specific and concrete.

Bad: "We worked on the build system."
Good: "Moved from a shell wrapper to native Zig+libgit2. Zig 0.15.2 breaks vs 0.14:
no usingnamespace, File.stdout().writer() needs a buffer param, ArrayList.init() API
changed. libgit2 is system-linked (brew install libgit2)."

Two rules that keep the docs trustworthy:

- **Reference, don't duplicate.** If something already lives in a PR, a commit, a
  diff, an issue, or an ADR, link it by path or URL instead of restating it. The code
  and git history are the source of truth for implementation detail.
- **Redact secrets.** Never write API keys, tokens, passwords, or private env values
  into these docs. Name the variable, not its value.

Keep each canonical file under ~100 lines. Past that you're capturing detail the code
already carries. Rewrite to stay lean rather than letting a file accrete.

## When invoked

### `/handoff` (no args)
1. Resolve the `.handoff` location (above); create it and the symlink if needed.
2. Read the conversation, recent `git log`, `git diff`, and any existing handoff docs.
3. Rewrite STATUS.md, DECISIONS.md, CONTEXT.md, and NEXT.md to current state. Redact
   secrets; reference rather than duplicate.
4. Ensure `.handoff` is gitignored.
5. Sync any existing agent-instruction files (AGENTS.md, CLAUDE.md, ...).
6. If the `retro` skill is installed, invoke it as the session's self-improvement pass,
   after the docs are written. retro self-routes: it folds tooling learnings back into
   the skills, always writes a per-project retro note (under `retro/` in the resolved
   location), and distills into an external knowledge base **only** when your operator
   config maps this repo to one. Safe on any project; routing is what changes, not
   whether it runs. Skip cleanly if retro isn't present.
7. Print a brief summary of what was documented (and what retro distilled, where).

### `/handoff [focus]`
Same, but emphasize the named area. e.g. `/handoff architecture` puts extra detail in
DECISIONS.md and CONTEXT.md about structural choices.

### `/handoff read` (or "what were we doing" / "catch me up")
Resolve the location and read/summarize the existing docs to restore context fast.

## File format

Plain markdown, no frontmatter. Start each file with a `# Title` and a one-line
description, then get into it. `##` sections to organize. When updating an
append-style file (like a retro note), use a dated section header (`## 2026-06-25`);
the four canonical docs are rewritten, not dated.

Example STATUS.md:
```markdown
# Status

Current state of widget as of 2026-06-25.

## Done
- Native status/log/diff via libgit2
- Git passthrough for unimplemented commands (execvpe)
- Benchmarks: status 1.61x, diff 1.47x faster than git

## In Progress
- (nothing active)

## Blocked
- (nothing blocked)
```
