# Templates

Reusable templates for mission lifecycle documents. Copy and fill in the bracketed fields.

---

## 1. Mission Scope Template

Define the mission boundaries before decomposition begins.

```
MISSION SCOPE
═════════════

Mission ID:     [auto-generated, e.g., mission-20260225-143000]
Mission Name:   [short descriptive name]
Created:        [ISO-8601 timestamp]

OUTCOME
  What does "done" look like?
  [1-2 sentences describing the desired end state]

SUCCESS METRIC
  How do we measure success?
  [Quantifiable or verifiable criteria, e.g., "all tests pass", "endpoint returns 200", "page renders in <2s"]

BUDGET
  Token/turn limits:
  [e.g., "max 300 turns total", "max 50K tokens", or "no hard limit"]

CONSTRAINTS
  - [technical constraint, e.g., "must use existing auth middleware"]
  - [process constraint, e.g., "no changes to database schema"]
  - [environment constraint, e.g., "must work on Node 22"]

IN SCOPE
  - [specific deliverable or change]
  - [specific deliverable or change]

OUT OF SCOPE
  - [explicitly excluded item]
  - [explicitly excluded item]

STOP CRITERIA
  When should the mission abort early?
  - [e.g., "3 consecutive task failures"]
  - [e.g., "budget exceeds 80% with <50% tasks complete"]
  - [e.g., "Tier 2+ risk discovered that was not in scope"]

DELIVERABLES
  What artifacts will be produced?
  - [e.g., "modified files committed to feature branch"]
  - [e.g., "test suite covering new functionality"]
  - [e.g., "completion summary with validation evidence"]

ORCHESTRATION PATTERN: [fan-out | pipeline | explore-then-act | competitive | iterative | supervisor | adaptive-retry]
OVERALL RISK TIER:     [0 | 1 | 2 | 3]
PLANNING DEPTH:        [skip | lite | spec | full]
```

---

## 2. Task Card Template

Standard format for every task in the dependency graph.

```
TASK CARD
═════════

ID:              [T1, T2, ... — unique within the mission]
Name:            [short descriptive name, <60 chars]
Agent type:      [researcher | mission-planner | implementer | reviewer | retrospective | <custom>]
Deliverable:     [what this task produces — file path, report, verdict, etc.]
Dependencies:    [T2, T3] or [] if none
Risk tier:       [0 | 1 | 2 | 3]
File ownership:  [list of files this agent will create or modify]
Model:           [haiku | sonnet | opus | default]
Validation:      [how to verify completion — test command, review criteria, acceptance check]

PROMPT CONTEXT (optional):
  Additional context to include in the agent's prompt:
  - [relevant finding from a predecessor task]
  - [specific pattern or constraint to follow]
  - [file paths to read before starting]

RETRY STRATEGY (if different from default):
  Max retries:   [0 | 1 | 2 | 3]
  Escalation:    [model ladder, e.g., haiku → sonnet → opus]
  Split on fail: [yes/no — if yes, describe how to split]
```

**Minimal task card (for Tier 0 tasks):**

```
ID: T1 | researcher | haiku
Name: Map existing route patterns
Deliverable: List of routes with file paths
Dependencies: []
Validation: Non-empty output with file paths
```

---

## 3. Checkpoint Report Template

Status report produced during mission execution via `/checkpoint`.

