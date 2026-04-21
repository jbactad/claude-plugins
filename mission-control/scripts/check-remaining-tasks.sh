#!/bin/bash
set -euo pipefail

# Read hook input from stdin
INPUT=$(cat)

# Parse agent_id and stop_hook_active from hook input
HOOK_DATA=$(echo "$INPUT" | python3 -c "
import json, sys
try:
    o = json.load(sys.stdin)
    print(o.get('agent_id', ''))
    print(str(o.get('stop_hook_active', False)).lower())
except Exception:
    print('')
    print('false')
" 2>/dev/null)

AGENT_ID=$(echo "$HOOK_DATA" | sed -n '1p')
STOP_ACTIVE=$(echo "$HOOK_DATA" | sed -n '2p')

# Never block sub-agents from stopping
if [ -n "$AGENT_ID" ]; then
  exit 0
fi

# Prevent infinite loops if stop hook is already active
if [ "$STOP_ACTIVE" = "true" ]; then
  exit 0
fi

MISSION_FILE="${CLAUDE_PROJECT_DIR}/.mission-control/missions/active.json"

if [ ! -f "$MISSION_FILE" ]; then
  exit 0
fi

# Count remaining (non-completed) tasks
REMAINING=$(echo "$MISSION_FILE" | python3 -c "
import json, sys
try:
    with open(sys.stdin.read().strip()) as f:
        data = json.load(f)
    tasks = data.get('tasks', [])
    print(sum(1 for t in tasks if t.get('status') != 'completed'))
except Exception:
    print('0')
" 2>/dev/null || echo "0")

if [[ "$REMAINING" =~ ^[0-9]+$ ]] && [ "$REMAINING" -gt 0 ]; then
  echo "Mission Control: $REMAINING task(s) remaining in active mission. Consider running /checkpoint or /debrief before ending the session." >&2
  exit 2
fi

exit 0
