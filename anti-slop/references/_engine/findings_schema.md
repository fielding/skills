# Findings Schema -- Anti-Slop

Write your topic file in exactly this structure. Keep it tight -- the synthesis step reads it,
not a human. Evidence over prose.

```
# <Topic Name>

## Verdict
PASS / PASS WITH CONCERNS / FAIL / INCONCLUSIVE

## One-liner
A single sentence a busy reader could act on.

## What I checked
Files reviewed and commands run (exact). "None" if none.

## Findings
For each confirmed issue:
- **ID**: <TOPIC-01>
- **Severity**: BLOCKER | HIGH | MEDIUM | LOW | INFO
- **Slop signal**: mirage | confident-lie | fake-completeness | theater-test |
  copy-paste-drift | swallowed-failure | hygiene | n/a
- **File/Line**: exact path:line
- **Evidence**: the exact code or command output (redact secrets)
- **Why it matters**: 1-2 sentences
- **Fix**: specific, minimal recommendation
- **Effort**: XS (<2h) | S (<1d) | M (2-3d) | L (1 sprint) | XL (rewrite)

## Suspicions (unconfirmed)
Things worth a closer look but not proven.

## Score input
- topic_verdict: <PASS|PASS WITH CONCERNS|FAIL|INCONCLUSIVE>
- blockers: <n>
- highs: <n>
- headline: <one phrase the synthesis can quote as a red flag, or "none">
```

Severity discipline: a BLOCKER means the project fails its basic promise of being real or
safe. Don't spend them on style. Don't withhold them when earned -- a non-building repo with a
"production-ready" README is a BLOCKER, not a MEDIUM.