```
CHECKPOINT REPORT
═════════════════

Mission:   [mission name]
Time:      [ISO-8601 timestamp]
Elapsed:   [time since mission start]

PROGRESS
────────
  Completed:    [N] / [total] tasks ([percentage]%)
  In Progress:  [N] tasks
  Blocked:      [N] tasks
  Pending:      [N] tasks

COMPLETED TASKS
  [T1] [task name] .................. DONE  (haiku, 12 turns)
  [T2] [task name] .................. DONE  (sonnet, 28 turns)

IN PROGRESS
  [T3] [task name] .................. RUNNING (sonnet, 15/50 turns)

BLOCKED
  [T5] [task name] .................. BLOCKED on [T3, T4]
  Reason: [why it cannot proceed]

BUDGET
──────
  Turns used:   [N] / [budget] ([percentage]%)
  Retries:      [N] retries across [M] tasks
  Escalations:  [N] model escalations

RISK UPDATES
────────────
  [any risk tier changes, unexpected findings, or new risks identified]
  - [T3] escalated from Tier 1 → Tier 2: discovered auth implications
  - [none if no changes]

CRITICAL PATH STATUS
────────────────────
  Original estimate:  [N] waves
  Current progress:   Wave [X] of [N]
  On track:           [YES / NO — if NO, explain delay]

DECISION
────────
  Recommendation: [CONTINUE | RESCOPE | STOP]
  Rationale:      [why this recommendation]
  Action items:   [specific next steps if rescoping]
```

---

## 4. Completion Summary Template

Final report produced when the mission completes via `/debrief`.

```
COMPLETION SUMMARY
══════════════════

Mission:       [mission name]
ID:            [mission ID]
Duration:      [start time] → [end time] ([elapsed])
Status:        [COMPLETED | PARTIALLY COMPLETED | FAILED | ABORTED]

OUTCOME
───────
  Planned:  [original outcome from scope]
  Achieved: [what was actually delivered]
  Delta:    [any gaps between planned and achieved]

ARTIFACTS
─────────
  Files created:    [list of new files]
  Files modified:   [list of modified files]
  Files deleted:    [list of deleted files, if any]
  Branch:           [git branch name, if applicable]
  Commits:          [number of commits or commit hashes]

TASK SUMMARY
────────────
  Total tasks:  [N]
  Completed:    [N] ([percentage]%)
  Failed:       [N] (after retries)
  Skipped:      [N] (if any were deprioritized)

  Task breakdown:
  [T1] [name] ......... DONE   (haiku, 12 turns)
  [T2] [name] ......... DONE   (sonnet, 28 turns, 1 retry)
  [T3] [name] ......... DONE   (sonnet → opus, 45 turns, escalated)
  [T4] [name] ......... FAILED (sonnet, 50 turns, 2 retries)

KEY DECISIONS
─────────────
  1. [decision made during execution and rationale]
  2. [e.g., "Switched from competitive to pipeline pattern after research phase"]
  3. [e.g., "Escalated T3 to opus after two sonnet failures"]

VALIDATION EVIDENCE
───────────────────
  Tests:    [test command and result, e.g., "npm test — 47 passed, 0 failed"]
  Review:   [reviewer verdict, e.g., "PASS — reviewer T9 approved all changes"]
  Manual:   [any manual verification performed]

BUDGET
──────
  Turns used:      [N] / [budget]
  Retries:         [N] total
  Escalations:     [N] model escalations
  Estimated cost:  [if trackable]

OPEN RISKS
──────────
  - [any unresolved risks or known issues]
  - [e.g., "OAuth refresh token rotation not tested with expired tokens"]
  - [none if clean]

FOLLOW-UPS
──────────
  - [suggested future work that was out of scope]
  - [e.g., "Add rate limiting to new OAuth endpoints"]
  - [e.g., "Performance test with 1000 concurrent users"]

LESSONS LEARNED
───────────────
  What worked:
  - [e.g., "Explore-then-act pattern was effective for unfamiliar auth code"]
  - [e.g., "File ownership rules prevented merge conflicts in Wave 4"]

  What did not work:
  - [e.g., "haiku struggled with complex TypeScript generics in T4"]
  - [e.g., "Initial task decomposition missed the config file dependency"]

  Recommendations:
  - [e.g., "Use sonnet minimum for TypeScript generic-heavy tasks"]
  - [e.g., "Always include config files in research phase"]
```

---

## 5. Playbook Reference Template

Template for defining reusable mission playbooks. Playbooks encode proven workflows for common mission types.

