#!/usr/bin/env python3
import json
import os
import re
import sys
from datetime import datetime, timezone

try:
    tool_input = json.load(sys.stdin)
except Exception:
    tool_input = {}

agent_type = (tool_input.get('tool_input') or {}).get('subagent_type', 'unknown')

if not re.match(r'^[a-zA-Z0-9_:-]+$', agent_type):
    agent_type = 'unknown'

mission_file = os.path.join(os.environ.get('CLAUDE_PROJECT_DIR', ''), '.mission-control/missions/active.json')

if os.path.isfile(mission_file):
    log_path = os.path.join(os.environ.get('CLAUDE_PROJECT_DIR', ''), '.mission-control/missions/log.jsonl')
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    entry = json.dumps({'event': 'delegate', 'agent': agent_type, 'time': timestamp})
    with open(log_path, 'a') as f:
        f.write(entry + '\n')
