#!/usr/bin/env python3
import json
import os
import sys

try:
    hook_input = json.load(sys.stdin)
except Exception:
    hook_input = {}

agent_id = hook_input.get('agent_id', '')
stop_hook_active = hook_input.get('stop_hook_active', False)

if agent_id:
    sys.exit(0)

if stop_hook_active:
    sys.exit(0)

if os.environ.get('MISSION_CONTROL_RESUME') != '1':
    sys.exit(0)

mission_file = os.path.join(os.environ.get('CLAUDE_PROJECT_DIR', ''), '.mission-control/missions/active.json')

if not os.path.isfile(mission_file):
    sys.exit(0)

try:
    with open(mission_file) as f:
        data = json.load(f)
    tasks = data.get('tasks', [])
    remaining = sum(1 for t in tasks if t.get('status') != 'completed')
except Exception:
    remaining = 0

if remaining > 0:
    print(f'Mission Control: {remaining} task(s) remaining in active mission. Consider running /checkpoint or /debrief before ending the session.', file=sys.stderr)
    sys.exit(2)
