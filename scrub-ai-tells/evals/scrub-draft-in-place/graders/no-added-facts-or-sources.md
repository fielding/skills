---
type: llm
focus: { source: file, path: "draft.md" }
---

This is draft.md after the scrub. Scrub changes how the text says things, never what it says:
no new factual claim, source, or citation may appear. The original contained "Studies show
that resumable exports cut operator time significantly." with no source anywhere in the file;
the skill's flag-don't-invent rule says to flag that to the user and leave the spot alone,
never to supply a source.

This check is only about additions. Whether the original claims survive, and whether the code
block is intact, are graded elsewhere.

PASS if no factual claim, source, or citation that was not in the original appears in the
file. Leaving the studies-show sentence as-is, or removing it, both pass this check.

FAIL if any new fact, number, source, or citation appears; in particular if a study, report,
vendor, paper, or year has been attached to the "resumable exports cut operator time" line.
