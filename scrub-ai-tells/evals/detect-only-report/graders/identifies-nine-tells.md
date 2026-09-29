---
type: llm
focus: last_message
weight: 2
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

This check is only about coverage and the overall shape of the reply. Count how many of the
thirteen numbered items the reply identifies: an item counts if the reply quotes it or clearly
points at it, whatever name it gives the pattern, and a grouped entry counts each item it
names. Whether each entry carries a fix, and how the studies-show item is handled, are graded
elsewhere.

PASS if the reply is a list of findings (not a rewritten draft) and identifies at least NINE of
the thirteen.

FAIL if the reply is a rewritten version of the document instead of a list of findings, or if
it identifies fewer than nine of the thirteen.
