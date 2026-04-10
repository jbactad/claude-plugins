#!/usr/bin/env python3
"""
Background memory flush agent — extracts important knowledge from a conversation
transcript and appends it to today's daily log.

Spawned by session-end.py or pre-compact.py as a detached background process.
Uses the Claude Agent SDK to decide what's worth saving.

Usage:
    python flush.py <context_file.md> <session_id>
"""

from __future__ import annotations

# Recursion prevention: set BEFORE any imports that might trigger Claude.
import os
os.environ["CLAUDE_INVOKED_BY"] = "memory_flush"

import asyncio
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import DAILY_DIR, PLUGIN_DIR, SCRIPTS_DIR, today_iso, now_iso

LAST_FLUSH_FILE = SCRIPTS_DIR / "last-flush.json"
COMPILE_AFTER_HOUR = 18  # 6 PM local time

logging.basicConfig(
    filename=str(SCRIPTS_DIR / "flush.log"),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [flush] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def load_flush_state() -> dict:
    if LAST_FLUSH_FILE.exists():
        try:
            return json.loads(LAST_FLUSH_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_flush_state(state: dict) -> None:
    LAST_FLUSH_FILE.write_text(json.dumps(state), encoding="utf-8")


def append_to_daily_log(content: str) -> None:
    """Append a session entry to today's daily log."""
    today = datetime.now(timezone.utc).astimezone()
    log_path = DAILY_DIR / f"{today.strftime('%Y-%m-%d')}.md"

    if not log_path.exists():
        DAILY_DIR.mkdir(parents=True, exist_ok=True)
        log_path.write_text(
            f"# Daily Log: {today.strftime('%Y-%m-%d')}\n\n## Sessions\n\n",
            encoding="utf-8",
        )

    time_str = today.strftime("%H:%M")
    entry = f"### Session ({time_str})\n\n{content}\n\n"

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(entry)


async def run_flush(context: str) -> str:
    """Use Claude Agent SDK to extract worth-keeping knowledge from conversation context."""
    from claude_agent_sdk import (
        AssistantMessage,
        ClaudeAgentOptions,
        ResultMessage,
        TextBlock,
        query,
    )

    prompt = f"""Review the conversation context below and respond with a concise summary
of important items that should be preserved in the daily knowledge log.
Do NOT use any tools — return plain text only.

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

Skip:
- Routine tool calls or file reads
- Trivial or obvious content
- Back-and-forth clarifications with no knowledge value

If nothing is worth saving, respond with exactly: FLUSH_OK

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


def main() -> None:
    if len(sys.argv) < 3:
        logging.error("Usage: flush.py <context_file.md> <session_id>")
        sys.exit(1)

    context_file = Path(sys.argv[1])
    session_id = sys.argv[2]

    logging.info("Started for session %s", session_id)

    if not context_file.exists():
        logging.error("Context file not found: %s", context_file)
        return

    # Deduplication: skip if same session flushed within 60 seconds
    state = load_flush_state()
    if (
        state.get("session_id") == session_id
        and time.time() - state.get("timestamp", 0) < 60
    ):
        logging.info("Skipping duplicate flush for session %s", session_id)
        context_file.unlink(missing_ok=True)
        return

    context = context_file.read_text(encoding="utf-8").strip()
    if not context:
        logging.info("Empty context, skipping")
        context_file.unlink(missing_ok=True)
        return

    logging.info("Flushing %d chars for session %s", len(context), session_id)

    response = asyncio.run(run_flush(context))

    if "FLUSH_OK" in response:
        logging.info("FLUSH_OK — nothing worth saving")
    elif "FLUSH_ERROR" in response:
        logging.error("Flush error: %s", response)
        append_to_daily_log(response)
    else:
        logging.info("Saved to daily log (%d chars)", len(response))
        append_to_daily_log(response)

    save_flush_state({"session_id": session_id, "timestamp": time.time()})
    context_file.unlink(missing_ok=True)

    maybe_trigger_compilation()

    logging.info("Complete for session %s", session_id)


if __name__ == "__main__":
    main()
