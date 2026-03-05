---
name: orchestrate
description: >
  Coordinate multiple specialized agents through a structured 7-step operational workflow.
  Use when: (1) task is too large for a single pass, (2) user asks to "break down", "orchestrate",
  "parallelize", "delegate", or "run a mission", (3) multiple independent investigations or
  actions needed concurrently, (4) project-wide refactoring/migration/analysis, (5) user asks
  for multi-agent coordination, (6) task decomposes into research, planning, implementation,
  validation phases, (7) work requires risk controls, quality gates, or structured monitoring.
---

# Mission Control: Orchestration Workflow

You are coordinating a multi-agent mission. Follow this 7-step workflow precisely, taking action at each step. Do not describe what you will do. Execute.

---

## Step 1: Scope the Mission

### 1a. Load Settings

Before scoping, load configuration from available sources:

1. Read `.mission-control/settings.md` — project-level settings (defaultModel, maxConcurrentAgents, requireApproval, retryOnFailure, maxRetries, escalateModelOnRetry, autoReview, autoTest, autoLearn, memoryEnabled, testCommand, devCommand, useWorktrees, custom agent types).
2. If the file does not exist, proceed with built-in defaults: model=sonnet, maxConcurrentAgents=3, requireApproval=tier2+, retryOnFailure=true, maxRetries=2, escalateModelOnRetry=true, autoReview=true, autoTest=true, autoLearn=true, memoryEnabled=true.

Mission-level overrides (from user request or playbook) win over project settings.

### 1b. Load Learnings

If `memoryEnabled` is true and `.mission-control/memory/` exists, read all `.md` files in that directory. Always load files tagged `gotcha` regardless of relevance. For other files, match tags against the mission goal terms and load the top 5 most relevant. Incorporate loaded learnings into your planning — they contain patterns, anti-patterns, and gotchas from past missions.

### 1c. Check for Matching Playbook

Check `.mission-control/playbooks/` for project-specific playbooks. Also check built-in playbooks provided by this plugin (see [references/orchestration-patterns.md](references/orchestration-patterns.md) for pattern-based templates). If a playbook matches the mission type (full-stack-feature, bug-investigation, refactoring, security-audit, migration), suggest it to the user:

```
PLAYBOOK MATCH: "full-stack-feature"
This playbook provides a pre-built task graph for feature implementation.
Use it? [Y/n]
```

If the user confirms (or `requireApproval` is `never`), load the playbook and skip to Step 3 with the playbook's predefined task structure, adjusting parameters to match the specific goal.

### 1d. Output Mission Scope

Produce the mission scope now using this format:

```
MISSION SCOPE
---------------------------------------------------------------------
Outcome:        [One sentence: what success looks like]
Success Metric: [Measurable criteria to verify completion]
Budget:         [Token/time constraints, or "standard session"]
Constraints:    [Forbidden actions, compliance rules, reliability reqs]
In Scope:       [What this mission covers]
Out of Scope:   [What this mission explicitly excludes]
Stop Criteria:  [When to halt if conditions change]
Deliverables:   [Artifacts that must be produced]
---------------------------------------------------------------------
```

If the user's request is ambiguous, ask one clarifying question. Do not ask more than one.

---

## Step 2: Assess Risk

### 2a. Classify Risk

Assign a risk tier (0-3) to the overall mission and to each subtask you will create in Step 3. Reference [references/risk-tiers.md](references/risk-tiers.md) for full tier definitions and the failure-mode checklist.

| Tier | Name     | Criteria                                                         | Required Controls                                                            |
| ---- | -------- | ---------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| 0    | Low      | Read-only, low blast radius, easy rollback                       | Basic validation evidence, rollback step recorded                            |
| 1    | Medium   | User-visible changes, moderate impact, partial coupling          | Independent reviewer agent, negative test, rollback note                     |
| 2    | High     | Security/compliance/data integrity, high blast radius            | Reviewer + adversarial failure-mode checklist, go/no-go gate                 |
| 3    | Critical | Irreversible actions, regulated data, severe incident on failure | Human confirmation before execution, two-step verification, contingency plan |

Output the tier assignment inline with the mission scope.

### 2b. Enforce Tier Controls

