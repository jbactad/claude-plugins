"""Incremental transcript capture shared by the SessionEnd, PreCompact and Stop hooks.

Each session keeps a cursor: the byte offset in its transcript up to which turns have
already been handed to the flush agent. A capture reads only what lies past the cursor,
so every turn is summarized exactly once, however long the session runs, and nothing
depends on the session ending.

Unflushed turns are grouped by the LOCAL DATE they happened on and packed into chunks
small enough for one flush call. Each chunk lands in that date's daily log, so a session
left open overnight files yesterday's work under yesterday.

No API calls here: hooks must stay fast. The summarizing happens in flush.py, spawned
as a background process with a manifest describing the chunks.
"""

from __future__ import annotations

import json
import logging
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from config import DATA_DIR, SCRIPTS_DIR, VAULT_CONFIGURED
from shared import file_lock, read_json, write_json_atomic

CURSOR_DIR = DATA_DIR / "cursors"
PENDING_DIR = DATA_DIR / "pending"

MAX_CONTEXT_CHARS = 15_000  # one flush call
MAX_TURN_CHARS = 4_000  # a single huge message must not crowd out the rest of a chunk
# A session first seen with a long backlog (e.g. started before this version) would
# otherwise fan out into dozens of flush calls; keep the most recent chunks only.
MAX_CHUNKS_PER_CAPTURE = 4

# A session untouched this long will not resume; its cursor and lock files can go.
CURSOR_MAX_AGE_DAYS = 14

SYSTEM_REMINDER_RE = re.compile(r"<system-reminder>.*?</system-reminder>", re.DOTALL)


@dataclass
class Turn:
    at: datetime  # local, timezone-aware
    role: str
    text: str
    cwd: str
    branch: str


@dataclass
class Chunk:
    date: str
    turns: list[Turn]


def read_hook_input() -> dict | None:
    raw = sys.stdin.read()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Windows paths arrive with unescaped backslashes.
        fixed = re.sub(r'(?<!\\)\\(?!["\\])', r"\\\\", raw)
        try:
            return json.loads(fixed)
        except json.JSONDecodeError as e:
            logging.error("Failed to parse stdin: %s", e)
            return None


def _parse_timestamp(value: object, fallback: datetime) -> datetime:
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone()
        except ValueError:
            pass
    return fallback


def _entry_text(entry: dict) -> tuple[str, str]:
    """Return (role, text) for a conversational entry, or ("", "") for anything else."""
    # Sidechains are sub-agent runs, meta entries are injected skill bodies, compact
    # summaries restate turns that were already captured.
    if entry.get("isSidechain") or entry.get("isMeta") or entry.get("isCompactSummary"):
        return "", ""

    msg = entry.get("message")
    if not isinstance(msg, dict):
        return "", ""
    role = msg.get("role", "")
    if role not in ("user", "assistant"):
        return "", ""

    content = msg.get("content", "")
    if isinstance(content, list):
        content = "\n".join(
            block.get("text", "") if isinstance(block, dict) and block.get("type") == "text"
            else block if isinstance(block, str) else ""
            for block in content
        )
    if not isinstance(content, str):
        return "", ""

    text = SYSTEM_REMINDER_RE.sub("", content).strip()
    if len(text) > MAX_TURN_CHARS:
        text = text[:MAX_TURN_CHARS].rstrip() + " …[truncated]"
    return role, text


def read_new_turns(transcript: Path, offset: int) -> tuple[list[Turn], int]:
    """Parse the complete lines past `offset`. Returns the turns and the new offset."""
    size = transcript.stat().st_size
    if offset > size:  # transcript replaced or truncated: start over
        offset = 0
    with open(transcript, "rb") as f:
        f.seek(offset)
        data = f.read()

    # The transcript is being appended to as we read; stop at the last complete line.
    end = data.rfind(b"\n") + 1
    turns: list[Turn] = []
    last_at = datetime.now(timezone.utc).astimezone()
    for raw in data[:end].splitlines():
        try:
            entry = json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(entry, dict):
            continue
        last_at = _parse_timestamp(entry.get("timestamp"), last_at)
        role, text = _entry_text(entry)
        if text:
            turns.append(Turn(last_at, role, text, entry.get("cwd", ""), entry.get("gitBranch", "")))
    return turns, offset + end


def _format_turn(turn: Turn) -> str:
    label = "User" if turn.role == "user" else "Assistant"
    return f"**{label}:** {turn.text}\n"


