# tutor evals

Two formats live here:

- `evals.json` is the skill-creator (anthropics/skills) format: prompt + expected output
  per eval. skill-creator's improve/benchmark loop reads it.
- `<case>/` directories are native `claude plugin eval` cases and are what skillbench
  (`~/src/hack/skillbench`) runs across models. They were derived from `evals.json` and
  then given concrete graders.

The fixtures under `*/fixtures/` (`cache.py`, `auth.py`) are reconstructions written
2026-09-23 from the descriptions in `evals.json`; the originals were not on this machine.
Grader design follows the 2026-07-03 retro: assert the outcome (what the learner is
steered to understand) as well as the process (checklist written, no silent fix).

A run is a single turn, so every case grades the *first reply*. For the two large asks
(`rust-ownership-concept`, `auth-flow-walkthrough`) the skill's correct first move is to
orient, so those graders judge the orient turn: calibration questions tied to the learner's
stated background, a scoped checklist with nothing marked Verified (read with
`focus: { source: file, path: .tutor/Understanding-Checklist.md }`), one step then a question.
`buggy-cache-understand` additionally asserts the mechanism the learner is steered toward
(shared `_store` + key collision) and that no fix is written.

Run: `cd ~/src/hack/skillbench && uv run skillbench run -s tutor -m claude-haiku-4-5 --runs 1`
