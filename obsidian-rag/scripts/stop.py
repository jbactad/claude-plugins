#!/usr/bin/env python3
"""
Stop hook — fires after every assistant turn and flushes a session that is still open
once enough has piled up, so its work reaches the daily log the same day.

Without this, a session only reaches the log when it ends or compacts: one left open
overnight would file yesterday's work late, and a quiet session might never compact.

Must stay cheap: it runs on every turn, reads only the transcript past the session's
cursor, and returns without spawning anything unless a threshold is crossed.
"""

from __future__ import annotations

import logging
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Recursion guard
if os.environ.get("CLAUDE_INVOKED_BY"):
    sys.exit(0)

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

logging.basicConfig(
    filename=str(SCRIPTS_DIR / "flush.log"),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [stop] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

from capture import Turn, capture, read_hook_input

FLUSH_AT_TURNS = 40  # a busy session flushes in batches of this size
IDLE_FLUSH_TURNS = 10  # a slower session flushes once this many turns are...
IDLE_FLUSH_AGE = timedelta(hours=2)  # ...at least this old


def should_flush(turns: list[Turn]) -> bool:
    now = datetime.now(timezone.utc).astimezone()
    oldest = turns[0].at
    return (
        len(turns) >= FLUSH_AT_TURNS
        # Crossed midnight: file the earlier day's turns under that day now.
        or oldest.date() < now.date()
        or (len(turns) >= IDLE_FLUSH_TURNS and now - oldest >= IDLE_FLUSH_AGE)
    )


def main() -> None:
    hook_input = read_hook_input()
    if hook_input is None:
        return
    capture(hook_input, "stop", should_flush)


if __name__ == "__main__":
    main()