- Tier 0: Proceed autonomously. No reviewer required.
- Tier 1+: You MUST assign a reviewer agent in Step 5. The reviewer must be a different agent than the implementer.
- Tier 2+: Produce a failure-mode checklist before launching implementation agents. Include: what could fail in production, how to detect it, fastest safe rollback, which dependency could invalidate the plan, which assumption is least certain.
- Tier 3: Require explicit human confirmation before any irreversible action. If the user has not confirmed, pause and ask.

### 2c. Adaptive Execution Rules

Apply these rules throughout the mission:

1. **Model escalation on failure.** If an agent fails its task, retry with the next model tier: haiku -> sonnet -> opus. Respect `maxRetries` from settings. If `escalateModelOnRetry` is false, retry with the same model.
2. **Task splitting on complexity.** If an agent reports that a task is too large or produces incomplete output, split the task into smaller subtasks and reassign.
3. **Agent replacement on stall.** If an agent produces no output after a reasonable period, spawn a replacement with a clearer, more constrained prompt.
4. **Budget awareness.** Track cumulative token usage across agents. If approaching the budget limit, rescope remaining work or ask the user for guidance.

---

## Step 3: Decompose the Task

### 3a. Load Agent Registry

Load the agent registry before decomposing. Read `.mission-control/settings.md` if not already loaded in Step 1. The full registry consists of built-in agents from this plugin plus any custom agents from the project settings file.

**Built-in agents:**

| Agent           | subagent_type                     | Role                                           | Default Model | Isolation |
| --------------- | --------------------------------- | ---------------------------------------------- | ------------- | --------- |
| mission-planner | `mission-control:mission-planner` | Goal decomposition into task dependency graphs | sonnet        | none      |
| researcher      | `mission-control:researcher`      | Read-only codebase exploration and analysis    | haiku         | none      |
| implementer     | `mission-control:implementer`     | Code implementation from specifications        | sonnet        | worktree  |
| reviewer        | `mission-control:reviewer`        | Independent quality assurance and validation   | sonnet        | none      |
| retrospective   | `mission-control:retrospective`   | Post-mission learning extraction               | sonnet        | none      |

Always use the exact `subagent_type` value shown above when spawning built-in agents. This ensures each agent runs with the correct tool permissions and isolation settings defined in its agent file. In particular, `mission-control:implementer` must be used for all implementation tasks — it is the only agent type that runs in an isolated git worktree.

Custom agents from `.mission-control/settings.md` extend (never replace) the built-in agents. Each custom agent maps to one of the four core `subagent_type` values: `Explore`, `Plan`, `Bash`, or `general-purpose`. Never apply the `mission-control:*` prefix to custom agents — only built-in agents have registered agent files under that namespace.

Output the merged registry, including the exact `subagent_type` to use for each agent:

```
AGENT REGISTRY
---------------------------------------------------------------------
Built-in:
  mission-planner  → mission-control:mission-planner
  researcher       → mission-control:researcher
  implementer      → mission-control:implementer  (isolated worktree)
  reviewer         → mission-control:reviewer
  retrospective    → mission-control:retrospective
Custom:
  [agent-name]     → [subagent_type from settings]  (or "none")
---------------------------------------------------------------------
```

### 3b. Select Planning Depth

Choose the planning depth based on task size:

| Depth | When to Use                               | What It Produces                                    |
| ----- | ----------------------------------------- | --------------------------------------------------- |
| skip  | 1 file, trivial change                    | Directly execute, no task graph needed              |
| lite  | 2-3 files, straightforward                | Flat task list, minimal dependencies                |
| spec  | 4+ files, moderate complexity             | Full task graph with dependencies and waves         |
| full  | Architectural changes, cross-cutting work | Detailed spec document + task graph + risk analysis |

If `skip` depth is selected, bypass the rest of the orchestration workflow. Execute the change directly with tools. For all other depths, continue.

Reference [references/task-decomposition.md](references/task-decomposition.md) for dependency graph construction, parallel grouping, critical path identification, and Kahn's algorithm for topological ordering.

### 3c. List Subtasks

List all subtasks now in dependency order. For each subtask, produce a task card:

```
TASK [ID]: [Name]
  Agent Type:     [mission-planner / researcher / implementer / reviewer / retrospective / <custom-type>]
  Deliverable:    [What this task produces]
  Dependencies:   [Task IDs that must complete first, or "none"]
  Risk Tier:      [0-3]
  File Ownership: [Specific files this agent owns, or "read-only"]
  Model:          [haiku / sonnet / opus]
```

