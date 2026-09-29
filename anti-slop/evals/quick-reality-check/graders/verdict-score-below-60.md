---
type: llm
focus: { source: file, path: ".antislop/VERDICT.md" }
---

This is the one-page VERDICT.md the skill writes. The fixture repo ("notekeeper") advertises
AES-256 "encrypted at rest" while every function in `notekeeper/crypto.py` only raises
NotImplementedError; a core advertised feature that is a stub is the confident-lie slop
signature and, per the rubric, caps the Substance Score at 34. `notekeeper/cli.py` also
hardcodes a live-looking `SYNC_API_KEY`, a BLOCKER. The bands: Real and Mostly-real sit at
60 and above; Mirage and Abandon sit below 60.

PASS if the Substance Score is below 60, i.e. the band is Mirage or Abandon.

FAIL if the score is 60 or higher, the band is Mostly-real or Real, or no score is given.
