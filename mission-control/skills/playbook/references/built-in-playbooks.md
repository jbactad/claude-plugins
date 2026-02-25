# Built-In Playbooks

Five playbooks ship with mission-control. Each defines a complete phase structure, agent assignments, default settings, and success criteria for a common mission type.

---

## 1. full-stack-feature

**Description:** For adding new features that span frontend and backend layers. Fans out research in parallel, then pipelines through backend implementation, frontend implementation, testing, and review.

**When to use:**
- The feature touches both API/backend and UI/frontend code.
- Multiple areas of the codebase need exploration before implementation.
- The feature is well-defined enough to implement in a single mission.

### Phases

| Phase | Name | Agents | Parallel? | Depends On | Description |
|-------|------|--------|-----------|------------|-------------|
| 1 | Research | 2-4 researcher | Yes (fan-out) | none | Explore existing patterns, routing conventions, data models, and UI component library. Each researcher owns a distinct area: API patterns, data layer, frontend components, test patterns. |
| 2 | Plan | 1 mission-planner | No | Phase 1 | Design the implementation approach. Produce task cards for backend and frontend work with file ownership, acceptance criteria, and dependency ordering. |
| 3 | Implement Backend | 1 implementer | No | Phase 2 | Create API endpoints, data models, services, and backend tests. |
| 4 | Implement Frontend | 1 implementer | No | Phase 3 | Create UI components, routes, state management, and frontend tests. Consumes the actual API shape from Phase 3. |
| 5 | Test | 1 implementer | No | Phase 4 | Run the full test suite. Fix any failures introduced by the new feature. |
| 6 | Review | 1 reviewer | No | Phase 5 | Validate all changes against the acceptance criteria from Phase 2. Check for missed edge cases, convention violations, and test coverage gaps. |

### Default Settings

| Setting | Value |
|---------|-------|
| planningDepth | spec |
| riskTier | 1 |
| useWorktrees | true |
| defaultModel | sonnet (researchers use haiku) |
| maxConcurrentAgents | 4 |

### Success Criteria

- All acceptance criteria from Phase 2 are met.
- Backend and frontend tests pass.
- Full existing test suite passes with no regressions.
- Reviewer issues a PASS verdict.

---

## 2. bug-investigation

**Description:** For diagnosing and fixing bugs. Follows a systematic approach: reproduce, trace to root cause, fix, write regression test, review.

**When to use:**
- A bug has been reported with symptoms but the root cause is unknown.
- The fix needs a regression test to prevent recurrence.
- The investigation may touch multiple modules to trace the code path.

### Phases

| Phase | Name | Agents | Parallel? | Depends On | Description |
|-------|------|--------|-----------|------------|-------------|
| 1 | Reproduce | 1 researcher | No | none | Find exact reproduction steps. Identify the symptom, the expected behavior, and the input conditions that trigger the bug. Document the affected code path entry point. |
| 2 | Trace | 1 researcher | No | Phase 1 | Trace the code path from the symptom back to the root cause. Follow the execution flow through relevant files, identify where the behavior diverges from the expected path. Document the root cause with file paths and line numbers. |
| 3 | Fix | 1 implementer | No | Phase 2 | Apply the minimal fix that addresses the root cause. Follow existing patterns. Do not refactor adjacent code. |
| 4 | Regression Test | 1 implementer | No | Phase 3 | Write a regression test that reproduces the original bug (fails without the fix, passes with it). Follow existing test conventions. |
| 5 | Review | 1 reviewer | No | Phase 4 | Validate that the fix addresses the root cause identified in Phase 2. Verify the regression test is meaningful. Check that the fix does not introduce new regressions. |

### Default Settings

| Setting | Value |
|---------|-------|
| planningDepth | lite |
| riskTier | 1 |
| useWorktrees | true |
| defaultModel | sonnet |
| maxConcurrentAgents | 1 |

### Success Criteria

- Root cause is identified with specific file path and line number.
- Fix addresses the root cause, not just the symptom.
- Regression test fails without the fix and passes with it.
- Full existing test suite passes with no regressions.
- Reviewer issues a PASS verdict.

---

## 3. refactoring

**Description:** For restructuring code without changing external behavior. Audits current structure, plans an incremental migration path, applies changes file-by-file with verification after each change, then reviews.

**When to use:**
- Code needs restructuring but external behavior must not change.
- The refactoring spans multiple files.
- Changes must be incremental and verifiable at each step.
- Risk of breaking existing functionality is non-trivial.

### Phases

| Phase | Name | Agents | Parallel? | Depends On | Description |
|-------|------|--------|-----------|------------|-------------|
| 1 | Audit | 1 researcher | No | none | Map the current structure. Identify all files, functions, and dependencies involved. Catalog the issues that motivate the refactoring. Document the dependency graph. |
| 2 | Plan | 1 mission-planner | No | Phase 1 | Create an incremental migration plan. Each step must be independently verifiable (tests pass after each step). Order steps to minimize intermediate breakage. Define rollback points. |
| 3 | Migrate | 1 implementer | No (iterate) | Phase 2 | Apply changes file-by-file following the plan from Phase 2. Each file change is a discrete step. Do not batch unrelated changes together. |
| 4 | Verify | 1 implementer | No (after each file) | Phase 3 | Run the full test suite after each file migration. If tests fail, fix before proceeding to the next file. Do not accumulate failures. |
| 5 | Review | 1 reviewer | No | Phase 4 | Verify that no external behavior has changed. Check that the refactoring achieved its stated goals. Confirm all tests pass and no new test gaps exist. |

