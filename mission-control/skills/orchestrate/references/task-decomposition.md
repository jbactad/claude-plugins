# Task Decomposition

How to break a mission goal into a structured task graph with dependencies, parallel groups, and execution order.

---

## Dependency Graphs (DAG)

Every mission decomposes into a Directed Acyclic Graph (DAG) of tasks. Each node is a task. Each edge means "this task must complete before that task can start."

```
  T1 ───► T3 ───► T5
              ╱        ╲
  T2 ───► T4            T6
```

In this graph:
- T1 and T2 have no dependencies (can start immediately, in parallel)
- T3 depends on T1; T4 depends on T2
- T5 depends on T3 and T4 (waits for both)
- T6 depends on T5

**Rules for constructing the DAG:**
1. Every task must have a unique ID (e.g., `T1`, `T2`, ...).
2. Dependencies are listed as task IDs: `dependencies: [T1, T3]`.
3. No cycles allowed. If A depends on B and B depends on A, the graph is invalid. Restructure by merging the tasks or introducing an intermediate task.
4. A task with an empty dependency list can start immediately.
5. A task with multiple dependencies waits for ALL of them to complete.

---

## Topological Sort (Kahn's Algorithm)

To determine a valid execution order, use topological sorting. Kahn's algorithm works as follows:

1. **Count incoming edges.** For each task, count how many tasks it depends on (its "in-degree").
2. **Seed the queue.** Add all tasks with in-degree 0 (no dependencies) to a queue.
3. **Process the queue.** Remove a task from the queue, add it to the execution order, then reduce the in-degree of all tasks that depend on it by 1. If any task's in-degree reaches 0, add it to the queue.
4. **Repeat** until the queue is empty.
5. **Cycle check.** If the execution order contains fewer tasks than the total, a cycle exists. The mission plan is invalid and must be restructured.

**Worked example:**

Given: T1 (no deps), T2 (no deps), T3 (depends on T1), T4 (depends on T1, T2), T5 (depends on T3, T4)

```
Step 1: In-degrees: T1=0, T2=0, T3=1, T4=2, T5=2
Step 2: Queue = [T1, T2]
Step 3: Process T1 → order=[T1], reduce T3 (now 0), T4 (now 1). Queue=[T2, T3]
Step 4: Process T2 → order=[T1,T2], reduce T4 (now 0). Queue=[T3, T4]
Step 5: Process T3 → order=[T1,T2,T3], reduce T5 (now 1). Queue=[T4]
Step 6: Process T4 → order=[T1,T2,T3,T4], reduce T5 (now 0). Queue=[T5]
Step 7: Process T5 → order=[T1,T2,T3,T4,T5]. Queue=[]
Final:  [T1, T2, T3, T4, T5] — valid, 5 tasks processed out of 5.
```

---

## Parallel Grouping

Tasks that can execute concurrently are grouped into "waves." A wave contains all tasks whose dependencies have been satisfied.

**Algorithm:**
1. Run topological sort.
2. Assign each task a "depth" = 1 + max depth of its dependencies (tasks with no dependencies have depth 0).
3. Tasks at the same depth form a wave and can run in parallel.

**Example:**

```
Depth 0 (Wave 1):  T1, T2          ← launch in parallel
Depth 1 (Wave 2):  T3, T4          ← launch after Wave 1 completes
Depth 2 (Wave 3):  T5              ← launch after Wave 2 completes
```

```
  Wave 1          Wave 2          Wave 3
  ┌─────┐        ┌─────┐        ┌─────┐
  │ T1  │───────►│ T3  │───────►│     │
  │     │   ╱    │     │   ╲    │ T5  │
  │ T2  │──►     │ T4  │────►   │     │
  └─────┘        └─────┘        └─────┘
```

**Concurrency limit:** Respect `maxConcurrentAgents` from mission settings. If Wave 2 has 4 tasks but `maxConcurrentAgents = 2`, split into sub-waves of 2.

---

## Critical Path

The critical path is the longest chain of dependent tasks through the DAG. It determines the minimum possible mission duration regardless of parallelism.

**How to find it:**
1. Calculate the "cost" of each task (estimated turns or time).
2. For each task, compute the longest path from any root to that task.
3. The task with the highest total path cost is the end of the critical path.
4. Trace back through its dependencies to find the full chain.

**Example:**

