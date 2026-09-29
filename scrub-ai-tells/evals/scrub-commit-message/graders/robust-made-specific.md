---
type: llm
focus: last_message
---

The original said retries "make uploads more robust". The skill's table lists "Robust (when
vague)": delete it or be specific.

PASS if the word "robust" is gone, or if where it remains the same sentence (or the next one)
names the specific failure the change survives (a 503 from the storage API, a transient
error, a dead endpoint).

FAIL if "robust" survives as a bare adjective with no specific failure named nearby.