Rules for task cards:

- Every task must have exactly one agent type.
- File ownership must not overlap between concurrent tasks. If two tasks need the same file, they must be sequential.
- Implementation tasks must depend on their corresponding research tasks.
- Reviewer tasks must depend on the implementation they review.
- Tasks with no dependencies form the first wave and launch in parallel.

### 3d. Identify Waves

Group tasks into execution waves based on dependencies:

```
EXECUTION PLAN
---------------------------------------------------------------------
Wave 1 (parallel): Task 1, Task 2, Task 3, Task 4   [no dependencies]
Wave 2 (sequential): Task 5                          [depends on Wave 1]
Wave 3 (parallel): Task 6, Task 7                    [depends on Task 5]
Wave 4 (sequential): Task 8                          [depends on Wave 3]
Wave 5 (sequential): Task 9                          [depends on Wave 4]
---------------------------------------------------------------------
Critical path: Task 1 -> Task 5 -> Task 7 -> Task 8 -> Task 9
```

---

## Step 4: Select Orchestration Pattern

### 4a. Choose a Pattern

Select the pattern that best fits the mission's structure:

**1. Fan-Out / Fan-In** — Multiple independent queries, then synthesize results.
Use when: several independent research queries, searching across different areas, running independent analyses.

```
Orchestrator
  |-- Agent A (area 1) --\
  |-- Agent B (area 2) ---+-> Synthesize
  \-- Agent C (area 3) --/
```

**2. Pipeline** — Sequential stages where each output feeds the next.
Use when: natural ordering exists (research -> plan -> implement -> validate).

```
Agent A -> Agent B -> Agent C -> Final Output
(research)  (plan)    (implement)
```

**3. Explore-Then-Act** — Deep exploration phase, then focused action.
Use when: unfamiliar codebases, complex bugs, refactoring where understanding must precede changes.

```
Explore agents (parallel) -> Orchestrator decides -> Action agents
```

**4. Competitive** — Multiple agents attempt the same task with different approaches; pick the best.
Use when: algorithm design, performance optimization, uncertain best approach.

```
Orchestrator
  |-- Agent A (approach 1) --\
  |-- Agent B (approach 2) ---+-> Evaluate & Select
  \-- Agent C (approach 3) --/
```

**5. Iterative Refinement** — Implement, review, fix loop until quality threshold is met.
Use when: code review cycles, documentation quality, complex implementations needing validation.

```
Agent A (implement) -> Agent B (review) -> [issues?] -> Agent A (fix) -> Agent B (re-review)
```

**6. Supervisor with Workers** — Persistent supervisor delegates to short-lived workers.
Use when: many small subtasks across files, project-wide refactoring, batch operations.

```
Supervisor (persistent)
  |-- Worker 1 (file A) -> done
  |-- Worker 2 (file B) -> done
  |-- Worker 3 (file C) -> done
  \-- ... continues until all complete
```

**7. Adaptive Retry** — Automatic retry with escalated model on failure. Wraps any of the above patterns.
Use when: retryOnFailure is true in settings. Applied automatically when an agent fails.

```
Agent A (haiku) -> [fail] -> Agent A' (sonnet) -> [fail] -> Agent A'' (opus) -> [fail] -> Escalate to user
```

Reference [references/orchestration-patterns.md](references/orchestration-patterns.md) for detailed examples of each pattern.

### 4b. Choose Execution Mode

Select the execution mode based on mission characteristics:

| Mission Characteristics                     | Execution Mode                           |
| ------------------------------------------- | ---------------------------------------- |
| Sequential work or same files               | Direct tools (no subagents)              |
| 2-3 independent read-only queries           | Standalone subagents (no team)           |
| Parallel work (3+ agents or any writes)     | **Agent-team (DEFAULT)**                 |
| Parallel work + agent-to-agent coordination | Agent-team with peer messaging           |
| High risk (Tier 2+)                         | Agent-team + dedicated reviewer teammate |

Default to agent-team mode. Only use standalone subagents for trivial fan-out of 2-3 read-only research agents where no coordination is needed. Only use direct tools for `skip` planning depth.

State your pattern and execution mode choice explicitly:

```
ORCHESTRATION
---------------------------------------------------------------------
Pattern:        [Pattern name]
Execution Mode: [direct / standalone / agent-team / agent-team+messaging]
Rationale:      [One sentence justification]
---------------------------------------------------------------------
```

