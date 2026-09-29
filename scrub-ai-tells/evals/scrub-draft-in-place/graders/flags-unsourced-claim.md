---
type: llm
focus: last_message
weight: 2
---

The draft contained "Studies show that resumable exports cut operator time significantly."
No source exists anywhere in the text. The skill's flag-don't-invent rule says: never invent a
source, never silently keep the weasel phrase; flag it to the user and leave that spot alone.

PASS if the final reply explicitly calls out that sentence (or the "studies show" claim) as
unsourced / needing a real source or the user's decision, AND does not supply a fabricated
source or citation for it.

FAIL if the reply never mentions the studies-show claim, or if it (or the described edit)
attributes the claim to a named study, report, vendor, or year that was not in the original,
or if it says the sentence was simply deleted without telling the user why.