```
PLAYBOOK
════════

---
name:             [lowercase-hyphenated-name]
description:      [1-2 sentence description of what this playbook does]
when-to-use:      [conditions under which this playbook is appropriate]
planning-depth:   [skip | lite | spec | full]
default-risk-tier: [0 | 1 | 2 | 3]
require-approval: [never | tier2+ | always]
estimated-waves:  [number of sequential waves]
estimated-tasks:  [approximate number of tasks]
---

## Goal Template
  [Parameterized goal description with {placeholders}]
  Example: "Implement {feature_name} with {backend|frontend|fullstack} scope"

## Phases

### Phase 1: [Phase Name]
  Purpose:    [what this phase accomplishes]
  Agents:     [agent types used in this phase]
  Parallel:   [yes | no]
  Risk tier:  [0 | 1 | 2 | 3]
  Tasks:
    - [task description with {placeholders}]
    - [task description]
  Exit criteria: [what must be true before moving to next phase]

### Phase 2: [Phase Name]
  Purpose:    [what this phase accomplishes]
  Agents:     [agent types used]
  Parallel:   [yes | no]
  Depends on: [Phase 1]
  Risk tier:  [0 | 1 | 2 | 3]
  Tasks:
    - [task description]
    - [task description]
  Exit criteria: [what must be true]

### Phase 3: [Phase Name]
  ...

## Success Criteria
  - [criterion 1, e.g., "all tests pass"]
  - [criterion 2, e.g., "reviewer agent approves"]
  - [criterion 3, e.g., "no security issues flagged"]

## Common Customizations
  - [how to adapt this playbook for variations]
  - [e.g., "For frontend-only: skip Phase 2 (backend)"]
  - [e.g., "For high-risk: add a Tier 2 security review phase after Phase 3"]
```

**Example — filled-in playbook reference:**

```
---
name:             bug-investigation
description:      Systematic bug investigation from reproduction to verified fix
when-to-use:      Bug report with unclear root cause; needs investigation before fix
planning-depth:   spec
default-risk-tier: 1
require-approval: never
estimated-waves:  5
estimated-tasks:  6-8
---

## Goal Template
  Investigate and fix: {bug_description}

## Phases

### Phase 1: Reproduce
  Purpose:    Confirm the bug exists and understand symptoms
  Agents:     [researcher]
  Parallel:   no
  Risk tier:  0
  Tasks:
    - Read the bug report and identify affected code paths
    - Attempt to reproduce via test or manual steps
  Exit criteria: Bug reproduced with clear steps, or confirmed unreproducible

### Phase 2: Trace
  Purpose:    Find the root cause
  Agents:     [researcher]
  Parallel:   no
  Risk tier:  0
  Tasks:
    - Trace execution path from trigger to symptom
    - Identify the exact line(s) causing incorrect behavior
  Exit criteria: Root cause identified with file path and line number

### Phase 3: Fix
  Purpose:    Implement the fix
  Agents:     [implementer]
  Parallel:   no
  Depends on: [Phase 2]
  Risk tier:  1
  Tasks:
    - Implement minimal fix addressing root cause
    - Add regression test covering the bug scenario
  Exit criteria: Fix compiles, regression test passes

### Phase 4: Verify
  Purpose:    Ensure fix is correct and complete
  Agents:     [reviewer]
  Parallel:   no
  Depends on: [Phase 3]
  Risk tier:  1
  Tasks:
    - Run full test suite
    - Review fix for edge cases and side effects
  Exit criteria: All tests pass, reviewer approves

## Success Criteria
  - Bug no longer reproducible
  - Regression test added and passing
  - No existing tests broken
  - Reviewer approves fix

## Common Customizations
  - For security bugs: escalate all phases to Tier 2, use adversarial review
  - For performance bugs: add a benchmarking step in Phase 4
  - For intermittent bugs: extend Phase 1 with multiple reproduction attempts
```
