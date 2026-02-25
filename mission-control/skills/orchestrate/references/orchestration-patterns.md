# Orchestration Patterns

Seven reusable patterns for coordinating multiple agents. Select the pattern that best fits the mission structure, then adapt as execution proceeds.

---

## 1. Fan-Out / Fan-In

Dispatch independent queries in parallel, then synthesize results into a unified deliverable.

**When to use:**
- Multiple independent investigations or analyses needed
- Tasks share no data dependencies
- Speed matters more than sequential reasoning
- Synthesis step can combine partial results

```
                    ┌─── Agent A ───┐
                    │               │
  Supervisor ──────┼─── Agent B ───┼──── Synthesizer ──── Result
                    │               │
                    └─── Agent C ───┘
        DISPATCH        PARALLEL          MERGE
```

**Concrete example — Codebase audit:**

| Step | Agent Type | Task |
|------|-----------|------|
| Fan-out | researcher (x3) | Agent A: scan for security vulnerabilities. Agent B: catalog deprecated API usage. Agent C: measure test coverage gaps. |
| Fan-in | reviewer | Synthesize findings into a prioritized remediation report. |

**Key considerations:**
- Each fan-out agent must own distinct files or concerns (no overlap).
- The synthesizer should receive structured output from each agent, not raw dumps.
- Budget: N parallel agents + 1 synthesizer. Set `maxConcurrentAgents` accordingly.

---

## 2. Pipeline

Sequential stages where each stage's output feeds the next. Work flows in one direction.

**When to use:**
- Each stage depends on the previous stage's output
- Clear phase boundaries (research, plan, implement, test)
- Quality gates needed between phases
- Standard feature development workflow

```
  Research ──── Plan ──── Implement ──── Test ──── Review
     │           │            │           │          │
  researcher  planner    implementer  implementer  reviewer
```

**Concrete example — New API endpoint:**

| Stage | Agent Type | Task | Gate |
|-------|-----------|------|------|
| 1. Research | researcher | Find existing patterns, identify affected files | Output: file list + pattern notes |
| 2. Plan | mission-planner | Design endpoint spec, define acceptance criteria | Output: spec document |
| 3. Implement | implementer | Write handler, service, tests following spec | Output: code changes |
| 4. Test | implementer | Run test suite, fix failures | Gate: all tests pass |
| 5. Review | reviewer | Validate against acceptance criteria | Gate: PASS verdict |

**Key considerations:**
- Each stage must produce a well-defined artifact for the next stage.
- Insert quality gates (test pass, review approval) to prevent wasted downstream work.
- Slowest stage determines total mission time. Consider splitting large stages.

---

## 3. Explore-Then-Act

Deep read-only exploration before any modifications. The exploration phase informs the action plan.

**When to use:**
- Unfamiliar codebase or module
- Risk of breaking existing functionality
- Need to understand before changing
- Complex refactoring where wrong approach is costly

```
  ┌─── Explore A ───┐                ┌─── Act X ───┐
  │                  │                │              │
  ├─── Explore B ───┤── Synthesize ──├─── Act Y ───┤── Verify
  │                  │    & Plan      │              │
  └─── Explore C ───┘                └─── Act Z ───┘
      READ-ONLY          PLAN           READ-WRITE      REVIEW
```

**Concrete example — Migrate state management library:**

| Phase | Agent Type | Task |
|-------|-----------|------|
| Explore (parallel) | researcher (x3) | A: map all Zustand store usage. B: identify component dependencies on stores. C: find test mocks for stores. |
| Plan | mission-planner | Design migration order, identify breaking changes, create task cards. |
| Act (sequential) | implementer (x3) | X: migrate core store. Y: update dependent components. Z: update test mocks. |
| Verify | reviewer | Run full test suite, review all changes against migration plan. |

**Key considerations:**
- Exploration agents must be read-only (`disallowedTools: Edit, Write`).
- Exploration output should include exact file paths and line numbers.
- The plan phase is the critical bridge: bad exploration leads to bad plans.

---

## 4. Competitive

Multiple agents attempt the same task with different approaches. A judge selects the best result.

**When to use:**
- Optimal approach is unclear
- Multiple valid solutions exist
- Quality matters more than speed or cost
- Algorithm design, architecture decisions, performance optimization

```
  ┌─── Approach A ───┐
  │                   │
  ├─── Approach B ───┼──── Judge ──── Winner
  │                   │
  └─── Approach C ───┘
      PARALLEL             SELECT
```

**Concrete example — Performance optimization:**

| Step | Agent Type | Task |
|------|-----------|------|
| Compete (parallel) | implementer (x3) | A: optimize via memoization. B: optimize via lazy loading. C: optimize via virtual scrolling. |
| Judge | reviewer | Benchmark all three, evaluate code complexity, select best approach. |

**Key considerations:**
- Each competitor must work in a separate worktree (`isolation: worktree`).
- The judge needs clear criteria defined upfront (performance target, complexity budget).
- Expensive: N times the implementation cost. Reserve for high-value decisions.
- Non-winning worktrees should be cleaned up.

---

## 5. Iterative Refinement

Implement, review, fix in a loop until quality criteria are met or max iterations reached.

**When to use:**
- Implementation likely needs multiple passes
- Tight acceptance criteria
- Test-driven development workflow
- Polishing user-facing output

```
  Implement ──── Review ──── Fix ──── Review ──── Done
      │             │          │          │
  implementer   reviewer  implementer  reviewer
                   │                      │
              FAIL: specific         PASS: ship it
              fix instructions
```

