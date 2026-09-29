---
type: llm
focus: last_message
---

draft.md contains these planted tells:

 1. Em dashes (three: "painful — slow", "pagination — you", "exactly once — no page").
 2. "Here's the thing:" announce opener.
 3. "It's worth noting that" filler.
 4. "serves as a centralized hub for" fake-strong verb (copula avoidance).
 5. "leverages", "in order to", "comprehensive", "robust", "seamlessly", "delves" vague-AI words.
 6. "Additionally", "Furthermore", "Note that", "Ultimately" transitions/openers.
 7. Three bullets all starting "Enables ..." (overly parallel list).
 8. "Studies show that ..." weasel attribution with no source.
 9. "might potentially be omitted ... could go to stdout" stacked hedging.
10. "While this is a simplified overview" unnecessary disclaimer.
11. "marks a pivotal moment" importance puffery.
12. "The result: exports that just work." colon reveal.
13. "Not faster. Not smaller. Just correct." negative listing / fake-profound kicker.

This check is only about the shape of each entry, not coverage. However many items the reply
lists, each one should give (a) a short quote or exact location in draft.md, (b) a name or
description of the pattern it matches, and (c) a suggested fix (a rewrite, "delete", "replace
with a comma", "needs a real source", and so on all count). A grouped entry such as "Vague
words: leverages, robust, seamlessly -> cut or say what it actually does" satisfies all three
for every word it names. How many tells were found is graded elsewhere; do not fail here for
items that are missing.

PASS if each listed entry gives a quote or location, a pattern name or description, and a
suggested fix.

FAIL if entries lack quotes or locations, or if they name patterns without saying what to do
about them.
