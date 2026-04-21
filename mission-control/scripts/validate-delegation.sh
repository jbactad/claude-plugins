#!/bin/bash
set -euo pipefail

# Read tool input from stdin
INPUT=$(cat)

# Extract the subagent_type from tool input
AGENT_TYPE=$(echo "$INPUT" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    print((d.get('tool_input') or {}).get('subagent_type', 'unknown'))
except Exception:
    print('unknown')
" 2>/dev/null || echo "unknown")

# Sanitize agent type — allow only alphanumeric, hyphens, underscores, colons
if [[ ! "$AGENT_TYPE" =~ ^[a-zA-Z0-9_:-]+$ ]]; then
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
