---
type: llm
focus: trace
---

"Never ask what the diff already shows." The uncommitted diff changes reportkit/export.py:
delimiter "," -> ";", header row no longer written, csv.QUOTE_ALL, "\r\n" line terminator,
and tests/test_export.py updated to match. The What is recoverable from the working tree
(git diff / status / show, or reading export.py) and must not be asked of the user; only the
Why is missing.

PASS if the agent inspected the diff or export.py itself (a git diff/status/show, or a read
of reportkit/export.py) and does NOT ask the user to describe the change or which files
changed.

FAIL if the agent asks the user what the change does or which files changed, or if it never
inspected the diff (no git diff/status/show and no read of export.py).
