#!/usr/bin/env python3
"""
Background memory flush agent — extracts important knowledge from a conversation
transcript and appends it to today's daily log.

Spawned by the SessionEnd, PreCompact and Stop hooks (via capture.py) as a background
process. Uses the Claude Agent SDK to decide what's worth saving.

Usage:
    python flush.py <manifest.json>

The manifest lists one or more chunks of not-yet-captured turns, each with the local
date its turns happened on. Each chunk is summarized separately and appended to that
date's daily log.
"""

from __future__ import annotations

# Recursion prevention: set BEFORE any imports that might trigger Claude.
import os
os.environ["CLAUDE_INVOKED_BY"] = "memory_flush"

import asyncio
import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import DAILY_DIR, PLUGIN_DIR, SCRIPTS_DIR, today_iso
from shared import file_lock, read_json

COMPILE_AFTER_HOUR = 18  # 6 PM local time

# Sentinel the flush agent returns when a session holds nothing worth recording.
# Matched exactly against the stripped response — a substring match would discard
# any entry that merely mentions the sentinel.
SENTINEL_NOTHING = "NOTHING_TO_SAVE"

# Plugins may prefix agent output (e.g. message-timestamps emits "[18:53:58] ").
# Stripped before sentinel matching and before the entry reaches the vault.
PREFIX_RE = re.compile(r"^\s*\[\d{1,2}:\d{2}(?::\d{2})?\]\s*")

# Every real entry opens with this heading. The agent sometimes writes the sentinel,
# then reconsiders in prose ("Wait — that's wrong...") before or instead of writing
# the entry; anything ahead of the heading is that chatter, never knowledge.
ENTRY_START = "**Context:**"


def parse_entry(response: str) -> tuple[str, bool]:
    """Turn the agent's raw reply into a vault entry.

    Returns (entry, reconsidered). An empty entry means nothing should be written.
    `reconsidered` is True when the agent opened with the sentinel but then kept
    talking without producing an entry: it changed its mind, so a retry is warranted.
    """
    text = PREFIX_RE.sub("", response).strip()
    start = text.find(ENTRY_START)
    if start != -1:
        return text[start:].strip(), False
    if text == SENTINEL_NOTHING:
        return "", False
    if text.startswith(SENTINEL_NOTHING):
        return "", True
    return text, False

logging.basicConfig(
    filename=str(SCRIPTS_DIR / "flush.log"),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [flush] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def entry_heading(chunk: dict) -> str:
    """`### Session (09:12–10:40) · backend · feature/x` — when and where the turns happened."""
    start, end = chunk.get("start", ""), chunk.get("end", "")
    span = start if start == end else f"{start}–{end}"
    location = chunk.get("location", "")
    return f"### Session ({span})" + (f" · {location}" if location else "")


def append_to_daily_log(content: str, date: str, heading: str) -> None:
    """Append a session entry to the daily log for `date` (YYYY-MM-DD)."""
    log_path = DAILY_DIR / f"{date}.md"
    DAILY_DIR.mkdir(parents=True, exist_ok=True)

    # Parallel sessions flush concurrently; serialize writers so entries never interleave
    # and the header is written exactly once.
    with file_lock(log_path):
        if not log_path.exists():
            log_path.write_text(f"# Daily Log: {date}\n\n## Sessions\n\n", encoding="utf-8")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"{heading}\n\n{content}\n\n")


RETRY_NOTE = f"""A previous attempt answered {SENTINEL_NOTHING} and then said the session
did hold content worth recording. Write the entry now, starting with {ENTRY_START}

"""


async def run_flush(context: str, preamble: str = "") -> str:
    """Use Claude Agent SDK to extract worth-keeping knowledge from conversation context."""
    from claude_agent_sdk import (
        AssistantMessage,
        ClaudeAgentOptions,
        ResultMessage,
        TextBlock,
        query,
    )

    prompt = preamble + f"""Extract the durable knowledge from the conversation below into an entry
for the daily knowledge log. Do NOT use any tools — return plain text only.

Default to saving. A real work session almost always contains something worth keeping:
what was being worked on, what was decided, what was learned, what is still open.
Write the entry unless the conversation is genuinely empty of content.

Format your response as a structured entry with these sections (omit empty ones):

**Context:** [One line about what was being worked on]

**Key Exchanges:**
- [Important Q&A or discussions worth remembering]

**Decisions Made:**
- [Decisions with rationale]

**Lessons Learned:**
- [Gotchas, patterns, or insights discovered]

**Action Items:**
- [ ] [Follow-ups or TODOs mentioned]

Leave out routine tool calls, file reads, and clarifications that carry no knowledge —
but their presence is not a reason to discard the session. Summarize what remains.

Respond with exactly {SENTINEL_NOTHING} only when there is nothing at all to record:
a bare greeting, an aborted session with no work, or context with no factual content.

Decide before you write. Your reply is either the entry, starting with {ENTRY_START},
or the single word {SENTINEL_NOTHING} and nothing else. Never write the sentinel and
then reconsider; never add commentary before or after the entry.

## Conversation Context

{context}"""

    stderr_lines: list[str] = []

    def _capture_stderr(line: str) -> None:
        stderr_lines.append(line)

    response = ""
    try:
        async for message in query(
            prompt=prompt,
            options=ClaudeAgentOptions(
                cwd=str(PLUGIN_DIR),
                allowed_tools=[],
                max_turns=2,
                stderr=_capture_stderr,
                # Judge the transcript on its own terms. Without this the agent inherits
                # the user's CLAUDE.md, hooks, and output-style plugins, which pull the
                # summary toward whatever tone/brevity those enforce.
                setting_sources=[],
            ),
        ):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        response += block.text
            elif isinstance(message, ResultMessage):
                pass
    except Exception as e:
        import traceback
        stderr_output = "\n".join(stderr_lines[-20:]) if stderr_lines else "(no stderr)"
        logging.error("Agent SDK error: %s\nstderr: %s\n%s", e, stderr_output, traceback.format_exc())
        response = f"FLUSH_ERROR: {type(e).__name__}: {e}"

    return response


