---
type: regex
target: trace
pattern: '\\?"name\\?"\s*:\s*\\?"(?:Task|Agent)\\?"\s*,\s*\\?"input\\?"\s*:\s*\{[^\n]{0,3000}?prompts/(?:py|ts)0[123]_'
match: not_contains
---
