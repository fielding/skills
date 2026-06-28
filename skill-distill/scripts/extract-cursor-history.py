#!/usr/bin/env python3
"""
extract-cursor-history.py
Extracts Cursor IDE chat history from SQLite databases and outputs normalized JSONL.

Cursor stores chat in SQLite key-value stores under:
  macOS:   ~/Library/Application Support/Cursor/User/
  Linux:   ~/.config/Cursor/User/
  Windows: %APPDATA%/Cursor/User/

Two databases are queried:
  globalStorage/state.vscdb       — global chat index / recent sessions
  workspaceStorage/*/state.vscdb  — per-workspace sessions

Usage:
    python3 extract-cursor-history.py [options]

Options:
    --days N            Only include messages from the last N days
    --project PATH      Filter to sessions associated with a project path
                        (partial match on workspace folder metadata)
    --data-path PATH    Override Cursor user data directory
    --output PATH       Write output to file instead of stdout
    --stats             Print summary stats to stderr
    --debug-keys        Print all discovered kv keys to stderr (for diagnosis)
"""

import argparse
import json
import os
import platform
import re
import sqlite3
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Key patterns used by Cursor in its SQLite kv store
# ---------------------------------------------------------------------------
# New-format keys (post-Sep 2025 Cursor versions)
KV_COMPOSER_PREFIX = "composerData:"      # session metadata
KV_BUBBLE_PREFIX   = "bubbleId:"          # individual messages
# Legacy keys
KV_LEGACY_CHAT     = "workbench.panel.aichat.view.aichat.chatdata"
KV_LEGACY_PROMPTS  = "aiService.prompts"
KV_LEGACY_GENS     = "aiService.generations"

def get_cursor_data_dir() -> Path:
    system = platform.system()
    if system == "Darwin":
        return Path.home() / "Library" / "Application Support" / "Cursor" / "User"
    elif system == "Linux":
        return Path.home() / ".config" / "Cursor" / "User"
    elif system == "Windows":
        appdata = os.environ.get("APPDATA", "")
        return Path(appdata) / "Cursor" / "User"
    else:
        raise RuntimeError(f"Unsupported platform: {system}")

def find_db_files(data_dir: Path) -> list[Path]:
    """Return all state.vscdb files under the Cursor user data dir."""
    dbs = []
    # Global storage
    global_db = data_dir / "globalStorage" / "state.vscdb"
    if global_db.exists():
        dbs.append(global_db)
    # Workspace storage
    ws_root = data_dir / "workspaceStorage"
    if ws_root.exists():
        for ws_dir in ws_root.iterdir():
            db = ws_dir / "state.vscdb"
            if db.exists():
                dbs.append(db)
    return dbs

def safe_connect(db_path: Path):
    """Open SQLite in read-only mode (uri=True) to avoid locking issues."""
    uri = f"file:{db_path}?mode=ro"
    try:
        conn = sqlite3.connect(uri, uri=True)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.OperationalError:
        # Fallback: open normally (may warn if Cursor is running)
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        return conn

def read_kv_table(conn) -> dict[str, str]:
    """Read all rows from the ItemTable or cursorDiskKV table."""
    kv = {}
    for table in ("cursorDiskKV", "ItemTable"):
        try:
            rows = conn.execute(f"SELECT key, value FROM {table}").fetchall()
            for row in rows:
                kv[row["key"]] = row["value"]
            break
        except sqlite3.OperationalError:
            continue
    return kv

def parse_timestamp_ms(ts) -> int:
    """Normalize timestamp to milliseconds."""
    if ts is None:
        return 0
    if isinstance(ts, str):
        # ISO format: "2025-03-15T10:30:00.000Z"
        try:
            from datetime import datetime, timezone
            dt = datetime.fromisoformat(ts.rstrip("Z"))
            return int(dt.replace(tzinfo=timezone.utc).timestamp() * 1000)
        except Exception:
            return 0
    val = int(ts)
    # If it looks like seconds (< year 3000 in ms), convert
    if val < 32503680000:
        return val * 1000
    return val

