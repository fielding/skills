---
type: llm
focus: { source: file, path: "draft.md" }
---

The original said "comprehensive error handling ensures robust operation even when the
upstream API is flaky". The skill's table lists "Robust (when vague)": delete it or be specific.

PASS if the word "robust" is gone from the file, or if where it remains the same sentence names
what the handling actually does (retries, resumes after a network failure, survives a flaky
upstream API).

FAIL if "robust operation" or a bare "robust" survives with nothing specific in the sentence.
