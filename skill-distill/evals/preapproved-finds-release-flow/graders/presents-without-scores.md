---
type: llm
focus: last_message
---

The skill's Phase 3 rule is "show a simple list without scores": the internal suitability
scoring (frequency, consistency, automatable fraction, cross-tool reach) and the internal
Recommend / Worth skillifying / Not suitable ranking logic are not shown as numbers. What IS
shown, per candidate: a verb + object name, its occurrence count and the tools it appeared
in, 1-2 representative prompts, and then a Phase 4 question asking which candidates to
turn into skills.

Definitions for this check:
- A "score" is a numeric or graded suitability rating attached to a candidate, e.g.
  "Score: 8/10", "consistency: HIGH, automation: 70%", a scoring table or matrix, or
  "priority 0.9". These FAIL.
- Occurrence counts ("3x", "seen 4 times") are required, not scores.
- Ordering by strength, tier or bucket labels ("Tier 1", "Recommended", "High priority",
  medal emoji), and phrases like "ranked by repetition" are NOT scores and do not fail.

PASS if the reply lists candidates with occurrence counts and no numeric/graded
suitability ratings, gives at least one representative prompt (quoted or paraphrased) for
the leading candidate, and ends by asking the user which candidates to skillify.

FAIL if a candidate carries a numeric or graded suitability score as defined above, if no
representative prompt appears anywhere, if the reply does not ask the user to choose, or if
it describes a generated skill's contents as though Phase 5 had already run.