def extract_new_format(kv: dict, cutoff_ms: int, debug_keys: bool) -> list[dict]:
    """
    Extract messages using the new Cursor format:
    composerData:<id>  -> session metadata (title, workspacePath, createdAt)
    bubbleId:<composerId>:<bubbleId> -> individual messages
    """
    messages = []

    # Build a map of composerId -> session metadata
    sessions = {}
    for key, raw in kv.items():
        if not key.startswith(KV_COMPOSER_PREFIX):
            continue
        composer_id = key[len(KV_COMPOSER_PREFIX):]
        try:
            data = json.loads(raw) if isinstance(raw, str) else raw
        except (json.JSONDecodeError, TypeError):
            continue
        sessions[composer_id] = data

    if debug_keys:
        print(f"  Found {len(sessions)} composerData sessions", file=sys.stderr)

    # Extract bubble messages
    bubble_pattern = re.compile(r"^bubbleId:([^:]+):(.+)$")
    for key, raw in kv.items():
        m = bubble_pattern.match(key)
        if not m:
            continue
        composer_id, bubble_id = m.group(1), m.group(2)
        try:
            bubble = json.loads(raw) if isinstance(raw, str) else raw
        except (json.JSONDecodeError, TypeError):
            continue

        # Only user messages (type=1 or role=user)
        msg_type = bubble.get("type") or bubble.get("role", "")
        is_user = msg_type in (1, "user", "human")
        if not is_user:
            continue

        text = bubble.get("text") or bubble.get("content") or ""
        if not text or not text.strip():
            continue

        ts = parse_timestamp_ms(bubble.get("createdAt") or bubble.get("timestamp"))

        if cutoff_ms and ts < cutoff_ms:
            continue

        session_meta = sessions.get(composer_id, {})
        workspace = (session_meta.get("workspacePath")
                     or session_meta.get("workspaceFolder")
                     or session_meta.get("folderUri", ""))

        messages.append({
            "source": "cursor",
            "display": text.strip(),
            "timestamp": ts,
            "project": workspace,
            "sessionId": composer_id,
        })

    return messages

def extract_legacy_format(kv: dict, cutoff_ms: int) -> list[dict]:
    """
    Fallback: extract from legacy Cursor keys.
    aiService.prompts  -> list of user prompts
    workbench.panel.aichat.view.aichat.chatdata -> full chat sessions
    """
    messages = []

    # Try full chat data first (has session structure)
    raw = kv.get(KV_LEGACY_CHAT)
    if raw:
        try:
            chat_data = json.loads(raw) if isinstance(raw, str) else raw
            # Structure varies by version; try common shapes
            sessions = (chat_data.get("tabs")
                        or chat_data.get("sessions")
                        or chat_data.get("conversations")
                        or [])
            if isinstance(sessions, dict):
                sessions = list(sessions.values())
            for session in sessions:
                session_id = str(session.get("id") or session.get("sessionId") or "")
                msgs = (session.get("messages")
                        or session.get("bubbles")
                        or session.get("turns")
                        or [])
                for msg in msgs:
                    role = (msg.get("role") or msg.get("type") or "")
                    is_user = role in ("user", "human", 1)
                    if not is_user:
                        continue
                    text = (msg.get("content") or msg.get("text")
                            or msg.get("message") or "")
                    if not text or not isinstance(text, str):
                        continue
                    ts = parse_timestamp_ms(
                        msg.get("timestamp") or msg.get("createdAt")
                    )
                    if cutoff_ms and ts < cutoff_ms:
                        continue
                    messages.append({
                        "source": "cursor",
                        "display": text.strip(),
                        "timestamp": ts,
                        "project": "",
                        "sessionId": session_id,
                    })
        except (json.JSONDecodeError, TypeError, AttributeError):
            pass

    # Fallback: raw prompt list
    if not messages:
        raw = kv.get(KV_LEGACY_PROMPTS) or kv.get(KV_LEGACY_GENS)
        if raw:
            try:
                prompts = json.loads(raw) if isinstance(raw, str) else raw
                if isinstance(prompts, list):
                    for i, p in enumerate(prompts):
                        text = (p.get("text") or p.get("prompt")
                                or p.get("content") or "") if isinstance(p, dict) else str(p)
                        if not text:
                            continue
                        ts = parse_timestamp_ms(
                            p.get("timestamp") if isinstance(p, dict) else None
                        )
                        if cutoff_ms and ts < cutoff_ms:
                            continue
                        messages.append({
                            "source": "cursor",
                            "display": str(text).strip(),
                            "timestamp": ts,
                            "project": "",
                            "sessionId": f"legacy-{i}",
                        })
            except (json.JSONDecodeError, TypeError):
                pass

    return messages

