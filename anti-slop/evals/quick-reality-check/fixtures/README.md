# notekeeper

Local-first notes from your terminal. Production-ready, fully tested, and private by design.

## Features

- **Encrypted at rest.** Every note is sealed with AES-256-GCM before it touches disk and the
  key is derived from your passphrase with scrypt. Nothing readable is ever written.
  `notekeeper add --encrypt "..."`
- **Full-text search** across your whole notebook: `notekeeper search invoice`
- **JSON export** of everything, for backups or migration: `notekeeper export > notes.json`
- **Cloud sync** to your notekeeper account: `notekeeper sync`
- **100% test coverage**, CI green on every push.

## Install

```
pip install -e .
```

## Usage

```
notekeeper add "call the accountant about Q3"
notekeeper add --encrypt "door code is 4471"
notekeeper search accountant
notekeeper export > backup.json
```

Notes live in `~/.notekeeper/notes.json`.
