# mission-control

Autonomous AI orchestration engine for Claude Code.

Mission Control takes high-level goals, decomposes them into task dependency graphs, executes tasks with specialized agents in isolated git worktrees, learns from outcomes, and delivers results with minimal human intervention. It brings multi-agent coordination to Claude Code through a structured 7-step operational workflow with risk-gated autonomy, adaptive execution, and persistent memory.

## Features

- **7-step operational workflow**: Scope, risk assess, decompose, pattern select, launch, monitor, close
- **5 specialized agents**: mission-planner, researcher, implementer, reviewer, retrospective
- **4 slash commands**: `/mission`, `/checkpoint`, `/debrief`, `/playbook`
- **Playbooks**: Reusable mission templates for common workflows (full-stack feature, bug investigation, refactoring, security audit, migration)
- **Mission memory**: Cross-session learnings extracted from completed missions, automatically applied to future work
- **Adaptive execution**: Model escalation on failure (haiku to sonnet to opus), automatic task splitting, mid-mission replanning
- **4-level customization**: Organization, project, mission, and task-level settings with cascading overrides

## Quick Start

Install the plugin:

```bash
claude plugin add jbactad/claude-plugins/mission-control
```

Launch your first mission:

```
/mission Add user authentication with JWT tokens and session management
```

Mission Control will scope the work, assess risk, decompose it into tasks, assign specialized agents, and begin execution -- prompting for approval only when risk warrants it.

## Commands

| Command | Description |
|---------|-------------|
| `/mission [goal]` | Launch a new mission. Loads settings, matches playbooks, begins orchestration. If no goal is provided, prompts interactively. |
| `/checkpoint` | Produce a status report for the active mission. Shows progress, blockers, budget, and a CONTINUE / RESCOPE / STOP recommendation. |
| `/debrief` | Close the active mission. Spawns a retrospective agent to extract learnings, archives mission state, and presents a completion summary. |
| `/playbook [list\|create\|use] [name]` | List available playbooks, create a new one, or launch a mission from a playbook template. |

## Agents

| Agent | Description |
|-------|-------------|
| `mission-planner` | Decomposes high-level goals into task dependency graphs with risk tiers, agent assignments, file ownership, and parallel grouping. |
| `researcher` | Read-only codebase exploration and analysis. Finds patterns, maps dependencies, answers questions. Never modifies files. |
| `implementer` | Writes production-quality code from detailed task specifications. Runs in isolated git worktrees. Follows existing patterns. |
| `reviewer` | Independent quality assurance. Validates against acceptance criteria, checks for bugs, security issues, and architectural violations. Produces pass/fail verdict. |
| `retrospective` | Post-mission learning extraction. Analyzes outcomes, identifies patterns and anti-patterns, produces structured learnings for mission memory. |

## Skills

| Skill | Description |
|-------|-------------|
| `orchestrate` | Core 7-step workflow for coordinating multiple agents through a structured mission. Auto-invoked when Claude detects multi-agent work is needed. |
| `playbook-knowledge` | Knowledge about creating and using mission playbooks. Referenced by the `/playbook` command. |
| `mission-memory-knowledge` | Knowledge about the mission memory system -- how learnings are extracted, scored, stored, and applied. |

## Configuration

Create `.claude/mission-control.local.md` in your project root to customize Mission Control for your project. This file supports YAML frontmatter for settings and a markdown body for custom agent type definitions.

```yaml
---
defaultModel: sonnet
defaultPlanningDepth: spec
requireApproval: tier2+
maxConcurrentAgents: 3
testCommand: "npm test"
useWorktrees: true
autoReview: true
autoTest: true
retryOnFailure: true
maxRetries: 2
escalateModelOnRetry: true
memoryEnabled: true
autoLearn: true
---

## Custom Agent Types

| Type | Description | subagent_type | model | Notes |
|------|-------------|---------------|-------|-------|
| `frontend-expert` | React/TypeScript UI specialist | general-purpose | sonnet | Components and styling |
| `backend-expert` | Node/Express API specialist | general-purpose | sonnet | Endpoints and services |
```

See `examples/project-settings-example.md` for a complete settings reference with example configurations, and `examples/project-agents-example.md` for custom agent type templates.

## Customization Hierarchy

Settings cascade through four levels. Each level overrides the one above it:

```
Organization defaults  (~/.claude/mission-control.local.md)
    |
    v  overridden by
Project settings       (.claude/mission-control.local.md)
    |
    v  overridden by
Mission overrides      (per-mission flags at launch time)
    |
    v  overridden by
Task overrides         (per-task flags during decomposition)
```

## Playbooks

Playbooks are reusable mission templates that pre-configure the task decomposition for common workflows. When you launch a mission, Mission Control checks for matching playbooks and offers to use one.

### Built-in Playbooks

- **full-stack-feature** -- Research, plan, implement backend, implement frontend, test, review
- **bug-investigation** -- Reproduce, trace, root cause, fix, regression test
- **refactoring** -- Audit, plan, migrate file-by-file, verify no regressions
- **security-audit** -- Scan dependencies, review auth, review input validation, review data handling, report
- **migration** -- Assess scope, create migration plan, execute incrementally, verify each step, cleanup

### Custom Playbooks

Create project-specific playbooks in `.claude/missions/playbooks/`. Each playbook is a markdown file with YAML frontmatter defining phases, agent assignments, and success criteria. Use `/playbook create` for guided creation.

## Memory

Mission Control learns from completed missions. During `/debrief`, the retrospective agent extracts structured learnings and saves them to `.claude/mission-memory/`. These learnings are automatically loaded at the start of future missions when their tags match the mission goal.

Learning categories:

- **pattern** -- Reusable implementation patterns discovered in the codebase
- **gotcha** -- Mistakes to avoid (always loaded regardless of tag match)
- **architecture** -- Architectural decisions and constraints
- **tooling** -- Build, test, and deploy patterns
- **prompt** -- Effective prompt templates for agents

## Risk Tiers

Mission Control uses a 4-tier risk system to control autonomy:

| Tier | Level | Controls |
|------|-------|----------|
| Tier 0 | Low | Basic validation. Docs, config, simple renames. No reviewer needed. |
| Tier 1 | Medium | Independent reviewer required. New features, refactors within one module. |
| Tier 2 | High | Reviewer + go/no-go checkpoint. Cross-module changes, API modifications, security code. |
| Tier 3 | Critical | Human confirmation required. Irreversible actions, regulated systems, safety-sensitive. |

## Hooks

Mission Control uses lifecycle hooks for session continuity and observability:

- **SessionStart**: Detects active missions and injects status context
- **Stop**: Warns when stopping with incomplete tasks
- **PreToolUse[Task]**: Logs agent delegation events for retrospective analysis

## License

MIT
