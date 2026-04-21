#!/bin/bash
set -euo pipefail

# Read hook input from stdin
INPUT=$(cat)

# Parse agent_id and stop_hook_active from hook input
HOOK_DATA=$(echo "$INPUT" | node -e "
  let d = '';
  process.stdin.on('data', c => d += c);
  process.stdin.on('end', () => {
    try {
      const o = JSON.parse(d);
      console.log(o.agent_id || '');
      console.log(o.stop_hook_active || false);
    } catch (e) {
      console.log('');
      console.log('false');
    }
  });
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
REMAINING=$(node -e "
  const fs = require('fs');
  try {
    const d = JSON.parse(fs.readFileSync(process.argv[1], 'utf8'));
    const tasks = d.tasks || [];
    const remaining = tasks.filter(t => t.status !== 'completed').length;
    console.log(remaining);
  } catch (e) {
    console.log('0');
  }
" "$MISSION_FILE" 2>/dev/null || echo "0")

if [[ "$REMAINING" =~ ^[0-9]+$ ]] && [ "$REMAINING" -gt 0 ]; then
  echo "Mission Control: $REMAINING task(s) remaining in active mission. Consider running /checkpoint or /debrief before ending the session." >&2
  exit 2
fi

exit 0
