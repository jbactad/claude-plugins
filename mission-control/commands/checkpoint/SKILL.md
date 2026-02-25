---
name: checkpoint
description: Produce a mission checkpoint report showing progress, blockers, and budget.
disable-model-invocation: true
---

# Mission Checkpoint

Produce a structured checkpoint report for the active mission. This command reads mission state, gathers current task statuses, identifies blockers, and recommends whether to continue, rescope, or stop.

## Workflow

### Step 1: Load Active Mission

Read `.claude/missions/active.json`.

If the file does not exist, report the following and stop:

```
No active mission. Use /mission to start one.
```

If the file exists, parse it and extract the mission ID, name, goal, status, tasks, and settings.

### Step 2: Gather Task Statuses

Run `TaskList` to get the current statuses of all tasks tracked by the Task tool. Cross-reference with the tasks recorded in `active.json`.

For each task in the mission state, determine its current status:
- **completed** -- task finished successfully
- **in_progress** -- task is currently being executed by an agent
- **blocked** -- task cannot start because a dependency has not completed, or a dependency failed
- **pending** -- task is waiting to be started (all dependencies are met but execution has not begun)
- **failed** -- task was attempted but did not succeed
- **cancelled** -- task was explicitly cancelled

### Step 3: Calculate Progress Metrics

Compute the following:

- **Total tasks**: count of all tasks in the mission
- **Completed**: count of tasks with status `completed`
- **In progress**: count of tasks with status `in_progress`
- **Blocked**: count of tasks with status `blocked`
- **Failed**: count of tasks with status `failed`
- **Pending**: count of tasks with status `pending`
- **Cancelled**: count of tasks with status `cancelled`
- **Completion percentage**: `(completed / (total - cancelled)) * 100`, rounded to the nearest integer. If all tasks are cancelled, report 0%.

### Step 4: Identify Blockers

For each task with status `blocked`:

1. Look at its `dependencies` array.
2. Check whether any dependency has status `failed` or is itself `blocked`.
3. Determine the root cause of the block:
   - A failed dependency (name the dependency and its failure reason).
   - A chain of blocked dependencies (trace back to the original blocker).
   - An external factor (if the task is marked blocked but dependencies are all completed).
4. For each blocker, determine the next action:
   - Retry the failed task (if `retryOnFailure` is enabled and retry count is below `maxRetries`).
   - Escalate model and retry (if `escalateModelOnRetry` is enabled).
   - Ask user for guidance (if retries are exhausted or the block is external).
   - Rescope the mission to remove the blocked path.

### Step 5: Detect Risk Updates

Check for any new risks that have emerged since the mission started:

- Tasks that failed on first attempt (indicates underestimated complexity).
- Tasks that required model escalation (original model was insufficient).
- Tasks whose actual file changes exceed planned `fileOwnership` (scope creep).
- Reviewer tasks that returned `FAIL` verdict (quality issues).
- Any task that has been retried the maximum number of times without success (systemic issue).

### Step 6: Produce Checkpoint Report

Format and display the checkpoint report:

```
CHECKPOINT REPORT
─────────────────
Mission: [name] ([id])
Goal: [goal]
Status: [status]
Started: [createdAt]

Progress: [completed]/[total] tasks completed ([completion%]%)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ [progress bar visualization]

Completed:
  [task-id]: [task name] ([agent type], [model])
  [task-id]: [task name] ([agent type], [model])

In Progress:
  [task-id]: [task name] ([agent type], [model]) — started [startedAt]
  [task-id]: [task name] ([agent type], [model]) — started [startedAt]

Blocked:
  [task-id]: [task name]
    Blocked by: [dependency task-id] ([dependency status])
    Next action: [retry / escalate / ask user / rescope]

Failed:
  [task-id]: [task name]
    Failure reason: [result summary]
    Retry count: [retryCount]/[maxRetries]
    Next action: [retry with escalation / manual intervention]

Pending:
  [task-id]: [task name] — waiting on [dependency task-ids]
  [task-id]: [task name] — ready to start

Risk Updates:
  [list any new risks discovered, or "No new risks"]

Decision: [CONTINUE / RESCOPE / STOP] — [rationale]
```

**Decision logic**:

- **CONTINUE** -- More than 50% of tasks are completed or in progress, no systemic blockers, failed tasks can be retried.
- **RESCOPE** -- One or more critical-path tasks have failed beyond retry limits, or blocked tasks form a chain that prevents significant remaining work. Recommend specific scope changes.
- **STOP** -- Fundamental assumption was wrong (e.g., required API does not exist, architecture prevents the goal), or the user explicitly requested stopping. Recommend archiving the mission.

If the decision is RESCOPE, include specific recommendations:
- Which tasks to remove or replace.
- Whether to split a failing task into smaller subtasks.
- Whether to change agent types or models for pending tasks.

### Step 7: Update Mission State

Update `.claude/missions/active.json`:

1. Set `updatedAt` to the current ISO-8601 timestamp.
2. Update all task statuses to reflect current state.
3. Append a checkpoint entry to the `checkpoints` array:

```json
{
  "timestamp": "<ISO-8601>",
  "completed": 3,
  "total": 8,
  "completionPercentage": 38,
  "blockers": ["task-4: blocked by task-2 failure"],
  "decision": "CONTINUE",
  "rationale": "Task-2 can be retried with model escalation"
}
```

Save the updated state back to `.claude/missions/active.json`.