---

## Step 5: Create Team & Launch Agents

Execute this step NOW. Do not describe what you plan to do. Act.

### 5a. Create the Team

Use `TeamCreate` to establish the team:

```
TeamCreate(team_name: "<mission-name>", description: "<brief mission description>")
```

Name the team after the mission goal (kebab-case, descriptive).

### 5b. Create Tasks with Dependencies

Use `TaskCreate` for every subtask from Step 3. Set up dependencies with `TaskUpdate(addBlockedBy)` to enforce execution order.

### 5c. Spawn All Independent Agents in ONE Message

Identify every task with no dependencies (Wave 1). Spawn agents for ALL of them in a single message. Do not spawn them one at a time.

For each agent, write a self-contained prompt that includes:

1. **Role context** — "You are a [agent type]: [description from registry]."
2. **Exact file paths** — Specific files to search, read, or modify.
3. **Task specification** — Precisely what to find, implement, or validate.
4. **Expected output format** — What the deliverable looks like (report, code, review verdict).
5. **Constraints** — Forbidden actions, file ownership boundaries, risk tier.
6. **Task management** — "Claim your task via TaskUpdate when starting. Mark it completed when done."

Choose the right model per agent:

- `haiku` — Simple searches, running commands, straightforward tasks.
- `sonnet` — Moderate complexity, most implementation work (default).
- `opus` — Complex reasoning, architecture decisions, security review.

For Tier 1+ tasks, spawn a reviewer agent AFTER the implementation agent completes. Never spawn implementer and reviewer for the same work simultaneously.

### 5d. Save Mission State

Save the mission state to `.mission-control/missions/active.json`. Include the mission scope, risk tier, task graph, pattern, settings, and current status. This enables session recovery if the conversation is interrupted.

```json
{
  "id": "mission-<timestamp>",
  "name": "<mission name>",
  "goal": "<goal>",
  "status": "active",
  "createdAt": "<ISO-8601>",
  "updatedAt": "<ISO-8601>",
  "scope": { ... },
  "settings": { ... },
  "pattern": "<pattern>",
  "riskTier": <tier>,
  "tasks": [ ... ],
  "log": [],
  "playbook": "<playbook name or null>"
}
```

### Standalone Subagent Fallback

Only skip team creation for trivial fan-out of 2-3 read-only research agents where no coordination is needed. In that case, launch standalone `Task` calls without `team_name`.

### Example Team Launch

```
TeamCreate(team_name: "preferences-feature", description: "Add user preferences page")

TaskCreate(subject: "Find auth patterns", ...)
TaskCreate(subject: "Find routing config", ...)
TaskCreate(subject: "Find theme implementation", ...)
TaskCreate(subject: "Find i18n config", ...)

[Spawn 4 agents in ONE message — all with no dependencies]
Task(team_name: "preferences-feature", name: "researcher-auth", subagent_type: "mission-control:researcher", ...)
Task(team_name: "preferences-feature", name: "researcher-routing", subagent_type: "mission-control:researcher", ...)
Task(team_name: "preferences-feature", name: "researcher-theme", subagent_type: "mission-control:researcher", ...)
Task(team_name: "preferences-feature", name: "researcher-i18n", subagent_type: "mission-control:researcher", ...)
```

---

## Step 6: Monitor & Adjust

### 6a. Track Progress

Use `TaskList` to check team progress after each wave. Teammates send messages when they complete tasks or need help.

### 6b. Produce Checkpoint Reports

After each wave completes, produce a checkpoint report:

```
CHECKPOINT REPORT
---------------------------------------------------------------------
Wave:              [Current wave number]
Tasks Completed:   [IDs and names]
Tasks In Progress: [IDs and agents]
Tasks Blocked:     [IDs -> Blocker -> Next Action]
Budget Burn:       [Tokens used / estimated total]
Risk Updates:      [New risks discovered during execution]
Decision:          CONTINUE | RESCOPE | STOP
Rationale:         [Why this decision]
---------------------------------------------------------------------
```

### 6c. Adaptive Execution

Apply these adjustments in real time:

1. **Agent failure.** If an agent fails its task and `retryOnFailure` is true:
   - Retry attempt 1: Escalate model (haiku -> sonnet, or sonnet -> opus) if `escalateModelOnRetry` is true. Otherwise retry with same model and a refined prompt.
   - Retry attempt 2+: Escalate model again if not already at opus. Refine the prompt with additional context from the failure.
   - After `maxRetries` exhausted: Mark task as blocked, report to user, recommend action.

