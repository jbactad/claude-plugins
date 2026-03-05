#!/bin/bash
set -euo pipefail
# SessionStart hook: Load active mission state and inject it as context.
#
# If .mission-control/missions/active.json exists, reads the file and outputs a
# formatted summary to stdout. Claude receives this output as injected
# context at the start of the session.
#
# If no active mission exists, exits silently (exit 0, no output).

MISSION_FILE="${CLAUDE_PROJECT_DIR}/.mission-control/missions/active.json"

if [ ! -f "$MISSION_FILE" ]; then
  exit 0
fi

# Use node to parse mission metadata and task files
node -e "
  const fs = require('fs');
  const path = require('path');
  try {
    const data = JSON.parse(fs.readFileSync(process.argv[1], 'utf8'));
    const tasksDir = path.join(path.dirname(process.argv[1]), 'tasks');

    const name = data.name || 'Unnamed mission';
    const status = data.status || 'unknown';

    let total = 0, completed = 0;
    const inProgress = [];
    const failed = [];

    if (fs.existsSync(tasksDir)) {
      const files = fs.readdirSync(tasksDir).filter(f => f.match(/^T\d+\.json$/));
      for (const f of files) {
        try {
          const t = JSON.parse(fs.readFileSync(path.join(tasksDir, f), 'utf8'));
          total++;
          if (t.status === 'completed') completed++;
          else if (t.status === 'in_progress') inProgress.push(t.name || t.id);
          else if (t.status === 'failed') failed.push(t.name || t.id);
        } catch {}
      }
    }

    console.log('[Mission Control] Active mission detected:');
    console.log('');
    console.log('  Mission: ' + name);
    console.log('  Status:  ' + status);
    console.log('  Progress: ' + completed + '/' + total + ' tasks completed');

    if (inProgress.length > 0) {
      console.log('  In Progress: ' + inProgress.join(', '));
    }

    if (failed.length > 0) {
      console.log('  Failed: ' + failed.join(', '));
    }

    console.log('');
    console.log('Use /checkpoint for full status, /board for task board, or /debrief to close the mission.');
  } catch (e) {
    process.exit(0);
  }
" "$MISSION_FILE" 2>/dev/null
