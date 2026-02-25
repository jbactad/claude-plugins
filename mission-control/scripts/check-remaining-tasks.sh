#!/bin/bash
# Stop hook: Check for remaining tasks in the active mission.
#
# Reads hook input from stdin (JSON with stop_hook_active field).
# If stop_hook_active is true, exits 0 immediately to prevent looping.
#
# If .claude/missions/active.json exists and has incomplete tasks,
# outputs a warning to stderr and exits 2 (which prevents Claude from
# stopping and asks it to remind the user about the active mission).
#
# If no active mission exists or all tasks are complete, exits 0.

# Read hook input from stdin
INPUT=$(cat)

# Check if the stop hook is already active to prevent infinite loops
STOP_ACTIVE=$(echo "$INPUT" | node -e "
  const fs = require('fs');
  try {
    const d = JSON.parse(fs.readFileSync('/dev/stdin', 'utf8'));
    console.log(d.stop_hook_active || false);
  } catch (e) {
    console.log('false');
  }
" 2>/dev/null)

if [ "$STOP_ACTIVE" = "true" ]; then
  exit 0
fi

MISSION_FILE=".claude/missions/active.json"

if [ ! -f "$MISSION_FILE" ]; then
  exit 0
fi

# Count remaining (non-completed) tasks
REMAINING=$(cat "$MISSION_FILE" | node -e "
  const fs = require('fs');
  try {
    const d = JSON.parse(fs.readFileSync('/dev/stdin', 'utf8'));
    const tasks = d.tasks || [];
    const remaining = tasks.filter(t => t.status !== 'completed').length;
    console.log(remaining);
  } catch (e) {
    console.log('0');
  }
" 2>/dev/null)

if [ "$REMAINING" -gt 0 ] 2>/dev/null; then
  echo "Mission Control: $REMAINING task(s) remaining in active mission. Consider running /checkpoint or /debrief before ending the session." >&2
  exit 2
fi

exit 0
