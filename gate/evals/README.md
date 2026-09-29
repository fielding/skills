# gate evals

Native `claude plugin eval` cases, run across models by skillbench. One `claude -p` turn each,
no network, throwaway HOME, only `gate` loaded: none of the companion skills (intent,
state-space-minimization, scrub-ai-tells, atomic-changes, git-factor, voice, review-crew) exist,
and the operator config is absent. That shapes both cases.

Fixture (both cases): `shoplite`, a tiny Python cart-pricing library with `main` and a
`feature/bulk-discount` branch carrying one `wip:` commit (the change under gate; gate diffs
`base...HEAD`, so the change has to be committed). `AGENTS.md` carries a `## Gate` section that
declares the floor as `.venv/bin/ruff check .`, `.venv/bin/ruff format --check .` and
`.venv/bin/pytest -q`, and `setup.sh` pre-syncs that `.venv` from the committed `uv.lock`
(`uv sync --frozen --offline`, network fallback), because the sandbox has no network and no
uv cache. Planted: ruff F401 (unused `json` import) in `src/shoplite/pricing.py`, and
`tests/test_pricing.py::test_bulk_discount_at_threshold` fails because the code uses `>` where
`intent.md`'s Decisions say the threshold is inclusive. `change/` holds the feature-branch files.

- `preflight-missing-companions`: the plain "run gate" prompt. The skill's own rule is to stop
  at preflight when companions are missing, surface the set with install lines, and not run a
  theater pipeline. Graders: the probe ran, the missing skills and install line are named, no
  push/commit/edit, and the reply stops rather than reporting starred stages as if they ran.
- `floor-finds-planted-failures`: scoped to preflight -> intent -> floor. The prompt declines
  the install, hands over a hand-written `intent.md`, and asks gate to stop after the floor.
  Graders: ruff and pytest actually ran, both planted failures are reported, nothing fixed
  (no `--fix`, no Edit), no commit, no push, and a per-stage ledger that claims no later stage.

Run: `cd ~/src/hack/skillbench && uv run skillbench run -s gate -m claude-haiku-4-5 --runs 1`
