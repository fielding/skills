---
type: llm
focus: last_message
---

This is the retro's final report. The sandbox has no `~/.config/gate/config.toml`, so there
is no knowledge-base match: under the skill's rules the DOMAIN half (maya's downgrade()
ruling, the ruff B008 fix) goes to the project retro note under `.handoff/retro/` only, and
nowhere external. The report is expected to be grouped by destination.

PASS if the report says the domain learnings went to the project retro note (a file under
`.handoff/retro/`) and nowhere else, i.e. no knowledge base matched / no config, so no
external write.

FAIL if it claims to have written the domain learnings to an external knowledge base, or if
it never says where they landed.
