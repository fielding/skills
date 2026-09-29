---
type: regex
target: { source: file, path: ".antislop/VERDICT.md" }
pattern: 'Substance Score[^\n]{0,12}\d{1,3}\s*/\s*100[^\n]{0,24}(Real|Mostly[- ]real|Mirage|Abandon)'
flags: i
match: contains
---
