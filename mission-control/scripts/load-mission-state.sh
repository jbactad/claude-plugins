#!/bin/bash
# SessionStart hook: Load active mission state and inject it as context.
#
# If .mission-control/missions/active.json exists, reads the file and outputs a
# formatted summary to stdout. Claude receives this output as injected
# context at the start of the session.
#
# If no active mission exists, exits silently (exit 0, no output).

MISSION_FILE=".mission-control/missions/active.json"

if [ ! -f "$MISSION_FILE" ]; then
  exit 0
fi

# Use node to parse JSON and produce a human-readable summary
node -e "
  const fs = require('fs');
  try {
    const data = JSON.parse(fs.readFileSync('$MISSION_FILE', 'utf8'));

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
    // Malformed JSON or read error — exit silently
    process.exit(0);
  }
" 2>/dev/null
