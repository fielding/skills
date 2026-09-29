---
type: regex
target: { source: file, path: "intent.md" }
pattern: '^(?=[\s\S]*#+\s*What\b)(?=[\s\S]*#+\s*Why\b)(?=[\s\S]*#+\s*Scope\b)(?=[\s\S]*#+\s*Decisions\b)(?=[\s\S]*\bIn\b)(?=[\s\S]*\bOut\b)'
---

The four headings the skill specifies, with In/Out under Scope.
