---
name: feature-optimizer
description: This skill should be used when the user asks to "create a feature", "add a feature", "plan feature implementation", "optimize features", "improve feature descriptions", "configure planning mode", "set up feature dependencies", "enhance feature cards", "batch create features", "break down work into features", or wants to create or improve feature cards for better AI agent execution in Automaker. Also use when discussing feature.json schema, feature statuses, description enhancement modes, thinking levels, planning modes (skip/lite/spec/full), or feature execution pipeline configuration.
---

# Automaker Feature Optimizer

Create and optimize feature card definitions in `.automaker/features/` so Automaker's AI agents produce higher-quality implementations with fewer iterations.

## How Features Work

Each feature in Automaker is stored as `.automaker/features/{featureId}/feature.json`. Features represent units of work on the Kanban board — the AI agent reads the feature's `description` and implements it in an isolated git worktree. The quality of the description directly impacts the quality of the agent's output.

Features flow through statuses: `pending` → `running` → `completed` (or `failed`) → `verified`.

## Creating Features

### Feature ID and Storage

Generate a feature ID: `feature-{Date.now()}-{random9chars}` (e.g., `feature-1707123456789-abc123def`).

Create the feature directory and file:

```
.automaker/features/{featureId}/feature.json
```

Minimal feature:

```json
{
  "id": "feature-1707123456789-abc123def",
  "category": "backlog",
  "description": "Add rate limiting to the /api/features endpoint using express-rate-limit with 100 requests per 15-minute window"
}
```

### Categories

Use categories matching project areas. Common examples: `backlog`, `in_progress`, `done`, or custom categories like `Backend`, `Frontend`, `Infrastructure`, `Testing`, `Bug Fix`, `Refactoring`. Categories map to Kanban board columns and are defined in `.automaker/categories.json`.

## Feature Optimization Workflow

### 1. Analyze Existing Features

Before optimizing, read the current features to understand patterns:

- **Description quality** — Vague descriptions produce vague implementations
- **Dependency chains** — Missing dependencies cause features to fail when they depend on unimplemented code
- **Planning mode selection** — Wrong planning mode wastes tokens or produces shallow implementations
- **Model selection** — Underpowered models struggle with complex features

### 2. Write Effective Descriptions

The `description` field is the most impactful field — it's the primary input to the AI agent.

**Structure effective descriptions with:**

1. **What** — Clear statement of the feature's purpose
2. **Where** — Specific file paths or modules to modify/create
3. **How** — Implementation approach, patterns to follow, libraries to use
4. **Constraints** — What NOT to do, edge cases, compatibility requirements
5. **Acceptance criteria** — How to verify the feature works

**Example — Good description:**

```
Add JWT authentication middleware to the Express API.

Create `src/middleware/auth.ts` that:
- Extracts Bearer token from Authorization header
- Verifies token using jsonwebtoken library (already in package.json)
- Attaches decoded user payload to `req.user`
- Returns 401 for missing/invalid tokens

Apply middleware to all routes in `src/routes/` except:
- POST /api/auth/login
- POST /api/auth/register
- GET /api/health

Follow the error handling pattern in `src/middleware/error-handler.ts`.
Add unit tests in `src/middleware/__tests__/auth.test.ts`.
```

**Example — Bad description:**

```
Add authentication to the API.
```

### 3. Use Description Enhancement Modes

Automaker offers built-in enhancement modes via the `POST /api/features/{id}/enhance` endpoint:

| Mode | Purpose | When to Use |
|------|---------|-------------|
| `improve` | General quality improvement | First pass on rough descriptions |
| `technical` | Add implementation details, file paths, patterns | After initial description is clear |
| `simplify` | Reduce complexity, focus on core requirement | When description is overloaded |
| `acceptance` | Add testable acceptance criteria | Before marking features ready |
| `ux-reviewer` | Add UX considerations and user flow details | For UI/frontend features |

