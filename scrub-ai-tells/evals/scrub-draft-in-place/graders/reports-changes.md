---
type: llm
focus: last_message
---

The skill ends with a brief report: files touched and the kinds of changes made (e.g. "removed
3 em dashes, replaced filler phrases, cut the kicker"), plus anything it could not fix without
inventing information.

PASS if the reply is a short summary of what changed in draft.md, naming at least three kinds
of change actually made (em dashes, filler words, the parallel bullets, the hedging, the
kicker/colon reveal, the opener), and does not paste the entire rewritten file as the reply.

FAIL if the reply is only the full rewritten document with no summary, if it lists no concrete
change types, or if it claims changes that the described categories could not plausibly cover
(e.g. "fixed grammar" as the only item).
