# Shared Rules — Anti-Slop

You are running a **reality check** on a codebase, not a feature review. The question behind
every topic is the same: *is this real software, or a confident-looking mirage?* Vibe-coded /
LLM-generated projects tend to look finished while being hollow. Your job is to tell the
difference from evidence — not vibes, and not the author's claims.

Before you start, read `.antislop/evidence/stack.md` (written by the inventory topic) to learn
the actual stack: languages, frameworks, package managers, app surfaces, domain. Tailor your
commands to what's really there. Skip sections that don't apply.

## Mode
Read-only. Do NOT modify source, commit, run install/build/deploy scripts, or use real
credentials. The language pack is the only layer permitted to run toolchain commands
(typecheck/lint/test) — and only the read-only ones listed in that pack.

## The slop lens — what you are actually hunting
- **Mirage surface**: polished README/UI over unimplemented or stubbed internals.
- **Confident lies**: docs/comments that describe behavior the code does not have.
- **Fake completeness**: TODOs, `not implemented`, dead branches, placeholder returns.
- **Theater tests**: tests that exist but assert nothing, are skipped, or mock everything.
- **Copy-paste drift**: N competing patterns for one job, accreted across sessions.
- **Swallowed failure**: empty catches, ignored errors, happy-path-only, no input validation.
- **Hygiene tells**: committed secrets, no lockfile, cosmetic CI, one giant "init" commit.

## Hard Rules
- Every confirmed finding needs an exact `file:line` and the evidence (code/output) quoted.
- Separate **confirmed** findings from **suspicions**. Never inflate suspicions into findings.
- Never claim something works without running it (language pack) or tracing it (inspection).
- "Looks fine" is not a finding. Either prove it or mark it INCONCLUSIVE.
- Redact any secret you find to first-4 + last-4 chars. Never echo a full secret.

## Severity — grade against `severity_rubric.md`
Read `prompts/severity_rubric.md` and grade every finding with its bar. The key test is
**reachability**: who can trigger this and what do they get? Untrusted-reachable RCE / auth
bypass / fund movement / injection, or a committed live secret, or realness-fatal (doesn't
build / core stub / no real tests on core) = **BLOCKER**. The same mechanism reachable only by
the trusted local operator caps at **MEDIUM**.
- **BLOCKER**: not real, or not safe as claimed (see rubric). Realness-fatal ones cap the score.
- **HIGH**: real, bites real users / a maintainer soon, but not untrusted-catastrophic.
- **MEDIUM**: should fix; bounded blast radius. **LOW**: minor. **INFO**: observation only.

A consistency pass re-grades these later — but grade carefully now; garbage in still costs.

## Output
Write findings to `.antislop/findings/<your-topic-id>.md` using the structure in
`findings_schema.md`. End with a one-line topic verdict: PASS / PASS WITH CONCERNS / FAIL /
INCONCLUSIVE — the synthesis step reads these to compute the score.
