---
name: playbook-knowledge
description: >
  Knowledge about mission playbooks — reusable templates for common orchestration workflows.
  Use when the user asks about playbooks, wants to know available playbook types, or needs
  guidance on creating custom playbooks. Also use when deciding which playbook fits a mission.
user-invocable: false
---

# Playbook System

Playbooks are reusable mission templates stored as markdown files with YAML frontmatter. They pre-define the phases, agent assignments, default settings, and success criteria for common mission types. Instead of planning from scratch every time, you select a playbook that matches the mission's shape, and the orchestrator uses it as the skeleton for task decomposition.

## Why Playbooks Exist

- **Consistency.** The same type of mission gets the same proven structure every time. No variance from one run to the next.
- **Speed.** Skip the planning phase for well-understood mission types. The playbook already encodes the right phase ordering, agent types, and model choices.
- **Best practices.** Playbooks encode lessons learned from past missions: which phases to parallelize, where to insert quality gates, when to use worktrees, and which risk tiers to assign.
- **Customizability.** Teams can create project-specific playbooks that encode their own conventions, preferred agent configurations, and domain-specific workflows.

## Built-In Playbooks

Five playbooks ship with mission-control:

1. **full-stack-feature** -- For adding new features that span frontend and backend. Research phase fans out in parallel, followed by sequential backend and frontend implementation with testing and review.
2. **bug-investigation** -- For diagnosing and fixing bugs. Starts with reproduction, traces to root cause, applies a fix, writes regression tests, and reviews.
3. **refactoring** -- For restructuring code without changing behavior. Audits current structure, plans incremental migration, applies changes file-by-file with verification after each, then reviews.
4. **security-audit** -- For reviewing security posture. Four parallel research phases (dependencies, auth, input validation, data handling) followed by a consolidated report.
5. **migration** -- For migrating between technologies or versions. Assesses scope, plans with rollback points, executes incrementally, verifies, and cleans up.

See `references/built-in-playbooks.md` for full definitions of each playbook including phase tables, default settings, and success criteria.

## Usage

### List available playbooks

```
/playbook list
```

Lists all built-in playbooks and any project-specific playbooks found in `.claude/missions/playbooks/`.

### Apply a playbook to the current mission

```
/playbook use [name]
```

Loads the named playbook and applies its phases to the current mission. The playbook's phases become the task decomposition structure -- the mission planner uses them as the skeleton rather than planning from scratch.

### Create a custom playbook

```
/playbook create [name]
```

Scaffolds a new playbook file in `.claude/missions/playbooks/` with the required YAML frontmatter and phase structure. You then edit it to define your custom workflow.

## Project Playbooks Location

Custom playbooks are stored in the project directory:

```
.claude/missions/playbooks/
├── full-stack-feature.md    (built-in, copied on first use)
├── bug-investigation.md     (built-in, copied on first use)
├── refactoring.md           (built-in, copied on first use)
├── security-audit.md        (built-in, copied on first use)
├── migration.md             (built-in, copied on first use)
└── my-custom-playbook.md    (user-created)
```

Project playbooks override built-in playbooks of the same name. If you want to customize the `full-stack-feature` playbook for your project, copy it to `.claude/missions/playbooks/full-stack-feature.md` and modify it.

## Integration with Orchestration

When the orchestrator runs Step 3 (task decomposition), it checks whether a playbook is active:

1. **With a playbook**: The playbook's phases become the task decomposition skeleton. The mission planner fills in task-specific details (file ownership, acceptance criteria, exact prompts) but follows the phase ordering, agent assignments, and parallelism rules defined in the playbook.
2. **Without a playbook**: The mission planner decomposes the goal from scratch, choosing its own phase structure, agent types, and parallelism strategy based on the orchestration patterns in `references/orchestration-patterns.md`.

Playbooks and orchestration patterns are complementary. A playbook pre-selects which orchestration pattern to use (e.g., `full-stack-feature` uses a Pipeline pattern, `security-audit` uses Fan-Out/Fan-In), while orchestration patterns are the lower-level building blocks that the planner can combine freely when no playbook is active.

## References

- `references/built-in-playbooks.md` -- Full definitions of all five built-in playbooks.
- `references/playbook-schema.md` -- File format specification for creating custom playbooks.
