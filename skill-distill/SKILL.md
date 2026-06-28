---
name: skill-distill
description: >-
  Analyzes AI agent session history across Claude Code, Codex CLI, pi-mono,
  and Cursor to discover recurring workflows and auto-generate Agent Skills.
  Use this skill whenever you want to mine your coding history for patterns
  worth turning into skills, even if you just say something like "what do I
  keep doing over and over" or "find patterns in my history". Invoke manually
  with /skill-distill.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch
disable-model-invocation: true
user-invocable: true
---

# Skill Distill

Analyze session history across AI coding tools, find recurring patterns, and generate new skills from them.

## Safety

- Never paste raw log content into a skill. Paraphrase and sanitize all examples.
- Before reading any history file, list the exact files for the user and get explicit approval.
- Mask secrets (tokens, passwords, keys) found in commands. Never copy stdout/stderr into skills.
- Use `[` and `]` instead of angle brackets in generated YAML frontmatter and skill bodies.

## Workflow

Run these 6 phases in order. Confirm with the user before starting Phase 5.

Progress checklist:
- [ ] Phase 1: Data Collection
- [ ] Phase 2: Pattern Extraction
- [ ] Phase 3: Suitability Evaluation
- [ ] Phase 4: User Selection
- [ ] Phase 5: Skill Generation
- [ ] Phase 6: Quality Validation

---

## Phase 1: Data Collection

### Consent Gate

Before reading anything, present these choices and get approval:

1. **Which tools**: Claude Code, Codex CLI, pi-mono, Cursor (any combination, default: all)
2. **Scope**: current project or all projects
3. **Time range**: last N days
4. **Files to read**: list them explicitly per tool

### Running the Extractors

All scripts live in this skill's directory and output normalized JSONL:
`{"source", "display", "timestamp", "project", "sessionId"}`

For **single-source** runs:

| Tool | Command |
|------|---------|
| Claude Code | `python3 {skill-dir}/scripts/filter-history.py --days {N} --project "{path}" --noise-filter` |
| Codex CLI | `python3 {skill-dir}/scripts/extract-codex-history.py --days {N} --project "{path}"` |
| pi-mono | `python3 {skill-dir}/scripts/extract-pi-history.py --days {N} --project "{path}"` |
| Cursor | `python3 {skill-dir}/scripts/extract-cursor-history.py --days {N} --project "{path}"` |

For **multi-source** runs (preferred):
```bash
python3 {skill-dir}/scripts/merge-histories.py --days {N} --sources claude,codex,pi,cursor --project "{path}" --noise-filter --stats
```

The merge script calls the individual extractors and deduplicates the output. Use `--stats` to show per-source counts.

If Claude Code's history.jsonl is too large for the Read tool (>256KB), the filter script handles it. For Cursor, ensure sqlite3 is available and Cursor is not running (locked DB).

---

## Phase 2: Pattern Extraction

Analyze the normalized prompts for concrete, recurring task patterns. Focus on what the user actually repeats, not broad categories.

### Three-Axis Extraction

**WHAT** - The goal the user wants to achieve.
Examples: "commit with appropriate granularity", "fix lint errors", "review PR feedback"

**HOW** - The method or workflow repeatedly specified.
Examples: "spin up agent team for parallel work", "create git worktree for isolation"
HOW patterns cross-cut multiple WHATs. This cross-cutting nature is strong evidence of skillification value.

**FLOW** - Session-level prompt chains forming a cohesive workflow.
Examples: "identify issues -> address each -> commit" repeated across 4 sessions.

### Extraction Steps

1. Exclude noise: /clear, /resume, /status, /usage, /plugin, /init, /mcp, empty prompts, bare `[Pasted text]`.
2. For each prompt, identify the WHAT (goal). If it also specifies a HOW (means), count it under both.
3. Group by sessionId, sort chronologically, summarize prompt chains. Record flows appearing 3+ times as FLOW patterns.
4. Name each pattern as verb + object.
5. For HOW patterns, record which WHATs they combined with.
6. For each pattern, record which tools it appeared in.

### Counting Rules

