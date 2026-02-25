---
name: playbook
description: List, create, or execute mission playbooks. Playbooks are reusable mission templates.
disable-model-invocation: true
argument-hint: "[list|create|use] [playbook-name]"
---

# Playbook Manager

Manage mission playbooks -- reusable templates that define phased execution plans for common mission types. Playbooks pre-configure the task decomposition, agent assignments, and settings so missions of a known type can start faster with proven structures.

## Argument Parsing

Parse `$ARGUMENTS` to determine the action:

- **No arguments or `list`**: List all available playbooks.
- **`create [name]`**: Guide the user through creating a custom playbook.
- **`use [name]`**: Load a playbook and launch a mission with it.
- **Anything else**: Treat as a playbook name and attempt `use`.

If `$ARGUMENTS` does not match any of the above patterns, ask the user:

```
AskUserQuestion:
  question: "What would you like to do with playbooks?"
  options:
    - "List available playbooks"
    - "Create a new playbook"
    - "Use an existing playbook"
```

---

## Action: list

### `/playbook list` (or `/playbook` with no arguments)

List all available playbooks, organized by source.

#### Built-in Playbooks

Display these built-in playbooks. These are always available regardless of project configuration.

| Name | Description | Phases |
|------|-------------|--------|
| `full-stack-feature` | End-to-end feature implementation with research, planning, backend, frontend, testing, and review. | 6 phases: Research, Plan, Implement Backend, Implement Frontend, Test, Review |
| `bug-investigation` | Systematic bug diagnosis from reproduction through root cause analysis to fix and regression testing. | 5 phases: Reproduce, Trace, Root Cause, Fix, Regression Test |
| `refactoring` | Safe codebase restructuring with audit, incremental migration, and regression verification at each step. | 4 phases: Audit, Plan, Migrate File-by-File, Verify |
| `security-audit` | Comprehensive security review covering dependencies, authentication, input validation, and data handling. | 5 phases: Scan Dependencies, Review Auth, Review Input Validation, Review Data Handling, Report |
| `migration` | Incremental technology or architecture migration with assessment, planning, stepwise execution, and cleanup. | 5 phases: Assess Scope, Create Plan, Execute Incrementally, Verify Each Step, Cleanup |

#### Project Playbooks

Check `.mission-control/playbooks/` for any `.md` files. For each file found:

1. Parse the YAML frontmatter to extract `name`, `description`, `planningDepth`, and `riskTier`.
2. Count the number of `### Phase` headings in the markdown body to determine the phase count.
3. Display in a table with the same format as built-in playbooks.

If no project playbooks exist, display: "No project playbooks found. Use `/playbook create [name]` to create one."

#### Output Format

```
AVAILABLE PLAYBOOKS
───────────────────

Built-in:
  full-stack-feature     End-to-end feature implementation               6 phases
  bug-investigation      Systematic bug diagnosis and fix                5 phases
  refactoring            Safe codebase restructuring                     4 phases
  security-audit         Comprehensive security review                   5 phases
  migration              Incremental technology migration                5 phases

Project (.mission-control/playbooks/):
  [name]                 [description]                                   [N] phases
  [name]                 [description]                                   [N] phases

Use "/playbook use [name]" to execute a playbook.
Use "/playbook create [name]" to create a custom playbook.
```

---

## Action: create

### `/playbook create [name]`

Guide the user through creating a custom playbook interactively.

#### Step 1: Name and Description

If `[name]` was provided in the arguments, use it. Otherwise ask:

```
AskUserQuestion:
  question: "What should this playbook be called? (lowercase, hyphens, e.g., 'api-endpoint', 'database-migration')"
```

Then ask for the description:

```
AskUserQuestion:
  question: "Describe when this playbook should be used (one sentence):"
```

#### Step 2: Define Phases

Ask the user to define the phases of the playbook. Each phase represents a stage of the mission.

```
AskUserQuestion:
  question: "Define the phases for this playbook. Common patterns:
    - Research, Plan, Implement, Test, Review
    - Investigate, Design, Build, Verify
    - Audit, Migrate, Validate, Cleanup

    Enter your phases (comma-separated):"
```

Parse the comma-separated list into individual phase names.

#### Step 3: Agent Assignments

For each phase, ask which agent type should handle it:

```
AskUserQuestion:
  question: "Which agent should handle the '[phase-name]' phase?"
  options:
    - "researcher — Read-only exploration and analysis"
    - "mission-planner — Goal decomposition and planning"
    - "implementer — Code writing and file creation"
    - "reviewer — Quality assurance and validation"
    - "retrospective — Learning extraction"
    - "Custom agent (defined in project settings)"
```

If the user selects "Custom agent", ask them to specify the custom agent type name.

#### Step 4: Phase Dependencies