2. **Task too complex.** If an agent reports the task exceeds its scope:
   - Split into 2-3 smaller subtasks with tighter file ownership.
   - Assign new agents and update the task graph.

3. **Agent stalled.** If an agent produces no meaningful output:
   - Send a status check message via `SendMessage`.
   - If still unresponsive, spawn a replacement agent with a clearer prompt and mark the original as abandoned.

4. **Drift detection.** If completed work diverges from the success metric:
   - Rescope immediately. Do not continue on a divergent path.
   - Update the mission scope and remaining tasks.

### 6d. Launch Next Waves

After each wave, identify tasks whose dependencies are now satisfied. Spawn agents for all newly unblocked tasks in a single message. Use `TaskUpdate` to assign owners and update status.

### 6e. Save Checkpoint to Mission State

After each checkpoint, update `.mission-control/missions/active.json` with current progress: task statuses, completed artifacts, log entries, and timestamp.

---

## Step 7: Close Out

### 7a. Merge Findings

When all tasks are complete:

1. Collect deliverables from every agent.
2. Merge findings into a coherent result. Do not dump raw agent outputs.
3. Resolve conflicts between agent outputs — if two agents disagree, evaluate evidence and pick the better-supported conclusion.
4. Identify gaps — if critical work is missing, spawn follow-up agents before closing.

### 7b. Produce Completion Summary

```
COMPLETION SUMMARY
---------------------------------------------------------------------
Planned Outcome:     [From Step 1]
Achieved Outcome:    [What actually got delivered]
Artifacts:           [Files created/modified with full paths]
Key Decisions:       [Important choices made during execution]
Validation Evidence: [Test results, review outcomes, manual verification]
Open Risks:          [Unresolved issues or technical debt]
Follow-Ups:          [Work items for future sessions]
Lessons Learned:     [Reusable patterns or anti-patterns discovered]
---------------------------------------------------------------------
```

Present this summary to the user as the final deliverable.

### 7c. Extract Learnings

If `autoLearn` is enabled in settings:

1. Spawn a retrospective agent to analyze the completed mission.
2. The retrospective agent examines: which patterns worked, which failed, what the root causes were, which models were right for which tasks, and what prompt patterns produced good results.
3. Save extracted learnings to `.mission-control/memory/` as tagged markdown files.
4. Each learning file uses this format:

```yaml
---
tags: [relevant, topic, tags]
source: mission-<id>
extractedAt: <ISO-8601>
confidence: high | medium | low
category: pattern | gotcha | architecture | tooling | prompt
---
# Learning Title

[Structured description of the learning with specific details and examples.]
```

### 7d. Archive Mission State

1. Move `.mission-control/missions/active.json` to `.mission-control/missions/archive/<mission-id>.json`.
2. Update the archive entry with the completion summary, final task statuses, and extracted learnings.
3. The active mission file is now cleared. A new mission can begin.

### 7e. Clean Up

1. Send shutdown requests to all teammates via `SendMessage(type: "shutdown_request")`.
2. Delete the team with `TeamDelete` after all teammates confirm shutdown.

---

## Operational Doctrine

Apply these principles throughout every mission:

1. **Load settings before scoping.** Always read organization and project settings files before producing the mission scope. Settings control planning depth, approval requirements, model selection, and retry behavior.

2. **Save state after each checkpoint.** Persist mission state to `.mission-control/missions/active.json` after every checkpoint report. This enables session recovery and provides an audit trail.

3. **Use playbooks when available.** If a playbook matches the mission type, use it. Playbooks encode proven task graphs and save decomposition time. Suggest matches but allow the user to override.

4. **Default to teams.** Create a team for any mission with 3+ agents or any agent that writes files. Only skip teams for trivial fan-out of 2-3 read-only agents.

5. **Optimize for throughput.** Assign work to complete the critical path fastest. Do not distribute work equally — optimize for the longest dependency chain.

6. **Use TaskList for visibility.** Check `TaskList` between waves to track progress and unblock work. Do not proceed blindly.

7. **Coordinate via messages.** Use `SendMessage` to direct teammates, share context from earlier waves, or reassign work when plans change.

