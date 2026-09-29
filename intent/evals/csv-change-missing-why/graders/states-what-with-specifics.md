---
type: llm
focus: trace
weight: 2
---

"Never ask what the diff already shows." The uncommitted diff changes reportkit/export.py
(function reportkit.export.to_csv): delimiter "," -> ";", the header row is no longer
written, quoting becomes csv.QUOTE_ALL, the line terminator becomes "\r\n", and
tests/test_export.py is updated to match. The What is obvious from the diff.

PASS if, somewhere in the session (final reply or a written intent.md), the agent states the
What with at least THREE of these specifics taken from the diff: semicolon delimiter, header
row removed, QUOTE_ALL / every field quoted, CRLF ("\r\n") line terminator,
tests/test_export.py updated to the new format, function reportkit.export.to_csv.

FAIL if the agent states fewer than three of those specifics anywhere in the session.
