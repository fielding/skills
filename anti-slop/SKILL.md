---
name: anti-slop
version: "1.0.0"
description: >
  Fast first-pass reality check for any codebase — especially vibe-coded / LLM-generated
  projects friends hand you to "look over." Answers the only question that matters up front:
  is this real software, or a confident-looking mirage? Produces a one-page VERDICT with a
  0-100 Substance Score, top red flags, a go/no-go call, and an ordered fix roadmap — backed
  by per-topic evidence on disk. Three layers over one engine: (1) universal slop checks that
  apply to any language, (2) a language pack (TypeScript/JS and Python implemented; Go/Rust
  stubbed) that runs the real toolchain, (3) optional domain packs (crypto-wallet bundled).
  Use this skill when the user says "audit this", "is this real / any good", "check this
  project", "anti-slop", "slop check", "review this repo", "did they actually build it",
  "should I bother", "vibe check this", or hands over an unfamiliar repo to vet. This is the
  first thing you run on any project before a deeper domain audit.
---

# Anti-Slop: First-Pass Reality Check

You are the orchestrator. You coordinate subagents — you do not review code yourself. Each
subagent has its own isolated context, reads one prompt file, does the analysis, and writes
findings to disk. Your job is setup, scheduling, and synthesis.

This is a **triage** tool. The deliverable people actually read is the one-page `VERDICT.md`.
Everything else is backing evidence for when someone disputes the call. Optimize for a
2-minute read that ends in a clear "real / fix it / restart" decision.

Prompt files live in `references/` inside this skill and are copied to `.antislop/prompts/`
in the target repo during setup. Findings are written to `.antislop/findings/`.

## Arguments

Parse from the user's invocation:
- `--quick` — universal layer only (skip the language pack). Fastest triage.
- `--deep` — after the verdict, also run the matched domain pack (default: recommend, don't run).
- `--domain <name>` — force a specific domain pack (e.g. `crypto-wallet`).
- `--lang <name>` — force a language pack instead of auto-detecting.
- `--topic <id>` — run only one topic (e.g. `u03_stubs_dead_code`).
- `--setup` — initialize dirs and copy prompts only; spawn nothing.
- `--no-score` — skip the numeric Substance Score (still produce the verdict).
- `--resume` — skip topics whose findings files already exist.
- `--dry-run` — print the plan only; write nothing; spawn nothing.

## Step 1: Setup

```bash
REPO=$(git rev-parse --show-toplevel 2>/dev/null || pwd)

# Locate this skill's references/. NOTE: some environments wrap `find` with `bfs`,
# whose `-path` glob does not match — so check canonical locations directly, then fall
# back to a `-name` search (which traverses reliably) filtered to anti-slop.
SKILL_DIR=""
for base in "$HOME/.claude/skills" "$REPO/.claude/skills"; do
  [ -d "$base/anti-slop/references" ] && { SKILL_DIR="$base/anti-slop/references"; break; }
done
[ -z "$SKILL_DIR" ] && SKILL_DIR=$(find "$HOME/.claude" "$REPO/.claude" -type d -name references 2>/dev/null | grep anti-slop | head -1)

mkdir -p "$REPO/.antislop/"{prompts,findings,evidence}
git -C "$REPO" rev-parse HEAD > "$REPO/.antislop/COMMIT_SHA.txt" 2>/dev/null || echo "no-git" > "$REPO/.antislop/COMMIT_SHA.txt"

if [ -n "$SKILL_DIR" ]; then
  cp "$SKILL_DIR"/_engine/*.md   "$REPO/.antislop/prompts/"
  cp "$SKILL_DIR"/universal/*.md "$REPO/.antislop/prompts/"
  echo "Copied engine + universal prompts."
else
  echo "WARNING: could not find anti-slop references. Prompts may already be in .antislop/prompts/."
fi
```

Language-pack prompts are copied in Step 3 after the stack is known. If `--setup`: stop here.

Every subagent gets this wrapper (fill in `<id>` and `<REPO>`):

> You are running a focused, read-only reality check on the codebase at `<REPO>`.
> Read your prompt at `<REPO>/.antislop/prompts/<id>.md` and follow it exactly. Also read
> `<REPO>/.antislop/prompts/shared_rules.md` and `<REPO>/.antislop/prompts/findings_schema.md`
> first. Use absolute paths under `<REPO>`. Do NOT modify source, commit, install, or deploy.
> Write your findings to `<REPO>/.antislop/findings/<id>.md` using the Write tool before finishing.

## Step 2: Wave 0 — Inventory & Stack Detection (sequential)

Run `u01_inventory_stack` first and wait. It maps the repo and writes
`.antislop/evidence/stack.md` declaring: detected language(s), package manager(s), frameworks,
app surfaces, and a **domain guess** (e.g. `crypto-wallet`, `web-api`, `cli`, `unknown`).
Read that file — every later decision keys off it.

## Step 3: Pick & copy the language pack

From `stack.md`'s `toolchain_for_language_pack`, choose the pack (see
`references/lang/_stack_detect.md`):
- TypeScript / JavaScript → `lang/ts/` **(implemented)**
- Python → `lang/py/` **(implemented)**
- Go / Rust → stubbed; if matched, tell the user the pack isn't built yet and run
  universal-only, noting the gap in the verdict. Do not fabricate language-specific findings.