```
T1 (5 turns) ──► T3 (10 turns) ──► T5 (3 turns)    Total: 18 turns
T2 (3 turns) ──► T4 (4 turns)  ──► T5 (3 turns)    Total: 10 turns

Critical path: T1 → T3 → T5 (18 turns minimum)
```

**Why it matters:**
- Optimizing tasks NOT on the critical path does not reduce total mission time.
- If you need to speed up the mission, focus on splitting or simplifying critical-path tasks.
- When re-planning mid-mission, recalculate the critical path with updated estimates.

---

## Planning Depth Selection

Not every mission needs a full dependency graph. Select planning depth based on mission complexity.

### skip — No Decomposition

```
Goal → Single agent executes directly → Done
```

**When to use:**
- Task touches 1 file
- Description is under 50 words
- Implementation path is obvious
- Single agent can handle it in one pass

**Example:** "Fix the typo in `Header.tsx` on line 42."

### lite — Quick Task List

```
Goal → 2-4 task list (no dependency graph) → Execute sequentially → Done
```

**When to use:**
- Task touches 2-3 files
- Steps are clear and mostly sequential
- No complex dependencies between steps
- Can be completed in one wave

**Example:** "Add a copy-to-clipboard button to the CodeBlock component. Update the component file, add a toast notification, write a test."

### spec — Dependency Graph

```
Goal → Task cards with dependencies → Parallel grouping → Execute waves → Done
```

**When to use:**
- Task touches 4+ files
- Multiple agents needed
- Some tasks can run in parallel
- Needs a plan document before implementation

**Output:** Full task cards with IDs, dependencies, agent types, file ownership, risk tiers.

**Example:** "Add user profile page with avatar upload, name editing, and settings."

### full — Phased Plan with Approval

```
Goal → Phased plan → Human approval → Execute phase by phase → Checkpoints → Done
```

**When to use:**
- Architectural changes affecting multiple modules
- High-risk changes (Tier 2+)
- Multi-day or multi-session effort
- Needs human sign-off before implementation begins
- 10+ tasks across 3+ phases

**Output:** Phased plan document with dependency graph per phase, risk assessment, budget estimate, and approval gates between phases.

**Example:** "Migrate the application from REST to GraphQL, including schema design, resolver implementation, client updates, and test migration."

### Selection Flowchart

```
How many files are affected?
  └─ 1 file → skip
  └─ 2-3 files → lite
  └─ 4-9 files → spec
  └─ 10+ files ↓

Is this an architectural change or high risk?
  └─ YES → full
  └─ NO → spec
```

---

## Task Card Format

Every task in a mission uses this standard format:

```
ID:            T1
Name:          Short descriptive name
Agent type:    researcher | mission-planner | implementer | reviewer | retrospective | <custom>
Deliverable:   What this task produces (file, report, verdict, etc.)
Dependencies:  [T2, T3] or [] if none
Risk tier:     0 | 1 | 2 | 3
File ownership: [src/services/auth.ts, src/middleware/auth.ts]
Model:         haiku | sonnet | opus (or default from settings)
Validation:    How to verify the task is complete (test command, review criteria, etc.)
```

**Example task card:**

```
ID:            T3
Name:          Implement authentication middleware
Agent type:    implementer
Deliverable:   Modified src/middleware/auth.ts with JWT validation
Dependencies:  [T1, T2]
Risk tier:     2
File ownership: [src/middleware/auth.ts, src/middleware/auth.test.ts]
Model:         sonnet
Validation:    npm test -- --grep "auth middleware" passes; reviewer approves
```

---

## File Ownership Rules

File ownership prevents merge conflicts and ensures accountability.

**Rule 1: One file, one agent.**
Never assign the same file to two different agents in the same wave. If two tasks need to modify the same file, they must be sequential (one depends on the other).

**Rule 2: Ownership is declared upfront.**
Every task card lists the files it will create or modify. The supervisor validates no overlaps before launching a wave.

**Rule 3: Read access is unrestricted.**
Any agent can read any file. Ownership only restricts write access.

**Rule 4: Shared files force sequencing.**
If T3 and T4 both need to modify `config.ts`, add a dependency: T4 depends on T3 (or vice versa).

```
WRONG (conflict):
  T3 (owns config.ts) ──┐
                          ├── same wave, both write config.ts
  T4 (owns config.ts) ──┘

RIGHT (sequenced):
  T3 (owns config.ts) ──► T4 (owns config.ts)
```

