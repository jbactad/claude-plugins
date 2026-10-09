#!/usr/bin/env python3
"""
SessionEnd hook — hands every not-yet-captured turn of the session to flush.py,
which extracts knowledge into the daily log in the background.

No API calls in this hook — only local file I/O for speed (<10s timeout).
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

# Recursion guard: exit immediately if spawned by flush.py (which calls Agent SDK,
# which runs Claude Code, which would re-fire this hook).
if os.environ.get("CLAUDE_INVOKED_BY"):
    sys.exit(0)

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

logging.basicConfig(
    filename=str(SCRIPTS_DIR / "flush.log"),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [session-end] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

from capture import capture, prune_cursors, read_hook_input


def main() -> None:
    hook_input = read_hook_input()
    if hook_input is None:
        return
    logging.info("SessionEnd fired: session=%s", hook_input.get("session_id", "unknown"))
    # The session is over: whatever is left gets flushed, however little.
    capture(hook_input, "session-end", lambda turns: True)
    prune_cursors()


if __name__ == "__main__":
    main()
