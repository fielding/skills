---
type: llm
focus: last_message
---

The repo is Python (`pyproject.toml`, `src/shoplite/*.py`). Gate's preflight requires a
conventions pack only for the detected language: `rust-conventions` for Rust,
`typescript-conventions` for TypeScript. For Python the pack is "planned", so it is dropped
from the required set and, at most, mentioned as a warning that stage 3's language layer
will be skipped. The probe script in the skill defaults `pack=rust-conventions`; running it
unadapted would wrongly report rust-conventions as a missing requirement for this repo.

PASS if the set of missing/required skills the reply reports contains none of
`rust-conventions`, `typescript-conventions`, or a Python conventions pack presented as a
hard requirement. The reply may mention a Python pack only as a warning or skipped layer, or
not at all; it does not need to say the word "Python".

FAIL if `rust-conventions` or `typescript-conventions` is listed as missing or required for
this repo, or if a Python conventions pack is listed as a blocking missing skill.
