#!/bin/bash
set -euo pipefail

MISSION_FILE="${CLAUDE_PROJECT_DIR}/.mission-control/missions/active.json"

if [ ! -f "$MISSION_FILE" ]; then
  exit 0
fi

# Parse hook input: extract agent_id and source
HOOK_DATA=$(node -e "
  let d = '';
  process.stdin.on('data', c => d += c);
  process.stdin.on('end', () => {
    try {
      const o = JSON.parse(d);
      console.log(o.agent_id || '');
      console.log(o.source || 'startup');
    } catch (e) {
      console.log('');
      console.log('startup');
    }
  });
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

node -e "
  const fs = require('fs');
  try {
    const data = JSON.parse(fs.readFileSync(process.argv[1], 'utf8'));

    const name = data.name || 'Unnamed mission';
    const status = data.status || 'unknown';
    const tasks = data.tasks || [];
    const total = tasks.length;
    const completed = tasks.filter(t => t.status === 'completed').length;
    const inProgress = tasks.filter(t => t.status === 'in_progress');
    const failed = tasks.filter(t => t.status === 'failed');

    console.log('[Mission Control] Active mission detected:');
    console.log('');
    console.log('  Mission: ' + name);
    console.log('  Status:  ' + status);
    console.log('  Progress: ' + completed + '/' + total + ' tasks completed');

    if (inProgress.length > 0) {
      console.log('  In Progress: ' + inProgress.map(t => t.name || t.id).join(', '));
    }

    if (failed.length > 0) {
      console.log('  Failed: ' + failed.map(t => t.name || t.id).join(', '));
    }

    console.log('');
    console.log('Use /checkpoint for full status or /debrief to close the mission.');
  } catch (e) {
    process.exit(0);
  }
" "$MISSION_FILE" 2>/dev/null
