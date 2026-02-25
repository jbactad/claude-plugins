# Playbook File Format

Playbooks are markdown files with YAML frontmatter. They define reusable mission templates that the orchestrator uses as the skeleton for task decomposition.

## File Location

```
.claude/missions/playbooks/{name}.md
```

The file name (without `.md`) is the playbook name used in commands:

```
/playbook use full-stack-feature    # loads .claude/missions/playbooks/full-stack-feature.md
```

## YAML Frontmatter Schema

```yaml
---
name: <string>                    # Required. Unique playbook identifier. Must match the filename.
description: <string>             # Required. One-line description shown in `/playbook list`.
planningDepth: <lite|spec|full>   # Required. How deeply the mission planner should plan.
                                  #   lite  — Minimal planning. Suitable for well-understood, low-risk tasks.
                                  #   spec  — Produce a specification before implementation. Good default.
                                  #   full  — Detailed planning with dependency graphs, rollback points,
                                  #           and file ownership. Use for risky or large-scope missions.
requireApproval: <boolean>        # Optional. Default: false. If true, the orchestrator pauses after
                                  #   planning and waits for human approval before executing.
riskTier: <0|1|2>                 # Required. Default risk tier for tasks in this playbook.
                                  #   0 — Low risk. No reviewer needed.
                                  #   1 — Medium risk. Reviewer required.
                                  #   2 — High risk. Reviewer required, consider opus model.
defaultModel: <string>            # Optional. Default: "sonnet". The model to use for agents unless
                                  #   overridden at the phase or task level. Values: haiku, sonnet, opus.
useWorktrees: <boolean>           # Optional. Default: false. If true, implementation agents work in
                                  #   isolated git worktrees.
---
```

## Body Format

The body is standard markdown. It must contain a `## Phases` section with one or more `### Phase N: <Name>` subsections.

### Overall Structure

```markdown
## Phases

### Phase 1: <Phase Name>
- **Agents**: <agent-type> (x<count>)
- **Parallel**: <true|false>
- **Depends On**: <none | Phase N, Phase M>
- **Model**: <haiku|sonnet|opus>          (optional, overrides defaultModel)
- **Isolation**: <none|worktree>          (optional, overrides useWorktrees)

#### Tasks
1. <Task description for this phase. Use {goal} to reference the mission goal.>
2. <Another task if the phase has multiple sub-tasks.>

#### Notes
<Any additional context, constraints, or guidance for agents in this phase.>

### Phase 2: <Phase Name>
...

## Success Criteria

1. <Criterion 1>
2. <Criterion 2>
3. <Criterion 3>
```

### Phase Fields

| Field | Required | Description |
|-------|----------|-------------|
| Agents | Yes | Agent type and count. Format: `<type>` or `<type> (x<N>)` for multiple agents. Valid types: `researcher`, `mission-planner`, `implementer`, `reviewer`, `retrospective`, or custom types from `.claude/mission-control.local.md`. |
| Parallel | Yes | Whether agents within this phase run in parallel (`true`) or sequentially (`false`). |
| Depends On | Yes | Phase dependencies. Use `none` for phases with no dependencies. Reference phases by name: `Phase 1`, `Phase 2`, etc. Multiple dependencies: `Phase 1, Phase 2`. |
| Model | No | Override the playbook's `defaultModel` for this phase. Useful when a specific phase needs a stronger or weaker model. |
| Isolation | No | Override the playbook's `useWorktrees` for this phase. Use `worktree` for isolated execution, `none` for shared workspace. |

### Variable Substitution

The placeholder `{goal}` is replaced with the mission goal text at runtime. Use it in task descriptions to make playbooks generic:

```markdown
#### Tasks
1. Research existing patterns related to {goal} in the codebase.
2. Identify all files that will need modification for {goal}.
```

## Rules

1. **Phase names must be unique.** No two phases can share the same name within a playbook.
2. **`depends_on` must reference existing phase names.** Referencing a non-existent phase causes a validation error.
3. **At least 2 phases are required.** A single-phase playbook provides no value over a direct task assignment.
4. **No circular dependencies.** Phase A cannot depend on Phase B if Phase B depends on Phase A (directly or transitively).
5. **Parallel phases cannot have internal ordering.** If a phase has `Parallel: true` and multiple agents, all agents start simultaneously. Use separate phases if ordering matters.
6. **File names must match the `name` field.** The file `my-playbook.md` must have `name: my-playbook` in its frontmatter.

## Complete Example: Custom Playbook

Below is a complete custom playbook for an API-first development workflow:

```markdown
---
name: api-first
description: Design and implement API endpoints with contract-first development.
planningDepth: spec
requireApproval: false
riskTier: 1
defaultModel: sonnet
useWorktrees: true
---

## Phases

### Phase 1: API Design
- **Agents**: researcher
- **Parallel**: false
- **Depends On**: none
- **Model**: haiku

#### Tasks
1. Research existing API patterns in the codebase: URL conventions, request/response shapes, error formats, authentication middleware.
2. Identify the router file, controller directory, and service layer structure.

#### Notes
This phase is read-only. The researcher must not suggest changes, only report facts about existing conventions.

### Phase 2: Contract
- **Agents**: mission-planner
- **Parallel**: false
- **Depends On**: Phase 1

#### Tasks
1. Design the API contract for {goal}: endpoints, HTTP methods, request schemas, response schemas, error codes.
2. Define acceptance criteria for each endpoint including edge cases.
3. Produce task cards for implementation.

### Phase 3: Implement
- **Agents**: implementer
- **Parallel**: false
- **Depends On**: Phase 2
- **Isolation**: worktree

#### Tasks
1. Implement route handlers following the contract from Phase 2.
2. Implement service layer logic.
3. Write request validation using the project's validation library.
4. Write unit tests for each endpoint.

### Phase 4: Integration Test
- **Agents**: implementer
- **Parallel**: false
- **Depends On**: Phase 3

#### Tasks
1. Write integration tests that exercise the full request-response cycle.
2. Run the full test suite and fix any failures.

### Phase 5: Review
- **Agents**: reviewer
- **Parallel**: false
- **Depends On**: Phase 4

#### Tasks
1. Validate all endpoints match the contract from Phase 2.
2. Check error handling, input validation, and edge cases.
3. Verify test coverage is sufficient.

## Success Criteria

1. All API endpoints match the contract defined in Phase 2.
2. Unit and integration tests pass.
3. Full existing test suite passes with no regressions.
4. Reviewer issues a PASS verdict.
```