**Concrete example — Complex UI component:**

| Iteration | Agent Type | Task | Exit Condition |
|-----------|-----------|------|----------------|
| 1. Implement | implementer | Build component following design spec | Code compiles, basic tests pass |
| 1. Review | reviewer | Check against acceptance criteria, visual spec | PASS or FAIL with fix list |
| 2. Fix | implementer | Address review findings | All fixes applied |
| 2. Review | reviewer | Re-verify fixes, run full test suite | PASS or FAIL |
| Max iterations: 3 | | Escalate to human if still failing | |

**Key considerations:**
- Set a maximum iteration count (2-3) to prevent infinite loops.
- Each review must produce specific, actionable fix instructions.
- The reviewer must NOT be the implementer (independent verification).
- If max iterations reached without PASS, escalate rather than continuing.

---

## 6. Supervisor with Workers

A persistent supervisor agent delegates tasks to worker agents, monitors progress, and adjusts the plan dynamically.

**When to use:**
- Large mission with many tasks
- Tasks may need re-planning based on intermediate results
- Dynamic coordination needed (e.g., worker finds something unexpected)
- Cross-cutting concerns require a coordinator

```
                 ┌─── Worker A (research)
                 │
  Supervisor ────┼─── Worker B (implement)
       │         │
       │         └─── Worker C (implement)
       │
  monitors, re-plans, dispatches next wave
```

**Concrete example — Full-stack feature with unknowns:**

| Step | Agent | Task |
|------|-------|------|
| Wave 1 | researcher | Explore database schema and existing API patterns |
| Decision | supervisor | Review findings, decide on schema approach, create implementation tasks |
| Wave 2 (parallel) | implementer A, implementer B | A: backend API. B: database migration. |
| Decision | supervisor | Check for conflicts, adjust frontend tasks based on actual API shape |
| Wave 3 | implementer C | Frontend integration using actual API response format |
| Wave 4 | reviewer | End-to-end review |

**Key considerations:**
- The supervisor must maintain a mental model of mission state.
- Workers report structured results back (not free-form text).
- The supervisor can re-plan between waves based on actual outcomes.
- More expensive than static patterns due to supervisor overhead.

---

## 7. Adaptive Retry

When a task fails, retry with escalated resources: stronger model, more context, or split into simpler subtasks.

**When to use:**
- Tasks with uncertain complexity
- Cost-sensitive missions (start cheap, escalate only on failure)
- Fault-tolerant workflows where some failures are expected
- Large batch operations where a few tasks may be harder than anticipated

```
  Task ──── haiku ──── FAIL ──── sonnet ──── FAIL ──── opus
                                                         │
                                              FAIL ──── Split into
                                                        subtasks
                                                           │
                                              ┌─ Subtask A (sonnet)
                                              └─ Subtask B (sonnet)
```

**Escalation ladder:**

| Attempt | Model | Strategy | Budget Multiplier |
|---------|-------|----------|-------------------|
| 1 | haiku | Original task, minimal context | 1x |
| 2 | sonnet | Same task, add error context from attempt 1 | 3x |
| 3 | opus | Same task, add error context from attempts 1-2 | 10x |
| 4 | Split | Decompose into 2-3 simpler subtasks, retry with sonnet | 6-9x |

**Concrete example — Batch file migration:**

| Step | Model | Task | Outcome |
|------|-------|------|---------|
| Attempt 1 | haiku | Migrate `auth.ts` from CommonJS to ESM | FAIL: complex re-exports |
| Attempt 2 | sonnet | Same task + error log from attempt 1 | FAIL: circular dependency |
| Attempt 3 | opus | Same task + both error logs | PASS |
| (alternate) | Split | Split into: (A) resolve circular dep, (B) migrate to ESM | Both PASS with sonnet |

**Key considerations:**
- Always include failure context from previous attempts in the retry prompt.
- Set `maxRetries` per task (default: 2, meaning 3 total attempts).
- Track cumulative cost: if retries exceed 3x original budget, consider human escalation.
- Splitting is preferred over opus escalation when the task has clear sub-components.
- Log all retry attempts for retrospective learning.

---

## Pattern Selection Guide

```
Is the work embarrassingly parallel (no dependencies between tasks)?
  └─ YES → Fan-Out / Fan-In
  └─ NO ↓

Are there clear sequential phases?
  └─ YES → Pipeline
  └─ NO ↓

Is the codebase unfamiliar or the change risky?
  └─ YES → Explore-Then-Act
  └─ NO ↓

Are there multiple valid approaches and quality matters most?
  └─ YES → Competitive
  └─ NO ↓

Will the implementation likely need multiple review passes?
  └─ YES → Iterative Refinement
  └─ NO ↓

Is the mission large with dynamic coordination needs?
  └─ YES → Supervisor with Workers
  └─ NO ↓

Are you optimizing cost and some tasks may fail?
  └─ YES → Adaptive Retry
  └─ NO → Pipeline (safe default)
```

## Combining Patterns

Patterns are composable. Common combinations:

- **Explore-Then-Act + Pipeline**: Explore phase, then pipeline the implementation.
- **Fan-Out + Iterative Refinement**: Parallel implementation, then iterative review on each.
- **Supervisor + Adaptive Retry**: Supervisor dispatches workers; failed workers get retried with escalation.
- **Pipeline + Competitive**: One stage uses competitive approach (e.g., compete on algorithm, then pipeline the rest).

Always document which pattern(s) you selected and why in the mission scope.
