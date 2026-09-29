"""JSON-backed note storage."""

import json
import os
import time
from pathlib import Path


class Store:
    def __init__(self, path: str | None = None):
        self.path = Path(path or os.path.expanduser("~/.notekeeper/notes.json"))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]")

    def _load(self) -> list[dict]:
        return json.loads(self.path.read_text())

    def _save(self, notes: list[dict]) -> None:
        self.path.write_text(json.dumps(notes, indent=2))

    def add(self, text: str, encrypted: bool = False) -> dict:
        notes = self._load()
        note = {
            "id": len(notes) + 1,
            "text": text,
            "encrypted": encrypted,
            "created": time.time(),
        }
        notes.append(note)
        self._save(notes)
        return note

    def list(self) -> list[dict]:
        return self._load()

    def search(self, query: str) -> list[dict]:
        q = query.lower()
        return [n for n in self._load() if q in n["text"].lower()]

    def export(self) -> str:
        return json.dumps(self._load(), indent=2)
