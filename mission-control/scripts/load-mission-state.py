#!/usr/bin/env python3
import json
import os
import sys

mission_file = os.path.join(os.environ.get('CLAUDE_PROJECT_DIR', ''), '.mission-control/missions/active.json')

if not os.path.isfile(mission_file):
    sys.exit(0)

try:
    hook_input = json.load(sys.stdin)
except Exception:
    hook_input = {}

agent_id = hook_input.get('agent_id', '')
source = hook_input.get('source', 'startup')

if agent_id:
    sys.exit(0)

if source != 'resume' and os.environ.get('MISSION_CONTROL_RESUME') != '1':
    sys.exit(0)

try:
    with open(mission_file) as f:
        data = json.load(f)
except Exception:
    sys.exit(0)

name = data.get('name', 'Unnamed mission')
status = data.get('status', 'unknown')
tasks = data.get('tasks', [])
total = len(tasks)
completed = sum(1 for t in tasks if t.get('status') == 'completed')
in_progress = [t.get('name') or t.get('id') for t in tasks if t.get('status') == 'in_progress']
failed = [t.get('name') or t.get('id') for t in tasks if t.get('status') == 'failed']

print('[Mission Control] Active mission detected:')
print()
print('  Mission: ' + name)
print('  Status:  ' + status)
print('  Progress: ' + str(completed) + '/' + str(total) + ' tasks completed')
if in_progress:
    print('  In Progress: ' + ', '.join(in_progress))
if failed:
    print('  Failed: ' + ', '.join(failed))
print()
print('Use /checkpoint for full status or /debrief to close the mission.')