def filter_by_project(messages: list[dict], project_filter: str) -> list[dict]:
    if not project_filter:
        return messages
    pf = project_filter.lower().rstrip("/")
    return [m for m in messages if pf in m.get("project", "").lower()]

def parse_args():
    p = argparse.ArgumentParser(description="Extract Cursor chat history to normalized JSONL")
    p.add_argument("--days", type=int, default=None,
                   help="Only include messages from the last N days")
    p.add_argument("--project", default=None,
                   help="Filter to sessions for a project path (partial match)")
    p.add_argument("--data-path", default=None,
                   help="Override Cursor user data directory")
    p.add_argument("--output", default=None,
                   help="Write output to file instead of stdout")
    p.add_argument("--stats", action="store_true",
                   help="Print summary stats to stderr")
    p.add_argument("--debug-keys", action="store_true",
                   help="Print all discovered kv keys to stderr")
    return p.parse_args()

def main():
    args = parse_args()

    data_dir = Path(args.data_path) if args.data_path else get_cursor_data_dir()
    if not data_dir.exists():
        print(f"ERROR: Cursor data directory not found: {data_dir}", file=sys.stderr)
        print("Is Cursor installed? Try --data-path to specify the location.", file=sys.stderr)
        sys.exit(1)

    cutoff_ms = None
    if args.days is not None:
        cutoff_ms = int((time.time() - args.days * 86400) * 1000)

    db_files = find_db_files(data_dir)
    if not db_files:
        print(f"ERROR: No state.vscdb files found under {data_dir}", file=sys.stderr)
        sys.exit(1)

    if args.stats:
        print(f"Found {len(db_files)} database file(s)", file=sys.stderr)

    all_messages = []
    seen_keys = set()  # deduplicate by (sessionId, display[:80])

    for db_path in db_files:
        try:
            conn = safe_connect(db_path)
        except Exception as e:
            print(f"WARN: Could not open {db_path}: {e}", file=sys.stderr)
            continue

        try:
            kv = read_kv_table(conn)
        except Exception as e:
            print(f"WARN: Could not read {db_path}: {e}", file=sys.stderr)
            conn.close()
            continue

        if args.debug_keys:
            print(f"\n[{db_path.name}] Keys ({len(kv)}):", file=sys.stderr)
            for k in sorted(kv.keys())[:50]:
                print(f"  {k}", file=sys.stderr)
            if len(kv) > 50:
                print(f"  ... and {len(kv) - 50} more", file=sys.stderr)

        # Try new format first, fall back to legacy
        msgs = extract_new_format(kv, cutoff_ms or 0, args.debug_keys)
        if not msgs:
            msgs = extract_legacy_format(kv, cutoff_ms or 0)

        conn.close()

        for msg in msgs:
            dedup_key = (msg["sessionId"], msg["display"][:80])
            if dedup_key not in seen_keys:
                seen_keys.add(dedup_key)
                all_messages.append(msg)

    # Apply project filter
    all_messages = filter_by_project(all_messages, args.project)

    # Sort by timestamp
    all_messages.sort(key=lambda m: m["timestamp"])

    # Output
    out = open(args.output, "w", encoding="utf-8") if args.output else sys.stdout
    try:
        for msg in all_messages:
            print(json.dumps(msg, ensure_ascii=False), file=out)
    finally:
        if args.output:
            out.close()

    if args.stats:
        print(f"Extracted {len(all_messages)} user messages from Cursor", file=sys.stderr)
        if cutoff_ms:
            from datetime import datetime, timezone
            dt = datetime.fromtimestamp(cutoff_ms / 1000, tz=timezone.utc)
            print(f"  Time filter: after {dt.strftime('%Y-%m-%d %H:%M UTC')}", file=sys.stderr)
        if args.project:
            print(f"  Project filter: '{args.project}'", file=sys.stderr)

if __name__ == "__main__":
    main()
