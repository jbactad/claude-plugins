# Mission Control - Project Agents

Copy this file to `.claude/mission-control.local.md` in your project root and customize the
agent types for your stack. Mission Control reads this file at the start of every mission
and merges these types with the built-in defaults.

---

## Full-Stack Project Example

A typical web application with frontend, backend, database, security, testing, and infrastructure concerns.

### Custom Agent Types

| Type | Description | subagent_type | model | Notes |
|------|-------------|---------------|-------|-------|
| `frontend-expert` | React/TypeScript UI specialist | general-purpose | sonnet | Use for components, styling, and accessibility |
| `backend-expert` | Node/Python API and business logic specialist | general-purpose | sonnet | Use for endpoints, services, and data access |
| `db-architect` | Database schema design and query optimization | general-purpose | opus | Use for schema decisions and complex queries |
| `security-auditor` | Security review and vulnerability analysis | general-purpose | opus | Required for all Tier 2+ tasks |
| `test-runner` | Test execution and coverage analysis | Bash | haiku | Runs test suites, lint, and type checks |
| `devops-agent` | CI/CD, Docker, and infrastructure | Bash | sonnet | Use for build pipelines and deployment scripts |

---

## Minimal Single-Domain Example

A focused project may only need one or two custom types. Here is an example for a data science / ML project:

### Custom Agent Types

| Type | Description | subagent_type | model | Notes |
|------|-------------|---------------|-------|-------|
| `ml-researcher` | Model training, evaluation, and experiment tracking | general-purpose | opus | Use for all ML pipeline tasks |
| `data-engineer` | ETL pipelines and data quality | general-purpose | sonnet | Use for ingestion and transformation |

---

## How Mission Control Uses These Agents

When Mission Control reads this file, it:

1. **Outputs the full agent registry** (built-in + custom) before decomposing tasks:

```
AGENT REGISTRY
--------------
Built-in:  mission-planner, researcher, implementer, reviewer, retrospective
Custom:    frontend-expert, backend-expert, db-architect, security-auditor, test-runner, devops-agent
```

2. **Assigns the most specific matching agent type** to each task card during decomposition. If a custom type matches the task domain, it takes priority over a generic built-in type.

3. **Includes the agent's description in the spawn prompt** so the delegated agent understands its specialized role and constraints.

### Example Task Card Using a Custom Type

```
### Task: task-3
- **Title**: Implement search API endpoint
- **Agent**: backend-expert
- **Model**: sonnet
- **Risk**: Tier 1
- **Dependencies**: task-1 (DB schema), task-2 (auth patterns)
- **Files**:
  - src/api/search.ts (create)
  - src/services/SearchService.ts (create)
- **Acceptance Criteria**:
  1. GET /api/search returns paginated results
  2. Supports filter parameters for status and date range
  3. Returns 400 for invalid filter values
- **Notes**: Follow existing endpoint patterns in src/api/
```

### Example Spawn Prompt

When Mission Control delegates to a custom agent, the spawn prompt includes the agent's description from the registry:

```
You are a backend-expert: Node/Python API and business logic specialist.

Your task: Implement the /api/search endpoint with pagination and filters.

Files to create/modify:
  - src/api/search.ts (create)
  - src/services/SearchService.ts (create)

Acceptance Criteria:
  1. GET /api/search returns paginated results
  2. Supports filter parameters for status and date range
  3. Returns 400 for invalid filter values

Context: Follow existing endpoint patterns in src/api/
```

---

## Format Rules

- **`subagent_type`** must be one of: `Explore`, `Plan`, `Bash`, `general-purpose`
- **`model`** must be one of: `haiku`, `sonnet`, `opus`
- **Type names** should be kebab-case and descriptive (e.g., `frontend-expert`, not `fe`)
- **Notes** column is shown in the agent registry but not required
- Custom types **extend** the built-in agents; they never replace them
- If no `.claude/mission-control.local.md` exists, Mission Control silently falls back to built-in types only
