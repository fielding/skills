---
type: regex
target: last_message
pattern: '\b(leverages?|leveraging|in order to|it[''’]s worth noting|worth noting|additionally|this ensures that|seamless\w*)\b'
flags: i
match: not_contains
---

Each phrase is an unconditional entry in the skill's "Always remove" table and was planted in
the message. ("robust" is "when vague" in the table, so it is a judgment call with its own
llm grader, not a regex.)
