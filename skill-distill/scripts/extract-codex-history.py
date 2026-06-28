#!/usr/bin/env python3
"""
extract-codex-history.py
Extracts user prompts from Codex CLI session transcripts and outputs
normalized JSONL.

Codex stores sessions at:
    ~/.codex/history.jsonl           — lightweight session index
    ~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl — full transcripts

This script reads both sources. The history index is used for fast
scanning; full transcripts are read when --full-transcripts is set.

Usage:
    python3 extract-codex-history.py [options]

Options:
    --days N                Only include sessions from the last N days
    --project PATH          Filter to sessions from a project path
                            (partial match against session working directory)
    --sessions-dir PATH     Override sessions directory
                            (default: ~/.codex/sessions)
    --history-file PATH     Override history index file
                            (default: ~/.codex/history.jsonl)
    --full-transcripts      Also read full session .jsonl transcripts
                            for richer content (slower)
    --output PATH           Write output to file instead of stdout
    --stats                 Print summary stats to stderr
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

def get_codex_dir() -> Path:
    return Path.home() / ".codex"

def normalize_ts(ts) -> int:
    """Normalize any timestamp representation to milliseconds."""
    if not ts:
        return 0
    if isinstance(ts, str):
        try:
            dt = datetime.fromisoformat(ts.rstrip("Z"))
            return int(dt.replace(tzinfo=timezone.utc).timestamp() * 1000)
        except Exception:
            return 0
    val = int(ts)
    if val < 32503680000:
        return val * 1000
    return val

def read_history_index(history_file: Path, cutoff_ms: int | None,
                       project_filter: str | None) -> list[dict]:
    """
    Read ~/.codex/history.jsonl — the lightweight session index.
    Each line is a JSON object. Known fields vary by Codex version but
    typically include: sessionId, firstPrompt/prompt, timestamp/createdAt,
    workingDir/cwd/project, model.
    """
    if not history_file.exists():
        return []

    messages = []
    try:
        with open(history_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                ts = normalize_ts(
                    entry.get("timestamp")
                    or entry.get("createdAt")
                    or entry.get("created_at")
                    or entry.get("ts")
                    or 0
                )
                if cutoff_ms and ts < cutoff_ms:
                    continue

                # Extract working directory (project)
                project = (
                    entry.get("workingDir")
                    or entry.get("cwd")
                    or entry.get("project")
                    or entry.get("workspaceDir")
                    or ""
                )

                if project_filter and project_filter.lower() not in project.lower():
                    continue

                # Extract the prompt text. Current Codex history.jsonl uses
                # "text"; older/other versions used firstPrompt/prompt/etc.
                prompt = (
                    entry.get("text")
                    or entry.get("firstPrompt")
                    or entry.get("prompt")
                    or entry.get("display")
                    or entry.get("message")
                    or entry.get("title")
                    or ""
                )
                prompt = prompt.strip()
                if not prompt:
                    continue
                if _is_injected(prompt):
                    continue

                session_id = (
                    entry.get("session_id")
                    or entry.get("sessionId")
                    or entry.get("id")
                    or ""
                )

                messages.append({
                    "source": "codex",
                    "display": prompt,
                    "timestamp": ts,
                    "project": project,
                    "sessionId": str(session_id),
                })
    except (OSError, IOError) as e:
        print(f"WARN: Could not read {history_file}: {e}", file=sys.stderr)

    return messages

def find_transcript_files(sessions_dir: Path, cutoff_mtime: float | None) -> list[Path]:
    """Find all rollout-*.jsonl transcript files in the date-organized sessions dir."""
    if not sessions_dir.exists():
        return []

    files = []
    for f in sessions_dir.rglob("rollout-*.jsonl"):
        if cutoff_mtime and f.stat().st_mtime < cutoff_mtime:
            continue
        files.append(f)
    return sorted(files, reverse=True)  # newest first

# Prefixes that mark machine-injected "user" turns (environment context,
# repo AGENTS.md instructions, IDE state). These are role:user in the rollout
# log but are not things the human actually typed, so we drop them.
INJECTED_PREFIXES = (
    "<environment_context>",
    "<user_instructions>",
    "# AGENTS.md",
    "# Context from my IDE",
)

def _is_injected(text: str) -> bool:
    t = text.lstrip()
    return any(t.startswith(p) for p in INJECTED_PREFIXES)

def extract_from_transcript(path: Path, cutoff_ms: int | None,
                             project_filter: str | None) -> list[dict]:
    """
    Read a full Codex session transcript JSONL file.

    Current Codex (codex_cli_rs) rollout format: each line is a JSON object
    with a top-level "type" and a "payload" object. The first line is
    type="session_meta" carrying payload.cwd. Conversation turns are
    type="response_item" whose payload is an OpenAI Responses-style item:
        {"type": "message", "role": "user"|"assistant",
         "content": [{"type": "input_text"|"output_text", "text": "..."}]}

    We extract payload role=="user" messages, joining input_text/text blocks,
    and skip machine-injected context turns (see INJECTED_PREFIXES).
    """
    messages = []
    session_id = path.stem  # e.g. "rollout-2025-03-15T10-30-00-abc123"
    working_dir = ""

    try:
        with open(path, "r", encoding="utf-8") as f:
            for lineno, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                entry_type = entry.get("type", "")
                payload = entry.get("payload")
                payload = payload if isinstance(payload, dict) else {}

                # Session metadata header carries the working directory.
                if entry_type in ("session_meta", "session_start",
                                  "metadata", "header", "init"):
                    working_dir = (
                        payload.get("cwd")
                        or payload.get("workingDir")
                        or payload.get("project")
                        or entry.get("workingDir")
                        or entry.get("cwd")
                        or entry.get("project")
                        or working_dir
                    )
                    continue

                # Conversation items live under payload for response_item
                # entries; fall back to the top-level entry for older formats.
                item = payload if payload else entry
                item_type = item.get("type", "")
                role = item.get("role", "")
                is_user = (
                    role in ("user", "human")
                    or item_type in ("user", "human")
                    or (item_type == "message" and role in ("user", "human"))
                )
                if not is_user:
                    continue

                content = (
                    item.get("content")
                    or item.get("text")
                    or item.get("message")
                    or ""
                )
                if isinstance(content, list):
                    parts = []
                    for block in content:
                        if isinstance(block, dict):
                            # Codex uses input_text/output_text; keep any text.
                            parts.append(block.get("text", ""))
                        elif isinstance(block, str):
                            parts.append(block)
                    content = " ".join(p for p in parts if p)
                content = str(content).strip()
                if not content:
                    continue
                if _is_injected(content):
                    continue

                ts = normalize_ts(
                    entry.get("timestamp")
                    or entry.get("createdAt")
                    or item.get("timestamp")
                    or 0
                )
                if cutoff_ms and ts < cutoff_ms:
                    continue

                messages.append({
                    "source": "codex",
                    "display": content,
                    "timestamp": ts,
                    "project": working_dir,
                    "sessionId": session_id,
                })
    except (OSError, IOError) as e:
        print(f"WARN: Could not read {path}: {e}", file=sys.stderr)

    # Apply project filter (working_dir may only be known after reading the file)
    if project_filter:
        messages = [m for m in messages
                    if project_filter.lower() in m.get("project", "").lower()]

    return messages

def parse_args():
    p = argparse.ArgumentParser(
        description="Extract Codex CLI session history to normalized JSONL"
    )
    p.add_argument("--days", type=int, default=None,
                   help="Only include sessions from the last N days")
    p.add_argument("--project", default=None,
                   help="Filter to sessions from a project path (partial match)")
    p.add_argument("--sessions-dir", default=None,
                   help="Override sessions directory (default: ~/.codex/sessions)")
    p.add_argument("--history-file", default=None,
                   help="Override history index file (default: ~/.codex/history.jsonl)")
    # Full transcripts are now the source of truth: the lightweight
    # history.jsonl index goes stale and only carries the first prompt of a
    # session. Read transcripts by default; --no-full-transcripts falls back
    # to the index alone.
    p.add_argument("--full-transcripts", dest="full_transcripts",
                   action="store_true", default=True,
                   help="Read full session transcript files (default)")
    p.add_argument("--no-full-transcripts", dest="full_transcripts",
                   action="store_false",
                   help="Skip transcripts; read only the history.jsonl index")
    p.add_argument("--output", default=None,
                   help="Write output to file instead of stdout")
    p.add_argument("--stats", action="store_true",
                   help="Print summary stats to stderr")
    return p.parse_args()

def main():
    args = parse_args()

    codex_dir = get_codex_dir()
    history_file = Path(args.history_file) if args.history_file else codex_dir / "history.jsonl"
    sessions_dir = Path(args.sessions_dir) if args.sessions_dir else codex_dir / "sessions"

    if not codex_dir.exists():
        print(f"ERROR: Codex directory not found: {codex_dir}", file=sys.stderr)
        print("Is Codex CLI installed?", file=sys.stderr)
        sys.exit(1)

    cutoff_ms = None
    cutoff_mtime = None
    if args.days is not None:
        cutoff_mtime = time.time() - args.days * 86400
        cutoff_ms = int(cutoff_mtime * 1000)

    project_filter = args.project
    all_messages = []

    # Full transcripts are the source of truth. The history.jsonl index is
    # stale (only updated through older sessions) and its session ids are bare
    # UUIDs that don't line up with the transcript file stems, so mixing the
    # two would double-count. Use the index only when transcripts are disabled.
    if args.full_transcripts:
        transcript_files = find_transcript_files(sessions_dir, cutoff_mtime)
        if args.stats:
            print(f"Transcript files: {len(transcript_files)}", file=sys.stderr)

        for tf in transcript_files:
            msgs = extract_from_transcript(tf, cutoff_ms, project_filter)
            all_messages.extend(msgs)
    else:
        index_msgs = read_history_index(history_file, cutoff_ms, project_filter)
        if args.stats:
            print(f"History index: {len(index_msgs)} entries", file=sys.stderr)
        all_messages.extend(index_msgs)

    # Deduplicate by (sessionId, display[:80])
    seen = set()
    deduped = []
    for m in all_messages:
        key = (m["sessionId"], m["display"][:80])
        if key not in seen:
            seen.add(key)
            deduped.append(m)

    deduped.sort(key=lambda m: m["timestamp"])

    # Output
    out = open(args.output, "w", encoding="utf-8") if args.output else sys.stdout
    try:
        for msg in deduped:
            print(json.dumps(msg, ensure_ascii=False), file=out)
    finally:
        if args.output:
            out.close()

    if args.stats:
        print(f"Total extracted: {len(deduped)} user messages from Codex CLI",
              file=sys.stderr)
        if cutoff_ms:
            dt = datetime.fromtimestamp(cutoff_ms / 1000, tz=timezone.utc)
            print(f"  Time filter: after {dt.strftime('%Y-%m-%d %H:%M UTC')}",
                  file=sys.stderr)
        if project_filter:
            print(f"  Project filter: '{project_filter}'", file=sys.stderr)

if __name__ == "__main__":
    main()