**Rule 5: New files are owned by their creator.**
If a task creates a new file, that file is automatically owned by the creating task's agent.

---

## Example: Simple 3-Task Pipeline

**Mission:** "Add a health check endpoint to the Express server."

**Planning depth:** lite (3 files, straightforward)

```
T1: Research existing routes
    Agent: researcher | Model: haiku | Risk: 0
    Deliverable: List of existing route patterns and middleware
    Dependencies: []
    Files: (read-only)

T2: Implement health check endpoint
    Agent: implementer | Model: sonnet | Risk: 1
    Deliverable: src/routes/health.ts with GET /health endpoint
    Dependencies: [T1]
    Files: [src/routes/health.ts, src/routes/index.ts]

T3: Add test for health check
    Agent: implementer | Model: haiku | Risk: 0
    Deliverable: src/routes/health.test.ts
    Dependencies: [T2]
    Files: [src/routes/health.test.ts]
```

**Execution:**
```
Wave 1: T1 (research)
Wave 2: T2 (implement, uses T1's findings)
Wave 3: T3 (test, uses T2's code)
Critical path: T1 → T2 → T3
```

---

## Example: Complex 9-Task Fan-Out-Then-Pipeline

**Mission:** "Refactor the authentication system to support OAuth2 providers (Google, GitHub) alongside existing JWT auth."

**Planning depth:** full (10+ files, architectural, Tier 2)

```
Phase 1: Research (Fan-Out)
──────────────────────────
T1: Map current auth flow
    Agent: researcher | Model: haiku | Risk: 0
    Deliverable: Auth flow diagram with file paths
    Dependencies: []

T2: Audit session management
    Agent: researcher | Model: haiku | Risk: 0
    Deliverable: Session store analysis, token lifecycle
    Dependencies: []

T3: Research OAuth2 library options
    Agent: researcher | Model: sonnet | Risk: 0
    Deliverable: Library comparison (passport vs custom)
    Dependencies: []

Phase 2: Plan (Fan-In)
──────────────────────
T4: Design OAuth2 integration architecture
    Agent: mission-planner | Model: sonnet | Risk: 0
    Deliverable: Architecture document with migration plan
    Dependencies: [T1, T2, T3]

Phase 3: Implement (Pipeline)
─────────────────────────────
T5: Implement OAuth2 provider abstraction
    Agent: implementer | Model: sonnet | Risk: 2
    Deliverable: src/services/auth/oauth-provider.ts
    Dependencies: [T4]
    Files: [src/services/auth/oauth-provider.ts, src/types/auth.ts]

T6: Implement Google OAuth2 provider
    Agent: implementer | Model: sonnet | Risk: 2
    Deliverable: src/services/auth/providers/google.ts
    Dependencies: [T5]
    Files: [src/services/auth/providers/google.ts, src/config/oauth.ts]

T7: Implement GitHub OAuth2 provider
    Agent: implementer | Model: sonnet | Risk: 2
    Deliverable: src/services/auth/providers/github.ts
    Dependencies: [T5]
    Files: [src/services/auth/providers/github.ts]

Phase 4: Verify (Pipeline)
──────────────────────────
T8: Write integration tests
    Agent: implementer | Model: sonnet | Risk: 1
    Deliverable: src/services/auth/__tests__/oauth.test.ts
    Dependencies: [T6, T7]
    Files: [src/services/auth/__tests__/oauth.test.ts]

T9: Security review of auth changes
    Agent: reviewer | Model: opus | Risk: 2
    Deliverable: Security review verdict with failure-mode checklist
    Dependencies: [T8]
    Files: (read-only)
```

**Dependency graph:**

```
  T1 ──┐
       │
  T2 ──┼──► T4 ──► T5 ──┬──► T6 ──┬──► T8 ──► T9
       │                 │         │
  T3 ──┘                 └──► T7 ──┘
```

**Parallel grouping:**

```
Wave 1: T1, T2, T3      (3 researchers in parallel)
Wave 2: T4               (planner synthesizes research)
Wave 3: T5               (foundation — must complete alone)
Wave 4: T6, T7           (2 implementers in parallel)
Wave 5: T8               (test writer)
Wave 6: T9               (security reviewer)
```

**Critical path:** T1 (or T2 or T3, whichever is slowest) -> T4 -> T5 -> T6 (or T7) -> T8 -> T9

**Budget estimate:** 6 waves, ~9 agent sessions, estimated 200-400 turns total.
