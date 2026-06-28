# Verdict Template — Anti-Slop

You are the synthesis agent. Read every file in `.antislop/findings/`, then write
`.antislop/VERDICT.md` in the format below. This is the **only** artifact most people read.
Lead with the answer. No preamble, no methodology section, no restating the topics.

Rules:
- The whole thing fits on one screen. If it doesn't, cut prose, not findings.
- Quote `file:line` for every red flag. A claim without a location is a suspicion, not a flag.
- Don't soften. If it's a mirage, say "mirage." Friends asked for the real call.
- Roadmap is *ordered next actions*, not story-pointed sprints. Highest-leverage first.

---

## VERDICT.md format

```
# Anti-Slop Verdict — <repo> @ <sha>

## Substance Score: <n>/100 — <Real | Mostly-real | Mirage | Abandon>
<Two sentences. What this project actually is vs. what it presents itself as. The honest call.>

## Go / No-Go
<One line: is it worth deeper work / real users / your time — and the single biggest reason.>

## Top Red Flags
1. **<headline>** — `path:line` — <why it matters, one line>  [Severity]
2. ...
(Up to 7. Ranked by how much they undermine "this is real". BLOCKERS first.)

## Roadmap (do in this order)
1. <action> — <effort> — <what it unblocks>
2. ...
(Stop at the point where the project crosses from "mirage" to "worth a real audit". Note that line.)

## Recommended next step
<Either: "Run the <name> domain pack: /anti-slop --deep --domain <name>" — or "none; fix the
above first" — or "restart; not salvageable as-is".>

## Evidence index
| Topic | Verdict | Blockers | Headline |
| ... one row per findings file ... |
Full evidence: .antislop/findings/<id>.md
```

---

## Substance Score rubric

Per-topic verdict → base points: PASS = 100 · PASS WITH CONCERNS = 65 · INCONCLUSIVE = 50 ·
FAIL = 15.

Weighted average over scored topics (inventory `u01` is context, **not scored**). The
language-pack topics map onto the `ts01/ts02/ts03` rows by position (`py01→ts01`, etc.).

**Do NOT compute this average in your head — summing 11 weighted terms by hand is error-prone
and will misclassify near a band boundary.** Build the `(base, weight)` list and evaluate it
with a tool, then paste the tool's exact output into the audit block:

```bash
python3 - <<'EOF'
rows = [            # (topic, base, weight) — base: PASS=100 PWC=65 INCONCLUSIVE=50 FAIL=15
  ("u02",  65, 1.5), ("u03", 100, 1.5), ("ts01", 65, 1.5), ("ts02", 100, 1.5),
  ("u09",  65, 1.2), ("u04", 100, 1.0), ("u08",  65, 1.0), ("ts03", 100, 1.0),
  ("u05", 100, 0.8), ("u06",  65, 0.8), ("u07",  65, 0.6),
]
num = sum(b*w for _,b,w in rows); den = sum(w for _,_,w in rows)
print(f"num={num}  den={den}  avg={num/den:.2f}  ->  {round(num/den)}/100")
EOF
```

(Drop any rows whose topic didn't run — e.g. `--quick` or an unbuilt language pack — so `den`
renormalizes automatically. Apply hard overrides AFTER this number.)

**Polyglot repos (more than one language pack ran):** each language pack maps onto the same
three `ts01/ts02/ts03` rows. Do NOT add both as separate rows (that would double the language
weight). Instead, for each language-row use the **average base points across the packs that
ran** for that row — e.g. with Python + TS, the `ts01` row base = `(py01_base + ts01_base)/2`.
This counts every language at its true weight. State in the verdict which packs ran and that
their per-row verdicts were averaged.