- WHAT/HOW contained within a FLOW: count on the FLOW side only.
- Only independently-appearing WHAT/HOW count as standalone WHAT/HOW.
- Still record the cross-cutting nature of HOW even when it appears inside a FLOW.

### Cross-Tool Bonus

Patterns appearing in 2+ tools are tool-agnostic and especially valuable. Note the tools for every pattern.

### Output Per Pattern

- Pattern name (verb + object), axis (WHAT/HOW/FLOW), occurrence count
- Sources (which tools), 2-3 representative prompts, common steps
- FLOW only: flow steps as arrows, contained WHAT/HOW patterns
- HOW only: which WHATs it combined with
- Variations across occurrences

---

## Phase 3: Suitability Evaluation

### Cross-Reference Existing Skills

1. Glob for `~/.claude/skills/*/SKILL.md` and `.claude/skills/*/SKILL.md`.
2. Read name + description from each.
3. Classify patterns: Fully covered (exclude), Partially covered (keep the gap), Not covered (keep).

### Scoring (Internal)

Evaluate each pattern on:
- **Frequency**: occurrence count
- **Consistency**: HIGH (nearly identical each time), MEDIUM (shared core, varying details), LOW (different each time)
- **Automatable steps**: fraction that is routine/templatable
- **Cross-tool reach**: patterns in more tools score higher

### Ranking (Internal - Do Not Show)

- **Recommend**: FLOW with freq >= 3 and consistency MEDIUM+, or WHAT with high freq and HIGH consistency, or any pattern in 3+ tools
- **Worth skillifying**: medium freq or MEDIUM consistency, or HOW across 3+ WHATs, or pattern in 2 tools
- **Not suitable**: LOW consistency with low automation rate

### Present to User

Show a simple list without scores:

```
Recommended for skillification:
1. [Pattern name] (Nx, tools: X + Y) - [description]

Worth skillifying:
2. [Pattern name] (Nx, tools: X) - [description]
```

Include 1-2 representative prompts per candidate. Note when a FLOW contains a WHAT/HOW.

---

## Phase 4: User Selection

1. Ask which patterns to skillify (multiple OK).
2. Show matching prompts from the relevant sources.
3. Confirm for each selection:
   - Scope: which part of the workflow to cover
   - Variation handling: options within one skill vs. separate skills
   - Placement: global (`~/.claude/skills/`) or project-specific (`.claude/skills/`)
   - Trigger phrases for the description
4. If more context is needed, read 2-3 individual session files.

---

## Phase 5: Skill Generation

### Rules

- Never paste raw session content into a skill.
- Never include angle brackets in YAML frontmatter or body. Use `[` and `]`.
- Never include secrets, tokens, or private identifiers.
- Paraphrase all examples.

### Structure

```
{skill-name}/
  SKILL.md          # Main procedure (required)
  scripts/          # Helper scripts (if needed)
  references/       # Supplementary docs (if needed)
```

### SKILL.md Requirements

Frontmatter must include at minimum:
```yaml
---
name: my-skill
description: >-
  What this skill does and when to use it. Include trigger phrases.
allowed-tools: Read, Bash, Grep
disable-model-invocation: true
user-invocable: true
---
```

Body must include:
- Clear numbered workflow steps
- Error handling for common failures
- At least 2 usage examples
- Under 500 lines total

Note in the skill which tools the pattern was observed in, for context.

### Placement

- Global: `~/.claude/skills/{skill-name}/`
- Project-specific: `.claude/skills/{skill-name}/`

---

## Phase 6: Quality Validation

1. Fetch best practices from `https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices` using WebFetch.
2. Check the generated skill against those guidelines.
3. Fix any issues and re-validate.
4. Report the result. If everything passes, say "All checks passed."

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Cursor SQLite fails | Check that sqlite3 exists and Cursor is not running |
| pi-mono sessions missing | Verify ~/.pi/agent/sessions/ exists; expand time range |
| history.jsonl too large | Use filter-history.py (handles files >256KB) |
| JSON parse error | Narrow scope or change time range |
| No sessions found | Expand time range or switch to all-projects scope |