### Default Settings

| Setting | Value |
|---------|-------|
| planningDepth | full |
| riskTier | 1 |
| useWorktrees | true |
| defaultModel | sonnet |
| maxConcurrentAgents | 1 |

### Success Criteria

- All tests pass after each incremental migration step.
- External behavior is unchanged (no API changes, no output changes, no side effect changes).
- The refactoring goals stated in the audit are achieved.
- Reviewer issues a PASS verdict.

---

## 4. security-audit

**Description:** For reviewing the security posture of a project. Four parallel research phases examine different security domains, followed by a consolidated findings report.

**When to use:**
- A security review is needed before a release, after a vulnerability report, or as a periodic check.
- The review should cover dependencies, authentication, input validation, and data handling.
- Findings need to be compiled into a structured, actionable report.

### Phases

| Phase | Name | Agents | Parallel? | Depends On | Description |
|-------|------|--------|-----------|------------|-------------|
| 1 | Dependencies | 1 researcher | Yes (with Phases 2-4) | none | Scan for vulnerable dependencies. Check lock files, audit tools, known CVE databases. Identify outdated packages with known vulnerabilities. |
| 2 | Auth | 1 researcher | Yes (with Phases 1, 3-4) | none | Review authentication and authorization mechanisms. Check session management, token handling, permission checks, credential storage. |
| 3 | Input | 1 researcher | Yes (with Phases 1-2, 4) | none | Review input validation and sanitization. Check all user input entry points (API endpoints, form handlers, URL parameters). Look for injection vulnerabilities (SQL, XSS, command injection). |
| 4 | Data | 1 researcher | Yes (with Phases 1-3) | none | Review data handling and storage. Check encryption at rest and in transit, PII handling, logging of sensitive data, backup security. |
| 5 | Report | 1 reviewer | No | Phases 1-4 | Compile findings from all four research phases into a structured security report. Prioritize findings by severity (critical, high, medium, low). Include remediation recommendations. |

### Default Settings

| Setting | Value |
|---------|-------|
| planningDepth | spec |
| riskTier | 2 |
| useWorktrees | false |
| defaultModel | sonnet (all researchers use sonnet) |
| maxConcurrentAgents | 4 |

### Success Criteria

- All four security domains are covered with documented findings.
- Each finding includes severity, affected code location, and remediation recommendation.
- Critical and high severity findings are flagged for immediate attention.
- Report is structured and actionable.

---

## 5. migration

**Description:** For migrating between technologies, frameworks, or major versions. Assesses scope, plans with rollback points, executes incrementally with testing after each step, verifies, and cleans up old code.

**When to use:**
- Migrating from one library/framework to another (e.g., Redux to Zustand, Express 4 to Express 5).
- Upgrading a major version with breaking changes (e.g., React 18 to React 19, Node 18 to Node 22).
- Changing a fundamental technology (e.g., REST to GraphQL, JavaScript to TypeScript).

### Phases

| Phase | Name | Agents | Parallel? | Depends On | Description |
|-------|------|--------|-----------|------------|-------------|
| 1 | Assess | 1 researcher | No | none | Assess the full scope of the migration. Identify every affected file, every API surface that changes, every dependency that needs updating. Produce a complete inventory with file paths and change descriptions. |
| 2 | Plan | 1 mission-planner | No | Phase 1 | Create an incremental migration plan with explicit rollback points. Each step must leave the codebase in a working state. Define the order of operations, identify files that must change together (atomic groups), and set verification checkpoints. |
| 3 | Execute | 1 implementer | No (iterate) | Phase 2 | Migrate incrementally following the plan. After each step, run tests to confirm the codebase still works. If a step breaks tests, fix before proceeding. Document any deviations from the plan. |
| 4 | Verify | 1 implementer | No | Phase 3 | Run the full test suite. Perform manual verification of critical paths. Check that the old technology is fully replaced (no lingering references). Verify build, lint, and type checking all pass. |
| 5 | Cleanup | 1 implementer | No | Phase 4 | Remove old code, unused dependencies, deprecated configuration files. Update documentation to reflect the new technology. Remove migration-specific workarounds or shims. |

### Default Settings

| Setting | Value |
|---------|-------|
| planningDepth | full |
| riskTier | 2 |
| useWorktrees | true |
| defaultModel | sonnet |
| maxConcurrentAgents | 1 |
| requireApproval | true |

### Success Criteria

- All affected files are migrated with no lingering references to the old technology.
- Full test suite passes.
- Build, lint, and type checking all pass.
- Old dependencies, configuration files, and dead code are removed.
- Documentation is updated to reflect the new technology.
- No migration shims or temporary workarounds remain.
- Reviewer or human approver issues a PASS verdict.