| Topic | Weight | Why it weighs that |
|---|---|---|
| u02 docs_vs_reality | 1.5 | confident-lie is *the* slop signature |
| u03 stubs_dead_code | 1.5 | measures hollowness directly |
| ts01 build_types_lint | 1.5 | does it even compile/run |
| ts02 test_reality | 1.5 | are the tests real or theater |
| u09 error_handling | 1.2 | happy-path-only is core slop |
| u04 secret_hygiene | 1.0 | also a hard safety gate |
| u08 architectural_coherence | 1.0 | copy-paste drift = no design |
| ts03 runtime_safety | 1.0 | boundaries validated? |
| u05 dependency_sanity | 0.8 | lockfile / bloat / hallucinated deps |

| Topic | Weight | Why it weighs that |
|---|---|---|
| u02 docs_vs_reality | 1.5 | confident-lie is *the* slop signature |
| u03 stubs_dead_code | 1.5 | measures hollowness directly |
| ts01 build_types_lint | 1.5 | does it even compile/run |
| ts02 test_reality | 1.5 | are the tests real or theater |
| u09 error_handling | 1.2 | happy-path-only is core slop |
| u04 secret_hygiene | 1.0 | also a hard safety gate |
| u08 architectural_coherence | 1.0 | copy-paste drift = no design |
| ts03 runtime_safety | 1.0 | boundaries validated? |
| u05 dependency_sanity | 0.8 | lockfile / bloat / hallucinated deps |
| u06 config_env_prod | 0.8 | hardcoded config, env separation |
| u07 ci_repo_hygiene | 0.6 | real CI vs cosmetic |

(If a language pack didn't run — `--quick` or unbuilt pack — drop its rows and renormalize.
Say so in the verdict; a missing toolchain check lowers confidence, not the score.)

**Two independent axes — do not conflate them:**

1. **Substance Score** answers *"is this real, built software or a hollow mirage?"* Only
   **realness-fatal** conditions cap it (they mean the code isn't actually there):
   - Doesn't build / typecheck, OR zero real tests on core logic, OR a core advertised feature
     is a stub/absent, OR the codebase is scaffolding → cap at **34 → Abandon**, unless one
     named focused fix clears it (say which).
   - Otherwise the score IS the weighted average. Individual FAIL verdicts already pull it down
     proportionally — do **not** additionally cap for them.

2. **Go / No-Go** answers *"should this be trusted / shipped / built on right now?"* It is
   SEPARATE from the score. Force **NO-GO** whenever **any BLOCKER** exists — security (auth
   bypass, injection, RCE), safety (money/data loss), or a committed live secret — and list
   each blocker explicitly. A repo can legitimately be **"Real, 82 — but NO-GO until the 2
   security blockers are fixed."** High substance and "do not ship" coexist; say both.

Why split them: a working app with an auth hole is *real software with a serious bug*, not a
mirage. Capping its substance to "Mirage" would mislabel solid work as fake. Reserve the
substance cap for genuine hollowness; route danger through Go/No-Go.

✅ **Use the normalized severities.** The Wave 2.5 severity-normalization pass already
reconciled BLOCKER/HIGH/MEDIUM across topics against one bar — read
`.antislop/evidence/severity_normalized.md` and take its **Final tallies** and **Go/No-Go
driver** as authoritative for the blocker count, Go/No-Go, and red-flag ranking. Do NOT re-tally
the raw per-topic grades (that's the drift this pass exists to remove). If that file is missing
(pass skipped), fall back to eyeballing consistency yourself per `severity_rubric.md`. The
Substance Score still reflects *how real/built* the code is — it is **not** an
engineering-quality or production-readiness ranking,
and a higher score does not mean "better engineered" (a small tidy repo can out-score a large
battle-tested one). Say this in the verdict if the number invites that misread.

Bands: **80-100 Real** (worth a full audit / real work) · **60-79 Mostly-real** (fixable, real
gaps) · **35-59 Mirage** (looks finished, isn't; major rework) · **0-34 Abandon** (scaffolding,
not a product; faster to restart). State the number AND the band — friends respond to a number.
