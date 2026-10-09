#!/usr/bin/env python3
"""
PreCompact hook — checkpoints the session before Claude Code compacts the context.

The transcript file keeps every turn after compaction, so nothing is lost if this
skips; it flushes here so a long session's knowledge reaches the daily log while
the work is still fresh rather than only when the session ends.

No API calls — only local file I/O.
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

# Recursion guard
if os.environ.get("CLAUDE_INVOKED_BY"):
    sys.exit(0)

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

logging.basicConfig(
    filename=str(SCRIPTS_DIR / "flush.log"),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [pre-compact] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

from capture import capture, read_hook_input

MIN_TURNS_TO_FLUSH = 5


def main() -> None:
    hook_input = read_hook_input()
    if hook_input is None:
        return
    logging.info("PreCompact fired: session=%s", hook_input.get("session_id", "unknown"))
    capture(hook_input, "pre-compact", lambda turns: len(turns) >= MIN_TURNS_TO_FLUSH)


if __name__ == "__main__":
    main()
