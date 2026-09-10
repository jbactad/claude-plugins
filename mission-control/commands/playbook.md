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

Invoke the `playbook` skill and list the five built-ins from its `built-in-playbooks` reference — name, description, and phase count for each. They are always available regardless of project configuration. Do not hardcode the list here; the skill reference is the only definition.

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

If `[name]` was provided in the arguments, use it. Otherwise ask inline — these answers are free text, so do not use `AskUserQuestion`:

```
What should this playbook be called? (lowercase, hyphens, e.g. "api-endpoint", "database-migration")
```

Then ask for the description:

```
Describe when this playbook should be used (one sentence):
```

#### Step 2: Define Phases

Ask the user to define the phases of the playbook. Each phase represents a stage of the mission.

Ask inline (free text, not `AskUserQuestion`):

```
Define the phases for this playbook, comma-separated. Common patterns:
  - Research, Plan, Implement, Test, Review
  - Investigate, Design, Build, Verify
  - Audit, Migrate, Validate, Cleanup
```

Parse the comma-separated list into individual phase names.

#### Step 3: Agent Assignments

**Discover available agents:**

Read the custom agent table in `.mission-control/settings.md`, then read `.claude/agents/*.md` and extract `name` and `description` from each file's YAML frontmatter. Both are project agents and have **higher precedence** than this plugin's built-in agents. Built-in agents are fallbacks only:

- `researcher` — Read-only exploration and analysis
- `mission-planner` — Goal decomposition and planning
- `implementer` — Code writing and file creation
- `reviewer` — Quality assurance and validation
- `retrospective` — Learning extraction

**Infer agent assignments:**

For each phase, infer the best agent by matching the phase name against agent names and descriptions. **Always prefer a project agent over a built-in if the project agent's name or description is a plausible match.** Only fall back to built-ins when no project agent fits.

Use these keywords as signals when no project agent matches:

| Phase name keywords | Built-in fallback |
|---|---|
| research, explore, investigate, discover, audit, scan, trace, analyze | `researcher` |
| plan, design, architect, decompose, spec, strategy | `mission-planner` |
| implement, build, code, fix, migrate, execute, create, develop, write | `implementer` |
| review, verify, validate, test, check, qa, regression | `reviewer` |
| debrief, retrospective, learn, extract, summarize | `retrospective` |

**Present inferred assignments for confirmation:**

Display all phases with their inferred agents and ask the user to approve or override:

```
Here are the proposed agent assignments:

  Phase 1: [Name] → [agent]  ([project agent] / built-in fallback)
  Phase 2: [Name] → [agent]
  ...

AskUserQuestion:
  question: "Do these agent assignments look right?"
  options:
    - "Looks good, confirm all"
    - "Change Phase 1: [Name]"
    - "Change Phase 2: [Name]"
    ...
```

If the user selects a phase to change, present the full agent list with **project agents listed first**, then built-ins. Repeat until the user confirms all assignments.

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
    - "Tier 3 — Critical, human confirmation before every irreversible action"

Approval:
  options:
    - "never — Fully autonomous"
    - "tier1+ — Approve Tier 1 and above"
    - "tier2+ — Approve Tier 2 and above"
    - "always — Approve every task"
```

#### Step 6: Save Playbook

Create `.mission-control/playbooks/` directory if it does not exist.

Save the playbook to `.mission-control/playbooks/{name}.md` using the exact field format defined by the `playbook` skill's schema reference — the loader reads these bolded field names:

```markdown
---
name: [name]
description: [description]
planningDepth: [skip|lite|spec|full]
requireApproval: [never|tier1+|tier2+|always]
riskTier: [0|1|2|3]
---

# [Name] Playbook

[description]

## Phases

### Phase 1: [Phase Name]
- **Agents**: [agent-type]
- **Parallel**: [true if no dependencies, false otherwise]
- **Depends On**: none

#### Tasks
1. [General task description for this phase]

### Phase 2: [Phase Name]
- **Agents**: [agent-type]
- **Depends On**: Phase 1

#### Tasks
1. [General task description for this phase]

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

Search for the playbook by name in this exact order. **Do NOT report "not found" until all three steps have been attempted.**

1. Check built-in playbooks. Match against: `full-stack-feature`, `bug-investigation`, `refactoring`, `security-audit`, `migration`. If matched, use the built-in definition below — skip steps 2 and 3.
2. **Always check `.mission-control/playbooks/{name}.md` if step 1 did not match.** Read the file if it exists and use it as the playbook definition.
3. If step 2 found no file, check `.mission-control/playbooks/` for any `.md` files whose filename contains the requested name as a substring.

Only after completing all three steps without a match, report:

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

Ask the user for the mission goal inline (free text, not `AskUserQuestion`):

```
What is the goal for this mission? The playbook "[name]" will structure the execution.
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

The five built-in playbooks are defined in one place only: the `playbook` skill, which carries their full phase tables, default settings, and success criteria in its `built-in-playbooks` reference. Invoke that skill when `/playbook use` loads a built-in and follow its definitions verbatim. Do not restate the phase structures here — a second copy drifts from the first.
