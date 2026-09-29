---
type: llm
focus: { source: file, path: ".antislop/VERDICT.md" }
weight: 2
---

The verdict template ends with an Evidence index table, one row per findings file the run
produced. With `--quick` the run is universal-only: the inventory topic (u01) plus the
eight universal topics u02_docs_vs_reality, u03_stubs_dead_code, u04_secret_hygiene,
u05_dependency_sanity, u06_config_env_prod, u07_ci_repo_hygiene,
u08_architectural_coherence, u09_error_handling. The Python language pack (py01, py02,
py03: build/lint, test reality, runtime safety) must NOT have run.

Judge only the Evidence index (or an equivalent per-topic listing) in this file.

PASS if it has rows for at least six of the eight universal topics u02-u09, each with a
topic verdict, and no py01/py02/py03 (or ts01-ts03) row is presented as having run with
results.

FAIL if fewer than six universal topics appear with a verdict, or if a language-pack topic
is listed with a verdict and findings as though it ran (e.g. "py02_test_reality: FAIL, suite
does not collect"), or if the verdict reports ruff/mypy/pytest results as its own toolchain
evidence.
