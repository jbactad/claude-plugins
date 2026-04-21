#!/bin/bash
set -euo pipefail

MISSION_FILE="${CLAUDE_PROJECT_DIR}/.mission-control/missions/active.json"

if [ ! -f "$MISSION_FILE" ]; then
  exit 0
fi

# Parse hook input: extract agent_id and source
HOOK_DATA=$(python3 -c "
import json, sys
try:
    o = json.load(sys.stdin)
    print(o.get('agent_id', ''))
    print(o.get('source', 'startup'))
except Exception:
    print('')
    print('startup')
" 2>/dev/null)

AGENT_ID=$(echo "$HOOK_DATA" | sed -n '1p')
SOURCE=$(echo "$HOOK_DATA" | sed -n '2p')

# Never inject into sub-agent sessions
if [ -n "$AGENT_ID" ]; then
  exit 0
fi

# Inject on resume (session recovery), or on startup only when explicitly requested
if [ "$SOURCE" != "resume" ] && [ "${MISSION_CONTROL_RESUME:-}" != "1" ]; then
  exit 0
fi

python3 -c "
import json, sys

try:
    with open(sys.argv[1]) as f:
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
print('')
print('  Mission: ' + name)
print('  Status:  ' + status)
print('  Progress: ' + str(completed) + '/' + str(total) + ' tasks completed')

if in_progress:
    print('  In Progress: ' + ', '.join(in_progress))

if failed:
    print('  Failed: ' + ', '.join(failed))

print('')
print('Use /checkpoint for full status or /debrief to close the mission.')
" "$MISSION_FILE" 2>/dev/null
