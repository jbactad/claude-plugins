#!/bin/bash
set -euo pipefail
# PreToolUse[Task] hook: Log agent delegation events.
#
# Reads tool input from stdin, extracts the subagent_type being spawned.
# If an active mission exists, appends a log entry to .mission-control/missions/log.jsonl
# with the event type "delegate", agent type, and timestamp.
#
# This hook is informational only — it always exits 0 and never blocks
# delegation. The log is used for observability and retrospective analysis.

# Read tool input from stdin
INPUT=$(cat)

# Extract the subagent_type from tool input
AGENT_TYPE=$(echo "$INPUT" | node -e "
  const fs = require('fs');
  try {
    const d = JSON.parse(fs.readFileSync('/dev/stdin', 'utf8'));
    const agentType = (d.tool_input && d.tool_input.subagent_type) || 'unknown';
    console.log(agentType);
  } catch (e) {
    console.log('unknown');
  }
" 2>/dev/null || echo "unknown")

# Sanitize agent type — allow only alphanumeric, hyphens, underscores
if [[ ! "$AGENT_TYPE" =~ ^[a-zA-Z0-9_-]+$ ]]; then
  AGENT_TYPE="unknown"
fi

# Log delegation if an active mission exists
MISSION_FILE="${CLAUDE_PROJECT_DIR}/.mission-control/missions/active.json"

if [ -f "$MISSION_FILE" ]; then
  LOG_DIR="${CLAUDE_PROJECT_DIR}/.mission-control/missions"
  TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  printf '{"event":"delegate","agent":"%s","time":"%s"}\n' "$AGENT_TYPE" "$TIMESTAMP" >> "$LOG_DIR/log.jsonl"
fi

# Always allow — this hook is informational only
exit 0
