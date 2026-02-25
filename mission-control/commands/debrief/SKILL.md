---
name: debrief
description: Close the active mission, extract learnings, and archive mission state.
disable-model-invocation: true
---

# Mission Debrief

Close the active mission, produce a completion summary, extract learnings for future missions, and archive the mission state. This is the final step in a mission lifecycle.

## Workflow

### Step 1: Load Active Mission

Read `.mission-control/missions/active.json`.

If the file does not exist, report the following and stop:

```
No active mission to debrief.
```

If the file exists, parse it and extract the full mission state: ID, name, goal, scope, tasks, log, artifacts, settings, and checkpoints.

### Step 2: Verify Task Completion

Check all tasks in the mission:

- Count tasks by status: completed, failed, cancelled, in_progress, pending, blocked.
- Determine whether the mission is ready to close.

**If all tasks are completed or cancelled**: Proceed to Step 3.

**If tasks remain in_progress, pending, or blocked**: Ask the user:

```
AskUserQuestion:
  question: "[X] tasks are not yet completed:
    - [task-id]: [task name] ([status])
    - [task-id]: [task name] ([status])
    Close the mission anyway?"
  options:
    - "Yes, close and mark remaining tasks as cancelled"
    - "No, continue working on remaining tasks"
```

If the user chooses to close anyway, update all non-completed tasks to status `cancelled` with a result of "Cancelled during debrief". If the user chooses to continue, report "Mission remains active. Use /checkpoint to check progress." and stop.

### Step 3: Produce Completion Summary

Gather the information needed for the summary:

1. **Planned outcome**: From `scope.outcome` in the mission state.
2. **Achieved outcome**: Summarize what was actually delivered based on completed task results and artifacts.
3. **Artifacts**: Collect all files created or modified across completed tasks. Use each task's `fileOwnership` field and any entries in the mission `artifacts` array. List each file with its path and whether it was created or modified.
4. **Key decisions**: Review the mission log and checkpoint history for decision points -- model escalations, rescoping events, playbook deviations, approval requests.
5. **Validation evidence**: Collect results from reviewer tasks (pass/fail verdicts) and any test execution results from task outputs.
6. **Open risks**: Identify unresolved issues -- failed tasks that were cancelled rather than fixed, reviewer findings marked as "PASS WITH NOTES", tasks where scope was reduced.
7. **Follow-ups**: Identify work items that should happen in a future session -- features deferred during rescoping, known issues discovered but not fixed, TODOs left in code.
8. **Lessons learned**: Identify patterns and anti-patterns from the mission execution -- what worked well, what caused problems, which agent/model assignments were right or wrong.

Display the completion summary:

```
COMPLETION SUMMARY
──────────────────
Mission: [name] ([id])
Goal: [goal]
Duration: [createdAt] to [now]
Tasks: [completed]/[total] completed, [cancelled] cancelled, [failed] failed

Planned Outcome:
  [scope.outcome]

Achieved Outcome:
  [summary of what was actually delivered]

Artifacts:
  [path/to/file1.ts] (created)
  [path/to/file2.ts] (modified)
  [path/to/file3.test.ts] (created)
  ...

Key Decisions:
  - [decision 1 and its rationale]
  - [decision 2 and its rationale]

Validation Evidence:
  - [reviewer task-id]: [verdict] — [summary]
  - Tests: [pass/fail summary if testCommand was configured]

Open Risks:
  - [risk 1: description and potential impact]
  - [risk 2: description and potential impact]
  (or "None identified")

Follow-Ups:
  - [follow-up 1: description]
  - [follow-up 2: description]
  (or "None")

Lessons Learned:
  - [lesson 1: what worked or failed and why]
  - [lesson 2: what worked or failed and why]
```

### Step 4: Extract Structured Learnings

Check whether `autoLearn` is enabled in the mission settings (from `settings` in the mission state, falling back to effective settings from settings files).

**If `autoLearn` is enabled**:

Spawn the **retrospective** agent to analyze the completed mission and extract structured learnings. Pass the agent:
- The full mission state (goal, tasks, log, checkpoints, artifacts).
- The completion summary from Step 3.
- Existing learnings from `.mission-control/memory/` (to avoid duplicates).

The retrospective agent will produce structured learnings. For each learning, save it to `.mission-control/memory/` as a markdown file with YAML frontmatter.

Create the `.mission-control/memory/` directory if it does not exist.

**Learning file format**:

Each learning is saved as a separate file or appended to an existing category file. The filename matches the category (e.g., `patterns.md`, `gotchas.md`, `architecture.md`, `tooling.md`, `prompts.md`).

```markdown
---
tags:
  - <tag1>
  - <tag2>
  - <tag3>
source: <mission-id>
extractedAt: <ISO-8601 timestamp>
confidence: <high|medium|low>
category: <pattern|gotcha|architecture|tooling|prompt>
---

# <Learning Title>

<Learning body — specific, actionable, with file paths where applicable.>
```

**Learning categories**:
- `pattern` -- Reusable implementation patterns discovered during the mission.
- `gotcha` -- Mistakes made or pitfalls discovered. These are always loaded in future missions.
- `architecture` -- Architectural decisions, constraints, or boundaries discovered.
- `tooling` -- Build, test, deploy, or development workflow patterns.
- `prompt` -- Effective prompt patterns for agent instructions.

When appending to an existing category file, add the new learning under a new heading. Do not overwrite existing content. Update the frontmatter `tags` array to include any new tags from the appended learning.

**If `autoLearn` is disabled**: Skip learning extraction. Display: "Auto-learn is disabled. Skipping learning extraction. Enable autoLearn in settings to capture mission learnings."

### Step 5: Archive Mission State

1. Create `.mission-control/missions/archive/` directory if it does not exist.
2. Update the mission state:
   - Set `status` to `"completed"` (or `"completed_partial"` if tasks were cancelled).
   - Set `updatedAt` to the current ISO-8601 timestamp.
   - Add a final checkpoint with the completion summary.
   - Add references to any extracted learning files.
3. Copy `.mission-control/missions/active.json` to `.mission-control/missions/archive/{mission-id}.json`.
4. Remove `.mission-control/missions/active.json`.

### Step 6: Present Summary

Display a final confirmation to the user:

```
Mission debriefed and archived.

  ID: [mission-id]
  Archive: .mission-control/missions/archive/[mission-id].json
  Learnings: [N] learnings extracted to .mission-control/memory/
    [list of learning files created or updated]

Use /mission to start a new mission.
Use /playbook list to see available playbooks.
```

If no learnings were extracted (either because `autoLearn` was disabled or the retrospective agent found nothing new), display:

```
Mission debriefed and archived.

  ID: [mission-id]
  Archive: .mission-control/missions/archive/[mission-id].json
  Learnings: None extracted

Use /mission to start a new mission.
```
