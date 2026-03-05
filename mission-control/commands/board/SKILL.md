---
name: board
description: Display the mission task board. Shows task progress, waves, and dependencies.
disable-model-invocation: true
argument-hint: "[--view board|list|graph|json] [--watch]"
---

# Mission Board

Display the current mission's task board.

## Workflow

### Step 1: Check for Active Mission

Check if `.mission-control/missions/active.json` exists and `.mission-control/missions/tasks/` contains task files.

If neither exists, report:

```
No active mission or tasks found. Use /mission to start one.
```

### Step 2: Run the Board

Run the mission-board script with the user's arguments:

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/mission-board.js $ARGUMENTS
```

Display the output directly to the user.

If `$ARGUMENTS` is empty, run with no flags (default board view).

### Available Views

- No flags or `--view board` -- Wave-grouped task board with progress bar and status icons
- `--view list` -- Flat task list sorted by status (running first, then blocked, pending, done)
- `--view graph` -- ASCII dependency graph showing task connections
- `--view json` -- Raw JSON output for programmatic use

### Watch Mode

Add `--watch` to any view to enter live mode. The board refreshes every 2 seconds and auto-exits when all tasks reach a terminal state.
