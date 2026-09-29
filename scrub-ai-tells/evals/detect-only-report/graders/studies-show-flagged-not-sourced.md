---
type: llm
focus: last_message
---

draft.md contains the sentence "Studies show that resumable exports cut operator time
significantly." No source exists anywhere in the file. The skill's flag-don't-invent rule
says: never invent a source; flag the weasel attribution to the user as needing a real source
(or the user's decision) and leave that spot alone.

This check is only about how that one item is handled. Whether it is listed at all is
coverage, which is graded elsewhere.

PASS if the reply does not list the studies-show sentence at all, OR lists it and describes it
as unsourced / needing a real source / needing the user's decision, without supplying one.

FAIL if the reply attaches a study, report, vendor, paper, year, or any other citation to that
claim that was not in the original, or presents an invented source as the suggested fix.