def maybe_trigger_compilation() -> None:
    """If it's past 6 PM and today's daily log hasn't been compiled, trigger compile.py."""
    import subprocess as sp

    now = datetime.now(timezone.utc).astimezone()
    if now.hour < COMPILE_AFTER_HOUR:
        return

    today_log = f"{today_iso()}.md"
    state_file = SCRIPTS_DIR / "state.json"
    if state_file.exists():
        try:
            state = json.loads(state_file.read_text(encoding="utf-8"))
            ingested = state.get("ingested", {})
            if today_log in ingested:
                from utils import file_hash
                log_path = DAILY_DIR / today_log
                if log_path.exists():
                    if ingested[today_log].get("hash") == file_hash(log_path):
                        return  # already compiled and unchanged
        except (json.JSONDecodeError, OSError):
            pass

    compile_script = SCRIPTS_DIR / "compile.py"
    if not compile_script.exists():
        return

    logging.info("Triggering end-of-day compilation (after %d:00)", COMPILE_AFTER_HOUR)

    cmd = ["uv", "run", "--directory", str(PLUGIN_DIR), "python", str(compile_script), "--source", "daily"]
    kwargs: dict = {}
    if sys.platform == "win32":
        kwargs["creationflags"] = sp.CREATE_NO_WINDOW

    try:
        log_handle = open(str(SCRIPTS_DIR / "compile.log"), "a")
        sp.Popen(cmd, stdout=log_handle, stderr=sp.STDOUT, cwd=str(PLUGIN_DIR), **kwargs)
    except Exception as e:
        logging.error("Failed to spawn compile.py: %s", e)


def flush_chunk(session_id: str, chunk: dict) -> None:
    context_file = Path(chunk["file"])
    if not context_file.exists():
        logging.error("Context file not found: %s", context_file)
        return

    context = context_file.read_text(encoding="utf-8").strip()
    if not context:
        logging.info("Empty context, skipping")
        context_file.unlink(missing_ok=True)
        return

    logging.info(
        "Flushing %d chars for session %s (%s %s–%s)",
        len(context), session_id, chunk["date"], chunk.get("start"), chunk.get("end"),
    )

    response = asyncio.run(run_flush(context))
    logging.info("Agent response (%d chars): %s", len(response), response[:500].replace("\n", " | "))
    entry, reconsidered = parse_entry(response)

    if reconsidered:
        logging.info("Agent reversed its %s without writing an entry, retrying once", SENTINEL_NOTHING)
        response = asyncio.run(run_flush(context, preamble=RETRY_NOTE))
        logging.info("Retry response (%d chars): %s", len(response), response[:500].replace("\n", " | "))
        entry, reconsidered = parse_entry(response)

    if entry.startswith("FLUSH_ERROR"):
        # Errors are operator signal, not knowledge — keep them out of the vault. The
        # session cursor has already moved past these turns, so keep the context for a
        # manual replay instead of deleting it.
        failed = context_file.with_name(f"failed-{context_file.name}")
        context_file.rename(failed)
        logging.error("Flush failed, nothing written, context kept at %s: %s", failed, entry)
        return
    if reconsidered:
        logging.warning("Agent reversed its %s again without an entry, nothing written", SENTINEL_NOTHING)
    elif not entry:
        logging.info("%s — nothing worth saving", SENTINEL_NOTHING)
    else:
        logging.info("Saved to daily log %s (%d chars)", chunk["date"], len(entry))
        append_to_daily_log(entry, chunk["date"], entry_heading(chunk))
    context_file.unlink(missing_ok=True)


def main() -> None:
    if len(sys.argv) < 2:
        logging.error("Usage: flush.py <manifest.json>")
        sys.exit(1)

    manifest_path = Path(sys.argv[1])
    manifest = read_json(manifest_path)
    session_id = manifest.get("session_id", "unknown")
    chunks = manifest.get("chunks", [])
    logging.info("Started for session %s (%s, %d chunks)", session_id, manifest.get("reason"), len(chunks))

    for chunk in chunks:
        try:
            flush_chunk(session_id, chunk)
        except Exception as e:
            logging.exception("Chunk %s failed for session %s: %s", chunk.get("file"), session_id, e)
    manifest_path.unlink(missing_ok=True)

    maybe_trigger_compilation()

    logging.info("Complete for session %s", session_id)


if __name__ == "__main__":
    main()