8. **Replace stalled agents immediately.** Do not wait on undefined blockers. Spawn a replacement teammate with a clearer, more constrained prompt.

9. **Escalate uncertainty early.** If blocked on a decision, present options to the user with one recommended path. Do not guess on ambiguous requirements.

10. **Write excellent prompts.** Agent effectiveness depends entirely on prompt clarity. Include exact file paths, constraints, expected format, risk tier, and task management instructions in every agent prompt.

11. **Launch in parallel.** If two tasks have no dependency between them, spawn agents in the same message. Sequential launches of independent work kill throughput.

12. **Clean shutdown.** Always send `shutdown_request` to all teammates and `TeamDelete` when the mission is complete. Do not leave orphaned agents.

13. **Never duplicate work.** Do not repeat searches you already delegated to agents. Trust agent outputs unless there is reason to doubt them.

---

## Anti-Patterns

Never do these:

- **Over-orchestrating.** Do not spawn agents for trivial tasks (reading 1 file, running 1 command). Use tools directly. The `skip` planning depth exists for this.

- **Vague prompts.** "Look at the code and figure it out" is not a prompt. Agents cannot read your mind. Specify exact file paths, what to find, what format to return, and what constraints apply.

- **Sequential when parallel is possible.** Launching agents one by one when they have no dependencies wastes time. Identify all independent tasks and launch them simultaneously.

- **Ignoring dependencies.** Launching implementation before research completes produces work based on wrong assumptions. Enforce the dependency graph.

- **Splitting one file across agents.** Multiple agents editing the same file create merge conflicts. Assign clear file ownership — one agent per file at any given time.

- **Forgetting synthesis.** Dumping raw agent outputs to the user is not a deliverable. Always merge, deduplicate, and present a coherent summary.

- **Adding agents without reducing critical path.** More agents only help if they shorten the longest dependency chain. Do not parallelize work that is already sequential.

- **Skipping the reviewer for Tier 1+ work.** The reviewer catches bugs and architectural violations that the implementer misses. Skipping review for medium-risk-or-higher work invites production incidents.

- **Ignoring loaded learnings.** If mission memory contains relevant gotchas or patterns, incorporate them into agent prompts. Past mistakes should not repeat.

- **Not saving state.** If the conversation is interrupted without saved state, the entire mission must restart from scratch. Save after every checkpoint.

---

## Full Example: Add a User Preferences Page

**User request:** "Add a user preferences page with dark mode toggle, language selector, and notification settings"

### Step 1 — Scope the Mission

Settings loaded from `.mission-control/settings.md`: testCommand="npm test", useWorktrees=true, autoReview=true.

No matching playbook found. No relevant learnings loaded (fresh project).

```
MISSION SCOPE
---------------------------------------------------------------------
Outcome:        Ship a working preferences page with three settings sections
Success Metric: All three controls persist user choices and are covered by tests
Budget:         Standard session, no external API costs
Constraints:    Follow existing UI patterns, no breaking changes to auth
In Scope:       New preferences page, dark mode toggle, language selector, notification settings
Out of Scope:   Profile editing, account deletion, OAuth provider changes
Stop Criteria:  If any setting requires backend migration, escalate to user first
Deliverables:   Preferences page component, API endpoint, tests, updated routing
---------------------------------------------------------------------
```

### Step 2 — Risk Assessment

```
RISK ASSESSMENT
---------------------------------------------------------------------
Overall Mission:          Tier 0 (Low) - new page, easy rollback, no sensitive data
  Dark mode toggle:       Tier 0 - isolated UI change
  Language selector:      Tier 1 (Medium) - touches i18n system, requires reviewer
  Notification settings:  Tier 0 - new isolated component
---------------------------------------------------------------------
```

Tier 1 work detected (language selector). A reviewer agent is required for the i18n integration.

### Step 3 — Decomposition

```
AGENT REGISTRY
---------------------------------------------------------------------
Built-in:  mission-planner | researcher | implementer | reviewer | retrospective
Custom:    none
---------------------------------------------------------------------
```

Planning depth: **spec** (4+ files, moderate complexity).