For each phase after the first, ask about dependencies:

```
AskUserQuestion:
  question: "Which phases must complete before '[phase-name]' can start?"
  options:
    - "[list of previous phases]"
    - "All previous phases"
    - "None (can run in parallel with others)"
```

#### Step 5: Default Settings

Ask about playbook-level default settings:

```
AskUserQuestion:
  question: "Configure default settings for this playbook:"

Planning depth:
  options:
    - "skip — No planning, jump straight to execution"
    - "lite — Quick task decomposition"
    - "spec — Standard planning with acceptance criteria (recommended)"
    - "full — Comprehensive planning with architecture review"

Risk tier:
  options:
    - "Tier 0 — Low risk, no reviewer needed"
    - "Tier 1 — Medium risk, reviewer required"
    - "Tier 2 — High risk, reviewer + approval required"

Approval:
  options:
    - "never — Fully autonomous"
    - "tier1+ — Approve Tier 1 and above"
    - "tier2+ — Approve Tier 2 only"
    - "always — Approve every task"
```

#### Step 6: Save Playbook

Create `.mission-control/playbooks/` directory if it does not exist.

Save the playbook to `.mission-control/playbooks/{name}.md` with the following format:

```markdown
---
name: [name]
description: [description]
planningDepth: [selected depth]
requireApproval: [selected approval level]
riskTier: [selected tier]
---

# [Name] Playbook

[description]

## Phases

### Phase 1: [Phase Name]
- agents: [[agent-type]]
- parallel: [true if no dependencies, false otherwise]
- tasks:
  - [General task description for this phase]

### Phase 2: [Phase Name]
- agents: [[agent-type]]
- depends_on: [[Phase N]]
- tasks:
  - [General task description for this phase]

[...repeat for each phase]

## Success Criteria
- All phase tasks completed successfully
- Review agent approves (if applicable)
- Tests pass (if testCommand configured)
```

Confirm to the user:

```
Playbook created: .mission-control/playbooks/[name].md

  Name: [name]
  Phases: [N] ([phase names])
  Planning: [depth]
  Risk: [tier]
  Approval: [level]

Use "/playbook use [name]" to execute this playbook.
```

---

## Action: use

### `/playbook use [name]`

Load the specified playbook and launch a mission with it.

#### Step 1: Find the Playbook

Search for the playbook by name:

1. Check built-in playbooks first. Match against: `full-stack-feature`, `bug-investigation`, `refactoring`, `security-audit`, `migration`.
2. Check `.mission-control/playbooks/{name}.md`.
3. If not found, check `.mission-control/playbooks/` for partial name matches.

If the playbook is not found, report:

```
Playbook "[name]" not found.
Use "/playbook list" to see available playbooks.
```

#### Step 2: Display Playbook

Display the playbook's phases, settings, and agent assignments:

```
PLAYBOOK: [name]
─────────────────
[description]

Settings:
  Planning: [planningDepth]
  Risk Tier: [riskTier]
  Approval: [requireApproval]

Phases:
  1. [Phase Name] — [agent-type] [parallel/sequential]
  2. [Phase Name] — [agent-type] [depends on Phase N]
  3. [Phase Name] — [agent-type] [depends on Phase N]
  ...

Success Criteria:
  - [criterion 1]
  - [criterion 2]
```

#### Step 3: Get Mission Goal

Ask the user for the mission goal:

```
AskUserQuestion:
  question: "What is the goal for this mission? The playbook '[name]' will structure the execution."
```

#### Step 4: Launch Mission

Invoke the `/mission` command with the playbook pre-selected. Pass:
- The mission goal from the user.
- The playbook name, so `/mission` skips playbook matching (Step 4 of the mission workflow) and uses this playbook directly.
- The playbook's default settings as mission-level overrides.

This is equivalent to `/mission [goal]` with the playbook already chosen. The mission workflow will use the playbook's phases as the task decomposition template.

Confirm:

```
Launching mission with playbook "[name]"...
```

The `/mission` workflow takes over from here.

---

## Built-in Playbook Definitions

These are the detailed phase structures for built-in playbooks. When `/playbook use` loads a built-in, these definitions are used.

### full-stack-feature

