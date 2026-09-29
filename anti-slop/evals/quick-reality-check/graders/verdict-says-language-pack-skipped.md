---
type: llm
focus: { source: file, path: ".antislop/VERDICT.md" }
---

With `--quick` the run is universal-only: the Python language pack (py01 build/lint, py02
test reality, py03 runtime safety) does not run, and the verdict template requires the file
to say so ("language pack skipped / toolchain checks not run"), lowering confidence, not the
score, on that account.

Judge only whether this file admits the skip.

PASS if the verdict states somewhere that the language pack / toolchain checks were skipped
or not run for this quick pass; noting that confidence is reduced as a result is expected
alongside that statement.

FAIL if the file never mentions that the language pack / toolchain checks were skipped or
not run.