- Polyglot repo → copy each implemented pack that applies and label findings by sub-project.

```bash
LANG=$(rg -m1 '^toolchain_for_language_pack:' "$REPO/.antislop/evidence/stack.md" | sed 's/.*: *//' | tr -d ' ')
for l in $(echo "$LANG" | tr ',' ' '); do
  [ -d "$SKILL_DIR/lang/$l" ] && cp "$SKILL_DIR"/lang/$l/*.md "$REPO/.antislop/prompts/" && echo "Copied $l language pack."
done
```

Skip this step entirely if `--quick`.

## Step 4: Wave 1 — Universal slop checks (parallel)

Spawn all eight in parallel:
`u02_docs_vs_reality`, `u03_stubs_dead_code`, `u04_secret_hygiene`, `u05_dependency_sanity`,
`u06_config_env_prod`, `u07_ci_repo_hygiene`, `u08_architectural_coherence`, `u09_error_handling`

## Step 5: Wave 2 — Language pack (parallel, skipped on `--quick`)

Spawn the three topics of each matched pack (e.g. TS: `ts01_build_types_lint`,
`ts02_test_reality`, `ts03_runtime_safety`; Python: `py01_build_types_lint`,
`py02_test_reality`, `py03_runtime_safety`). These run the real toolchain (tsc/eslint/jest,
mypy/ruff/pytest) and are the ground truth for "does it actually work."

## Step 6: Wave 2.5 — Severity Normalization (sequential, single agent)

After all topic findings exist and before synthesis, run **one** `severity_normalize` agent.
Per-topic agents grade BLOCKER/HIGH/MEDIUM in isolation, so their calls drift — and that drift
is what moves a repo across the Go/No-Go line. This pass re-grades every consequential finding
against one bar (`references/_engine/severity_rubric.md`, copied to prompts/) with full
cross-topic visibility, applying the reachability test (untrusted-reachable RCE/auth-bypass/
fund-movement = BLOCKER; trusted-local-operator-only = capped at MEDIUM). It writes
`.antislop/evidence/severity_normalized.md` with reconciled tallies and a Go/No-Go driver.

Skip only if `--no-score` AND the user explicitly wants raw grades. For scale, you may run a
3-agent panel and take the majority grade per finding instead of one normalizer.

## Step 7: Wave 3 — Synthesis → VERDICT.md (sequential)

Read every file in `.antislop/findings/` AND `.antislop/evidence/severity_normalized.md`,
then write `.antislop/VERDICT.md` following `references/_engine/verdict_template.md` exactly.
Compute the Substance Score per the rubric there (unless `--no-score`). **Use the normalized
severities — not the raw per-topic grades — for the blocker count, Go/No-Go, and red-flag
ranking.** The verdict leads; evidence is indexed, not pasted.

## Step 8: Domain handoff

From `stack.md`'s domain guess, consult `references/domain/_registry.md`:
- If `--deep` or `--domain <name>`: copy that pack's prompts into `.antislop/prompts/` and run
  them as an extra wave, then fold their findings into the verdict.
- Otherwise: end the verdict with a one-line **recommendation** of which domain pack to run
  next and the exact command (e.g. `/anti-slop --deep --domain crypto-wallet`).

## Step 9: Completion report

```
ANTI-SLOP — <repo name> @ <sha>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SUBSTANCE SCORE   <n>/100   →  <Real | Mostly-real | Mirage | Abandon>
RED FLAGS         <n>       BLOCKERS  <n>
Verdict written:  .antislop/VERDICT.md
Recommended next: <domain pack or "none">
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
Print the one-paragraph verdict inline so the user gets the answer without opening a file.

## Notes for the Orchestrator

- Default model: Sonnet for universal/language waves; Opus for synthesis. Override as needed.
- Tell the user which agents are about to run before each wave; one-line PASS/FAIL after.
- If `u01` fails, stop — every later topic depends on the stack map.
- `--resume`: skip topics whose `.antislop/findings/<id>.md` already exists; mark "RESUMED".
- Never fabricate a finding to fill a topic. INCONCLUSIVE is an honest verdict.
- Three layers, one engine: universal (`references/universal/`) is language- and
  domain-agnostic; language packs (`references/lang/<lang>/`) own the toolchain; domain packs
  (`references/domain/<name>/`) own domain risk. All share `_engine/` rules + schema + verdict
  format. To add a language or domain, drop a new folder in — the orchestrator picks it up.
```