```
Phase 1: Research
  agents: [researcher]
  parallel: true
  tasks:
    - Explore existing patterns related to the feature
    - Identify affected files and modules
    - Check for potential conflicts with existing code

Phase 2: Plan
  agents: [mission-planner]
  depends_on: [Phase 1]
  tasks:
    - Design implementation approach based on research
    - Define detailed acceptance criteria
    - Assign file ownership across implementation tasks

Phase 3: Implement Backend
  agents: [implementer]
  depends_on: [Phase 2]
  isolation: worktree
  tasks:
    - Implement server-side logic, routes, services
    - Write unit tests for backend changes

Phase 4: Implement Frontend
  agents: [implementer]
  depends_on: [Phase 2]
  isolation: worktree
  tasks:
    - Implement UI components, state, and routing
    - Write component tests

Phase 5: Test
  agents: [implementer]
  depends_on: [Phase 3, Phase 4]
  tasks:
    - Run full test suite
    - Fix any integration issues
    - Write integration/E2E tests if needed

Phase 6: Review
  agents: [reviewer]
  depends_on: [Phase 5]
  tasks:
    - Review all changes against acceptance criteria
    - Check for security issues, edge cases, and regressions
    - Produce final verdict
```

### bug-investigation

```
Phase 1: Reproduce
  agents: [researcher]
  parallel: false
  tasks:
    - Locate the reported behavior in the codebase
    - Identify reproduction steps
    - Confirm the bug exists

Phase 2: Trace
  agents: [researcher]
  depends_on: [Phase 1]
  tasks:
    - Trace the code path that triggers the bug
    - Identify all related files and dependencies

Phase 3: Root Cause
  agents: [researcher]
  depends_on: [Phase 2]
  tasks:
    - Determine the root cause of the bug
    - Document why the current code produces incorrect behavior

Phase 4: Fix
  agents: [implementer]
  depends_on: [Phase 3]
  isolation: worktree
  tasks:
    - Implement the fix based on root cause analysis
    - Write a regression test that fails without the fix

Phase 5: Regression Test
  agents: [reviewer]
  depends_on: [Phase 4]
  tasks:
    - Run full test suite to verify no regressions
    - Review fix for correctness and completeness
```

### refactoring

```
Phase 1: Audit
  agents: [researcher]
  parallel: false
  tasks:
    - Catalog all instances of the pattern to refactor
    - Map dependencies between affected files
    - Identify high-risk areas

Phase 2: Plan
  agents: [mission-planner]
  depends_on: [Phase 1]
  tasks:
    - Define the target pattern
    - Order files for migration to minimize breakage
    - Define checkpoints for incremental verification

Phase 3: Migrate
  agents: [implementer]
  depends_on: [Phase 2]
  isolation: worktree
  tasks:
    - Migrate files one-by-one or in small batches
    - Run tests after each batch
    - Fix any breakage before proceeding

Phase 4: Verify
  agents: [reviewer]
  depends_on: [Phase 3]
  tasks:
    - Verify all instances have been migrated
    - Run full test suite
    - Check for leftover references to the old pattern
```

### security-audit

```
Phase 1: Scan Dependencies
  agents: [researcher]
  parallel: true
  tasks:
    - Check for known vulnerabilities in dependencies
    - Review dependency versions and update status
    - Identify dependencies with excessive permissions

Phase 2: Review Auth
  agents: [researcher]
  parallel: true
  tasks:
    - Review authentication implementation
    - Check session management and token handling
    - Verify authorization checks on protected routes

Phase 3: Review Input Validation
  agents: [researcher]
  depends_on: [Phase 1]
  tasks:
    - Check all user input entry points
    - Verify sanitization and validation patterns
    - Look for injection vulnerabilities (SQL, XSS, command)

Phase 4: Review Data Handling
  agents: [researcher]
  depends_on: [Phase 2]
  tasks:
    - Check sensitive data storage and transmission
    - Review encryption usage
    - Verify secrets are not hardcoded or logged

Phase 5: Report
  agents: [reviewer]
  depends_on: [Phase 3, Phase 4]
  tasks:
    - Compile findings into a structured security report
    - Classify findings by severity (critical, high, medium, low)
    - Recommend remediation steps for each finding
```

### migration

```
Phase 1: Assess Scope
  agents: [researcher]
  parallel: false
  tasks:
    - Identify all code, configuration, and data affected
    - Assess compatibility between source and target
    - Estimate effort and risk

Phase 2: Create Plan
  agents: [mission-planner]
  depends_on: [Phase 1]
  tasks:
    - Define migration steps in dependency order
    - Identify rollback points
    - Plan verification for each step

Phase 3: Execute Incrementally
  agents: [implementer]
  depends_on: [Phase 2]
  isolation: worktree
  tasks:
    - Execute migration steps one at a time
    - Verify each step before proceeding
    - Maintain backward compatibility where possible

Phase 4: Verify Each Step
  agents: [reviewer]
  depends_on: [Phase 3]
  tasks:
    - Run test suite after each migration step
    - Verify functionality matches pre-migration behavior
    - Check for performance regressions

Phase 5: Cleanup
  agents: [implementer]
  depends_on: [Phase 4]
  tasks:
    - Remove old code, configuration, and compatibility shims
    - Update documentation
    - Run final verification
```
