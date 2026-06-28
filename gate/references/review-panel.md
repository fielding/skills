# Built-in review panel (gate stage 7 fallback)

The portable implementation of gate's adversarial review, for when `review-crew` is
not installed. It reconstructs the crew's core value -- cross-reviewer diversity and
*disagreement as signal* -- using only the agent's own `Agent` (subagent) tool. Load
this file only on the fallback path; if `review-crew` is present, stage 7 uses it
instead and this is never read.

## Run the panel

Spawn 2-3 reviewers with the **Agent** tool, each over the pushed diff
(`git diff <base>...HEAD`) plus `intent.md`, each with a **distinct lens** and, where
the operator has the access, a **distinct model**. Cross-model diversity is the real
prize (a second model is blind to different things); same-model/different-lens still
helps. Suggested lenses:

- **correctness & safety** -- logic errors, edge cases, error handling, concurrency.
- **API & design** -- public surface, naming, abstraction, state shape (intent's Scope).
- **tests & evidence** -- do the tests cover the change; is every claim backed.

Give each reviewer the diff, `intent.md`, and its lens; ask for findings plus a verdict
on the ladder **MERGE > APPROVE_WITH_NOTES > BLOCK**.

## Reconcile

- flagged by **all** -> high-confidence; fix.
- flagged by **one** -> surface for judgment (one lens saw it; verify before acting).
- verdicts **disagree** -> the disagreement *is* the finding; dig into the contested
  point and resolve it on evidence. A split verdict is never averaged away.

The reconciled findings + verdict are the stage's output -- they feed the fold
(stage 8) exactly like review-crew's `pr-comment.md`.

## Optional: a debate round

Closer to the real crew: after the independent pass, show each reviewer the others'
findings and let them rebut or concede, then re-reconcile. The disagreement-driven dig
above already captures most of this signal, so the extra round is for thoroughness on
high-stakes changes.
