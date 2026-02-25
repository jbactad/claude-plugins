---
name: mission
description: Launch a new mission. Initializes mission state and begins the orchestration workflow.
disable-model-invocation: true
argument-hint: "[goal description]"
---

# Mission Launcher

Launch a new autonomous mission. This command initializes mission state, loads settings and learnings, optionally applies a playbook, and begins the full orchestration workflow.

## Workflow

### Step 1: Determine Mission Goal

If `$ARGUMENTS` is provided and non-empty, use it as the mission goal. Skip the interactive prompt.

If `$ARGUMENTS` is empty, ask the user for the mission goal:

```
AskUserQuestion:
  question: "What is the goal of this mission?"
  options:
    - "New Feature: [describe]"
    - "Bug Fix: [describe]"
    - "Refactoring: [describe]"
    - "Migration: [describe]"
    - "Other: [describe]"
```

Capture the user's response as the mission goal. If they selected a category prefix (e.g., "New Feature:"), retain it -- it informs planning depth and playbook matching later.

### Step 2: Load Settings

Read settings from two locations and merge them. Project settings override organization defaults for any key present in both.

1. **Organization defaults**: Read `~/.claude/mission-control.local.md`. Parse the YAML frontmatter to extract default settings. If the file does not exist, use built-in defaults.

2. **Project overrides**: Read `.claude/mission-control.local.md`. Parse the YAML frontmatter to extract project-specific settings. If the file does not exist, use organization defaults only.

3. **Merge**: For each setting key, the project value wins if present. Otherwise the org value applies. If neither exists, use built-in defaults.

**Built-in defaults** (used when no settings files exist):

```yaml
defaultModel: sonnet
defaultPlanningDepth: spec
requireApproval: tier2+
maxConcurrentAgents: 3
useWorktrees: true
autoReview: true
autoTest: true
testCommand: ""
retryOnFailure: true
maxRetries: 2
escalateModelOnRetry: true
memoryEnabled: true
autoLearn: true
```

Display the effective settings summary to the user:

```
EFFECTIVE SETTINGS
──────────────────
Model: [defaultModel]
Planning: [defaultPlanningDepth]
Approval: [requireApproval]
Max Agents: [maxConcurrentAgents]
Worktrees: [useWorktrees]
Auto-Review: [autoReview]
Auto-Test: [autoTest] ([testCommand] or "no test command")
Retry: [retryOnFailure] (max [maxRetries], escalate: [escalateModelOnRetry])
Memory: [memoryEnabled]
Auto-Learn: [autoLearn]
```

Also note any custom agent types defined in the project settings file's markdown body. These are available for task assignment alongside the built-in agents (researcher, mission-planner, implementer, reviewer, retrospective).

### Step 3: Load Relevant Learnings

If `memoryEnabled` is true in the effective settings:

1. Check if `.claude/mission-memory/` exists. If it does not, skip this step.
2. Read all `.md` files in `.claude/mission-memory/`.
3. For each file, parse the YAML frontmatter and extract `tags`, `category`, and the markdown body.
4. Match tags against keywords in the mission goal using simple term overlap.
5. Always include files with `category: gotcha` regardless of tag match.
6. Display any relevant learnings to the user:

```
RELEVANT LEARNINGS
──────────────────
[filename] (category: [category], confidence: [confidence])
  [first 2-3 lines of body or summary]

[filename] (category: gotcha)
  [first 2-3 lines of body or summary]
```

If no learnings are found, display: "No relevant learnings found for this mission goal."

These learnings will be injected into the mission planner's context during task decomposition.

### Step 4: Check for Matching Playbooks

Check for playbooks that match the mission goal:

1. **Built-in playbooks**: Check against these known playbook types:
   - `full-stack-feature` -- matches goals mentioning "feature", "add", "implement", "build", "create"
   - `bug-investigation` -- matches goals mentioning "bug", "fix", "broken", "error", "crash", "regression"
   - `refactoring` -- matches goals mentioning "refactor", "clean up", "reorganize", "extract", "consolidate"
   - `security-audit` -- matches goals mentioning "security", "audit", "vulnerability", "auth", "permissions"
   - `migration` -- matches goals mentioning "migrate", "upgrade", "move", "convert", "transition"

2. **Project playbooks**: Check `.claude/missions/playbooks/` for any `.md` files. Parse their frontmatter for `name` and `description`. Match descriptions against the mission goal.

3. If one or more playbooks match, ask the user:

```
AskUserQuestion:
  question: "A matching playbook was found: [playbook-name] — [description]. Use it?"
  options:
    - "Yes, use this playbook"
    - "No, plan from scratch"
    - "Show me the playbook first"
```

If the user chooses "Show me the playbook first", display the playbook contents, then re-ask whether to use it.

If a playbook is selected, its phases will be used as the pre-configured task decomposition in Step 5, bypassing the mission-planner agent's free-form decomposition. The planner will still fill in file ownership, models, and acceptance criteria within the playbook's phase structure.

### Step 5: Begin Orchestration

Invoke the **orchestrate** skill workflow. The orchestrate skill defines a 7-step process:

1. **Scope** -- Define the mission outcome, success metrics, budget, constraints, deliverables, and stop criteria.
2. **Risk Assessment** -- Assign an overall risk tier (Tier 0-3) based on scope and impact.
3. **Decompose** -- Spawn the mission-planner agent to produce a task dependency graph. If a playbook was selected, pass its phases as the decomposition template.
4. **Pattern Selection** -- Choose an orchestration pattern (fan-out, pipeline, explore-then-act, competitive, iterative, supervisor) based on the task graph structure.
5. **Launch** -- Begin executing tasks in dependency order, respecting `maxConcurrentAgents`. Spawn agents for each task.
6. **Monitor** -- Track task completion, handle failures (retry with model escalation if enabled), run reviewer agents for Tier 1+ tasks.
7. **Close** -- When all tasks complete, produce a completion summary. If `autoLearn` is enabled, trigger learning extraction.

Pass the following context to the orchestrate workflow:
- Mission goal
- Effective settings (merged)
- Relevant learnings (from Step 3)
- Selected playbook (from Step 4, if any)
- Custom agent types (from project settings, if any)

### Step 6: Save Initial Mission State

Create the `.claude/missions/` directory if it does not exist.

Generate a mission ID using the format `mission-{timestamp}` where timestamp is the current Unix timestamp in milliseconds.

Save the initial mission state to `.claude/missions/active.json`:

```json
{
  "id": "mission-{timestamp}",
  "name": "<short name derived from goal>",
  "goal": "<full mission goal text>",
  "status": "active",
  "createdAt": "<ISO-8601 timestamp>",
  "updatedAt": "<ISO-8601 timestamp>",
  "scope": {
    "outcome": "<expected outcome from scoping step>",
    "successMetric": "<how to measure success>",
    "budget": "<estimated token/time budget>",
    "constraints": ["<constraint 1>", "<constraint 2>"],
    "inScope": ["<item 1>", "<item 2>"],
    "outOfScope": ["<item 1>", "<item 2>"],
    "stopCriteria": ["<condition 1>", "<condition 2>"],
    "deliverables": ["<deliverable 1>", "<deliverable 2>"]
  },
  "settings": {
    "planningDepth": "<from effective settings>",
    "requireApproval": "<from effective settings>",
    "maxConcurrentAgents": 3,
    "defaultModel": "sonnet",
    "useWorktrees": true,
    "autoReview": true,
    "autoTest": true,
    "testCommand": "",
    "retryOnFailure": true,
    "maxRetries": 2,
    "escalateModelOnRetry": true
  },
  "pattern": "<selected orchestration pattern>",
  "riskTier": 1,
  "tasks": [],
  "log": [],
  "artifacts": [],
  "playbook": "<playbook name or null>",
  "checkpoints": [],
  "learnings": []
}
```

The `tasks` array is empty at this point. It will be populated by the mission-planner agent during the decomposition step of the orchestrate workflow. Each task entry will follow this structure:

```json
{
  "id": "task-1",
  "name": "Task name",
  "agentType": "researcher",
  "deliverable": "Description of what this task produces",
  "dependencies": [],
  "riskTier": 0,
  "fileOwnership": ["path/to/file1.ts", "path/to/file2.ts"],
  "model": "haiku",
  "status": "pending",
  "assignedAgent": null,
  "result": null,
  "startedAt": null,
  "completedAt": null,
  "retryCount": 0,
  "acceptanceCriteria": ["criterion 1", "criterion 2"]
}
```

Valid task statuses: `pending`, `in_progress`, `completed`, `failed`, `blocked`, `cancelled`.

After saving the initial state, confirm to the user:

```
Mission launched: [mission-id]
Goal: [goal]
State saved to .claude/missions/active.json
Use /checkpoint to check progress, /debrief to close the mission.
```