def build_chunks(turns: list[Turn]) -> list[Chunk]:
    chunks: list[Chunk] = []
    size = 0
    for turn in turns:
        date = turn.at.strftime("%Y-%m-%d")
        cost = len(_format_turn(turn)) + 1
        if not chunks or chunks[-1].date != date or size + cost > MAX_CONTEXT_CHARS:
            chunks.append(Chunk(date, []))
            size = 0
        chunks[-1].turns.append(turn)
        size += cost
    return chunks


def _location(turns: list[Turn]) -> str:
    last = turns[-1]
    parts = [Path(last.cwd).name if last.cwd else "", last.branch if last.branch not in ("", "HEAD") else ""]
    return " · ".join(p for p in parts if p)


def _spawn_flush(manifest_path: Path) -> None:
    plugin_dir = SCRIPTS_DIR.parent
    cmd = ["uv", "run", "--directory", str(plugin_dir), "python", str(SCRIPTS_DIR / "flush.py"), str(manifest_path)]
    # Do NOT use DETACHED_PROCESS or start_new_session — it breaks the Agent SDK's subprocess I/O.
    creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=creation_flags)


def prune_cursors() -> None:
    """Delete cursor and lock files of sessions untouched for CURSOR_MAX_AGE_DAYS."""
    if not CURSOR_DIR.exists():
        return
    cutoff = time.time() - CURSOR_MAX_AGE_DAYS * 86_400
    for path in CURSOR_DIR.iterdir():
        try:
            if path.stat().st_mtime < cutoff:
                path.unlink()
        except OSError:
            pass


def capture(hook_input: dict, reason: str, should_flush: Callable[[list[Turn]], bool]) -> None:
    """Hand every unflushed turn of the session to the flush agent, if `should_flush` agrees."""
    if not VAULT_CONFIGURED:
        logging.info("SKIP: no vault configured (OBSIDIAN_VAULT_PATH not set, not in vault dir)")
        return

    session_id = hook_input.get("session_id", "unknown")
    transcript_str = hook_input.get("transcript_path", "")
    # transcript_path can be empty (known Claude Code bug #13668)
    if not transcript_str:
        logging.info("SKIP %s: no transcript path (session=%s)", reason, session_id)
        return
    transcript = Path(transcript_str)
    if not transcript.exists():
        logging.info("SKIP %s: transcript missing: %s", reason, transcript_str)
        return

    cursor_path = CURSOR_DIR / f"{session_id}.json"
    # Stop and SessionEnd can fire together; the lock keeps them from both claiming the same turns.
    with file_lock(cursor_path):
        offset = int(read_json(cursor_path).get("offset", 0))
        try:
            turns, new_offset = read_new_turns(transcript, offset)
        except OSError as e:
            logging.error("Transcript read failed for session %s: %s", session_id, e)
            return

        if not turns:
            if new_offset != offset:
                write_json_atomic(cursor_path, {"offset": new_offset})
            return
        if not should_flush(turns):
            return  # cursor stays put; these turns are picked up by a later capture

        chunks = build_chunks(turns)
        if len(chunks) > MAX_CHUNKS_PER_CAPTURE:
            dropped = chunks[:-MAX_CHUNKS_PER_CAPTURE]
            logging.warning(
                "Session %s: backlog of %d chunks, dropping the oldest %d (%s to %s)",
                session_id, len(chunks), len(dropped), dropped[0].date, dropped[-1].date,
            )
            chunks = chunks[-MAX_CHUNKS_PER_CAPTURE:]

        stamp = datetime.now(timezone.utc).astimezone().strftime("%Y%m%d-%H%M%S")
        PENDING_DIR.mkdir(parents=True, exist_ok=True)
        manifest_chunks = []
        for i, chunk in enumerate(chunks):
            context_file = PENDING_DIR / f"{session_id}-{stamp}-{i}.md"
            context_file.write_text("\n".join(_format_turn(t) for t in chunk.turns), encoding="utf-8")
            manifest_chunks.append({
                "date": chunk.date,
                "start": chunk.turns[0].at.strftime("%H:%M"),
                "end": chunk.turns[-1].at.strftime("%H:%M"),
                "location": _location(chunk.turns),
                "file": str(context_file),
            })
        manifest_path = PENDING_DIR / f"{session_id}-{stamp}.json"
        write_json_atomic(manifest_path, {"session_id": session_id, "reason": reason, "chunks": manifest_chunks})

        try:
            _spawn_flush(manifest_path)
        except Exception as e:
            logging.error("Failed to spawn flush.py for session %s: %s", session_id, e)
            return  # cursor not advanced, so the next capture retries these turns

        write_json_atomic(cursor_path, {"offset": new_offset})
        logging.info(
            "%s: spawned flush for session %s (%d turns, %d chunks)",
            reason, session_id, len(turns), len(chunks),
        )