```
TASK 1: Find existing settings/preferences patterns
  Agent Type:     researcher
  Deliverable:    List of files implementing settings UI with code snippets
  Dependencies:   none
  Risk Tier:      0
  File Ownership: read-only
  Model:          haiku

TASK 2: Find routing config and layout components
  Agent Type:     researcher
  Deliverable:    Routing file paths and layout component structure
  Dependencies:   none
  Risk Tier:      0
  File Ownership: read-only
  Model:          haiku

TASK 3: Find current theme/dark-mode implementation
  Agent Type:     researcher
  Deliverable:    Theme system architecture and toggle mechanism
  Dependencies:   none
  Risk Tier:      0
  File Ownership: read-only
  Model:          haiku

TASK 4: Find i18n/language configuration
  Agent Type:     researcher
  Deliverable:    i18n setup, language switching, namespace registration
  Dependencies:   none
  Risk Tier:      0
  File Ownership: read-only
  Model:          haiku

TASK 5: Design preferences page architecture
  Agent Type:     mission-planner
  Deliverable:    Implementation plan with file structure and component hierarchy
  Dependencies:   Tasks 1, 2, 3, 4
  Risk Tier:      0
  File Ownership: read-only
  Model:          sonnet

TASK 6: Implement preferences data model and API
  Agent Type:     implementer
  Deliverable:    API endpoint, data model, persistence layer
  Dependencies:   Task 5
  Risk Tier:      0
  File Ownership: models/*, api/preferences.*
  Model:          sonnet

TASK 7: Implement preferences UI page
  Agent Type:     implementer
  Deliverable:    React component with dark mode, language, notification sections
  Dependencies:   Task 5
  Risk Tier:      1 (i18n integration)
  File Ownership: components/preferences/*
  Model:          sonnet

TASK 8: Review i18n integration
  Agent Type:     reviewer
  Deliverable:    Review report — PASS / PASS WITH NOTES / FAIL
  Dependencies:   Task 7
  Risk Tier:      1
  File Ownership: read-only
  Model:          sonnet

TASK 9: Run tests and type checks
  Agent Type:     implementer
  Deliverable:    Test results and type check output — all green
  Dependencies:   Tasks 6, 7, 8
  Risk Tier:      0
  File Ownership: N/A
  Model:          haiku
```

```
EXECUTION PLAN
---------------------------------------------------------------------
Wave 1 (parallel): Tasks 1, 2, 3, 4     [no dependencies — research phase]
Wave 2 (sequential): Task 5              [depends on Wave 1 — planning phase]
Wave 3 (parallel): Tasks 6, 7           [depends on Task 5 — implementation phase]
Wave 4 (sequential): Task 8             [depends on Task 7 — review phase]
Wave 5 (sequential): Task 9             [depends on Tasks 6, 7, 8 — validation phase]
---------------------------------------------------------------------
Critical path: Task 1 -> Task 5 -> Task 7 -> Task 8 -> Task 9
```

### Step 4 — Pattern Selection

```
ORCHESTRATION
---------------------------------------------------------------------
Pattern:        Explore-Then-Act with Fan-Out for the exploration phase
Execution Mode: agent-team (parallel work with writes in Wave 3)
Rationale:      4 independent research tasks fan out, then sequential plan/implement/review
---------------------------------------------------------------------
```

### Step 5 — Launch

**Wave 1:** Launch Tasks 1-4 in a single message with 4 `Task` tool calls:

```
TeamCreate(team_name: "preferences-feature", description: "Add user preferences page with dark mode, language, and notifications")

TaskCreate(subject: "Find settings/preferences patterns", ...)
TaskCreate(subject: "Find routing config", ...)
TaskCreate(subject: "Find theme/dark-mode implementation", ...)
TaskCreate(subject: "Find i18n configuration", ...)

Task(team_name: "preferences-feature", name: "researcher-settings", subagent_type: "Explore", model: "haiku",
  prompt: "You are a researcher: read-only codebase exploration specialist.
  Task: Find all existing settings or preferences UI patterns in this project.
  Search for: settings pages, preferences components, user configuration UI.
  Report: file paths, component structure, state management approach, API patterns used.
  Claim task 'Find settings/preferences patterns' via TaskUpdate. Mark completed when done.")

Task(team_name: "preferences-feature", name: "researcher-routing", subagent_type: "Explore", model: "haiku",
  prompt: "You are a researcher: read-only codebase exploration specialist.
  Task: Find the routing configuration and layout components.
  Search for: route definitions, layout wrappers, navigation components, page templates.
  Report: exact file paths, how new routes are added, which layout wraps authenticated pages.
  Claim task 'Find routing config' via TaskUpdate. Mark completed when done.")

Task(team_name: "preferences-feature", name: "researcher-theme", subagent_type: "Explore", model: "haiku",
  prompt: "You are a researcher: read-only codebase exploration specialist.
  Task: Find the current theme and dark mode implementation.
  Search for: theme provider, dark mode toggle, CSS variables, theme context.
  Report: architecture of the theme system, how to toggle dark mode, where theme state is stored.
  Claim task 'Find theme/dark-mode implementation' via TaskUpdate. Mark completed when done.")

Task(team_name: "preferences-feature", name: "researcher-i18n", subagent_type: "Explore", model: "haiku",
  prompt: "You are a researcher: read-only codebase exploration specialist.
  Task: Find the i18n and language configuration.
  Search for: i18n provider, translation files, language switching, namespace registration.
  Report: i18n library used, how translations are organized, how to add a new namespace, how language selection is persisted.
  Claim task 'Find i18n configuration' via TaskUpdate. Mark completed when done.")
```