Enhancement history is tracked in `descriptionHistory` — previous versions are preserved.

### 4. Configure Planning Mode

Select the right planning mode based on feature complexity:

| Mode | Agent Behavior | Best For |
|------|---------------|----------|
| `skip` | Implement immediately, no planning | Simple changes, bug fixes, one-file edits |
| `lite` | Quick task decomposition, then implement | Small features, 2-3 file changes |
| `spec` | Generate spec with tasks, optionally approve | Medium features, multi-file changes |
| `full` | Full phased plan with task tracking | Complex features, architectural changes |

**Rules of thumb:**
- Use `skip` for features under 50 words
- Use `lite` for features that touch 2-3 files
- Use `spec` for features spanning 4+ files or requiring new patterns
- Use `full` for features that need phased rollout or have complex dependencies

Set `requirePlanApproval: true` with `spec` or `full` to review the agent's plan before it executes.

### 5. Set Dependencies

Features can declare dependencies on other features via the `dependencies` array (list of feature IDs). Automaker uses Kahn's algorithm to resolve dependency order and blocks execution until dependencies complete.

**Dependency best practices:**
- Only declare direct dependencies, not transitive ones
- Ensure no circular dependency chains
- Keep dependency chains shallow (2-3 levels max)
- Use categories to group related features visually on the board

### 6. Configure Model and Thinking

Select appropriate model and thinking level per feature:

| Setting | Options | Impact |
|---------|---------|--------|
| `model` | `claude-opus`, `claude-sonnet`, `claude-haiku` | Quality vs speed tradeoff |
| `thinkingLevel` | `none`, `low`, `medium`, `high`, `ultrathink` | Reasoning depth (token budget) |
| `skipTests` | `true/false` | Skip test generation step |
| `excludedPipelineSteps` | Array of step IDs | Skip specific pipeline steps |

**Model selection guide:**
- **Opus** — Complex features, architectural work, multi-file refactors
- **Sonnet** — Standard features, well-described tasks
- **Haiku** — Simple fixes, typos, configuration changes

### 7. Optimize for Batch Execution (Auto-Mode)

When using auto-mode to execute multiple features:

- **Order by dependencies** — Features with no dependencies execute first
- **Balance complexity** — Mix simple and complex features for consistent throughput
- **Set `maxConcurrentAgents`** — Limit parallelism to avoid overwhelming the codebase
- **Use consistent planning modes** — Don't mix `full` and `skip` in the same batch unless intentional
- **Include cleanup features** — Add "lint fix" or "format code" features at the end of batches

## Quick Reference: Feature Schema

| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| `id` | `string` | Yes | Unique feature identifier |
| `title` | `string` | No | Short display name (auto-generated if empty) |
| `category` | `string` | Yes | Board column (e.g., "backlog", "in_progress") |
| `description` | `string` | Yes | Full implementation instructions |
| `priority` | `number` | No | Sort order within category |
| `dependencies` | `string[]` | No | Feature IDs this depends on |
| `model` | `string` | No | Claude model override |
| `thinkingLevel` | `string` | No | Extended thinking level |
| `planningMode` | `string` | No | Planning approach |
| `requirePlanApproval` | `boolean` | No | Require plan review before execution |
| `skipTests` | `boolean` | No | Skip test generation |
| `imagePaths` | `array` | No | Reference screenshots/mockups |
| `textFilePaths` | `array` | No | Reference text files with content |
| `status` | `string` | No | Current status (managed by Automaker) |
| `branchName` | `string` | No | Git branch for this feature |

## Additional Resources

### Reference Files

- **`references/feature-schema.md`** — Complete `Feature` TypeScript interface with all fields documented, including `PlanSpec`, `ParsedTask`, `DescriptionHistoryEntry`, and export/import types
- **`references/planning-modes.md`** — Detailed comparison of planning modes with examples, token usage estimates, and decision flowchart for selecting the right mode
