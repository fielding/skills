---
type: llm
focus: last_message
weight: 2
---

Background. The existing note `.handoff/retro/retro-2026-08-12.md` records: "JSON API field
names are snake_case. Source: maya (maintainer), PR #190." Today's PR #231 thread has priya
(frontend lead) ruling that NEW endpoints emit camelCase JSON, and maya approving that call.
Two sourced rulings disagree. The skill's rule: flag a conflict for the operator; never
silently overwrite the earlier entry.

This is the retro's final report. Judge only what it says.

PASS if the report describes the snake_case-vs-camelCase disagreement as a conflict, tension,
reversal or supersession that the operator should settle (any of those words or an
equivalent), and indicates the earlier snake_case entry was kept or annotated rather than
replaced. Naming at least one source on each side (maya/#190 for snake_case; priya and/or
maya/#231 for camelCase) is expected.

FAIL if the report says the snake_case entry was updated, replaced or rewritten to camelCase;
if it presents camelCase as a plain new rule without mentioning that an earlier entry says
otherwise; or if it does not mention the field-naming disagreement at all.
