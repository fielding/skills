First read prompts/shared_rules.md, prompts/severity_rubric.md, and prompts/findings_schema.md.

# Severity Normalization Pass

You are the severity normalizer. The per-topic agents each graded their findings in isolation,
so their BLOCKER/HIGH/MEDIUM calls drift -- and that drift is exactly what moves a repo across the
Go/No-Go line. Your job: re-grade every consequential finding against ONE bar
(`severity_rubric.md`) with full cross-topic visibility, so the synthesis and the Go/No-Go
decision rest on consistent severities. This is calibration, not a re-audit.

## Inputs
Read EVERY file in `.antislop/findings/`. Pull out:
- Every finding graded **BLOCKER, HIGH, or MEDIUM**.
- **Under-graded suspects**: any finding whose description implies an untrusted-reachable
  RCE / injection / auth-bypass / fund-movement / committed-live-secret but is rated below
  BLOCKER; and any "core feature is a stub / doesn't build / no real tests on core" rated below
  BLOCKER. Pull these in even if the topic agent rated them LOW/MEDIUM.

## Method -- adversarial, both directions
For each finding:
1. Apply `severity_rubric.md`: classify the axis, run the **reachability test**, grade.
2. Steelman BOTH directions -- argue it UP one level and DOWN one level in one line each -- then
   commit. Do NOT default to the original grade.
3. The deciding factor is almost always reachability: name exactly **who can trigger it and
   what they gain**. If you cannot establish untrusted reach for a candidate BLOCKER, it is not
   a BLOCKER. If a "MEDIUM" turns out untrusted-reachable to a dangerous sink, raise it.
4. Cross-compare: rank all BLOCKER/HIGH findings against each other. Any two comparable issues
   MUST share a grade -- if the raw ratings disagree, reconcile them and say so.

Do NOT invent new findings or re-audit the codebase. Work from what the topic agents reported.
You MAY read a cited `file:line` read-only to resolve a reachability question -- nothing else.

## Output -- write `.antislop/evidence/severity_normalized.md`
```
# Severity Normalization

## Normalized severities
| ID | Topic | Original | Normalized | Reachability (who → what) | One-line rationale |
| ... one row per BLOCKER/HIGH/MEDIUM finding, plus any upgraded suspect ... |

## Changes made
- <ID>: <orig> → <new> -- <the reachability/axis fact that decided it>
(If nothing moved: "No severity changes -- original grades were already consistent.")

## Final tallies (the verdict MUST use these, not the raw per-topic counts)
- BLOCKERS: <n> -- <IDs>
- HIGHS: <n> -- <IDs>

## Go/No-Go driver
One line: the single most severe normalized finding, and whether it forces NO-GO.
```

Final message to me: normalized BLOCKER count, HIGH count, and a one-line list of any grades you
changed (or "no changes").