Save mission state to `.mission-control/missions/active.json`.

### Step 6 — Monitor

**After Wave 1 completes:**

```
CHECKPOINT REPORT
---------------------------------------------------------------------
Wave:              1 (Research)
Tasks Completed:   1 (settings), 2 (routing), 3 (theme), 4 (i18n)
Tasks In Progress: none
Tasks Blocked:     none
Budget Burn:       ~15% of session budget
Risk Updates:      none
Decision:          CONTINUE
Rationale:         All research complete, findings consistent, ready for planning
---------------------------------------------------------------------
```

Launch Task 5 (planning). After Task 5 completes, launch Tasks 6 and 7 in parallel. After Task 7 completes, launch Task 8 (reviewer). After Task 8 completes (assuming PASS or PASS WITH NOTES), launch Task 9.

If Task 8 returns FAIL: fix the issues identified by the reviewer by spawning a new implementer agent with the required changes, then re-run the reviewer. This is the Iterative Refinement sub-pattern.

### Step 7 — Close Out

```
COMPLETION SUMMARY
---------------------------------------------------------------------
Planned Outcome:     Ship a working preferences page with three settings sections
Achieved Outcome:    Delivered fully functional preferences page with all three settings
Artifacts:
  - components/preferences/PreferencesPage.tsx (new)
  - components/preferences/DarkModeToggle.tsx (new)
  - components/preferences/LanguageSelector.tsx (new)
  - components/preferences/NotificationSettings.tsx (new)
  - api/preferences.ts (new)
  - models/UserPreferences.ts (new)
  - __tests__/preferences.test.tsx (new)
Key Decisions:
  - Reused existing theme context for dark mode toggle
  - Reused i18n provider with new "preferences" namespace for language selector
  - Stored preferences in localStorage with API sync on change
Validation Evidence:
  - All tests passing (8/8)
  - Type checks clean
  - i18n integration reviewed and approved (Task 8: PASS)
Open Risks:
  - None — Tier 1 review completed successfully
Follow-Ups:
  - Consider adding preferences export/import feature
  - Add analytics tracking for settings changes
Lessons Learned:
  - Parallel exploration phase (Tasks 1-4) saved significant time vs sequential
  - Tier 1 review caught missing i18n namespace registration early
  - haiku was sufficient for all 4 research tasks (cost-effective)
---------------------------------------------------------------------
```

Retrospective agent spawned (autoLearn=true). Learning extracted: "Always register i18n namespaces before implementing components that use translations."

Mission state archived to `.mission-control/missions/archive/mission-<id>.json`. Active mission cleared.

---

## References

- For full tier definitions (0-3), required controls per tier, and the failure-mode checklist for Tier 1+ tasks, see [references/risk-tiers.md](references/risk-tiers.md)
- For dependency graph construction, parallel grouping, critical path identification, Kahn's algorithm for topological ordering, and planning depth selection criteria, see [references/task-decomposition.md](references/task-decomposition.md)
- For detailed descriptions and examples for all 7 orchestration patterns: Fan-Out/Fan-In, Pipeline, Explore-Then-Act, Competitive, Iterative Refinement, Supervisor with Workers, and Adaptive Retry, see [references/orchestration-patterns.md](references/orchestration-patterns.md)
- For reusable templates for mission scope, task cards, checkpoint reports, and completion summaries, see [references/templates.md](references/templates.md)
