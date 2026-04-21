# Memory File Format

Each memory file is a standalone markdown document with YAML frontmatter. One file captures one learning.

## YAML Frontmatter Schema

```yaml
---
tags:
  - <string>
  - <string>
source: <string>
extractedAt: <string>
confidence: <low|medium|high>
category: <pattern|gotcha|architecture|tooling|prompt>
---
```

## Field-by-Field Documentation

### tags (string[], required)

Keywords used to match this learning against mission goals. The system performs case-insensitive substring matching: if any tag appears as a substring in the mission goal text, the learning is considered relevant.

**Guidelines:**
- Use specific, meaningful terms: `vitest`, `monorepo`, `worktree`, `eslint`, `api-routes`.
- Include both the technology name and the concept: `["vitest", "testing", "root-flag"]`.
- Avoid overly broad tags like `code`, `bug`, `fix` -- these match too many missions and dilute relevance.
- Aim for 2-5 tags per learning. Fewer is too narrow; more is too broad.
- Use lowercase. Tags are matched case-insensitively but storing them lowercase is convention.

### source (string, required)

The identifier of the mission that produced this learning. Format: the mission ID from `active.json` (e.g., `mission-2025-01-15-auth-refactor`). For manually created learnings, use `manual`.

**Guidelines:**
- Always trace back to the originating mission for auditability.
- If a learning is reinforced by a later mission, update the `source` to the latest mission ID and bump `confidence`.

### extractedAt (string, required)

ISO-8601 datetime when the learning was extracted or last updated. Example: `2025-07-15T14:30:00Z`.

**Guidelines:**
- Use UTC timezone.
- Update this timestamp whenever the learning is modified or reinforced.

### confidence (string, required)

How confident the system (or human) is in this learning. One of: `low`, `medium`, `high`.

| Level | Meaning | When to use |
|-------|---------|-------------|
| `high` | Verified across multiple missions or by human review. This learning is reliable and should be trusted. | Pattern confirmed in 2+ missions; human-verified gotcha; well-established architectural constraint. |
| `medium` | Observed in one mission with clear evidence. Likely correct but not yet confirmed across missions. | Single mission observation with clear cause-and-effect; manual entry with reasonable confidence. |
| `low` | Inferred from indirect evidence. May be correct but needs confirmation. | Correlation without clear causation; edge case that may not generalize; speculative pattern. |

### category (string, required)

The type of learning. One of: `pattern`, `gotcha`, `architecture`, `tooling`, `prompt`.

| Category | What it captures | Loading behavior |
|----------|-----------------|------------------|
| `pattern` | A successful approach to reuse. | Tag-matched. |
| `gotcha` | A mistake or trap to avoid. | **Always loaded.** |
| `architecture` | A structural constraint or design decision. | Tag-matched. |
| `tooling` | A tool-specific quirk or configuration. | Tag-matched. |
| `prompt` | A prompt technique that improved agent output. | Tag-matched. |

---

## Complete Examples

### Pattern

```markdown
---
tags:
  - monorepo
  - build
  - packages
source: mission-2025-06-10-add-mcp-server
extractedAt: 2025-06-10T16:45:00Z
confidence: high
category: pattern
---

# Always Build Packages Before Server

In this monorepo, shared packages in `libs/` must be built before `apps/server` or `apps/ui` can compile. Run `npm run build:packages` before any other build step.

The build order is enforced by the dependency chain: `types` -> `utils`, `prompts`, `platform`, `model-resolver`, `dependency-resolver` -> `git-utils` -> `server`, `ui`. The `build:packages` script handles this ordering automatically.

Skipping this step causes TypeScript compilation errors in consuming packages because they import from `dist/` directories that do not exist yet.
```

### Gotcha

```markdown
---
tags:
  - vitest
  - testing
  - monorepo
source: mission-2025-05-22-test-infrastructure
extractedAt: 2025-05-22T11:20:00Z
confidence: high
category: gotcha
---

# Vitest Requires --root Flag in Monorepo

When running Vitest for an individual package from the monorepo root, you must pass the `--root` flag pointing to the package directory:

```bash
# Correct
npx vitest run --config libs/utils/vitest.config.ts --root libs/utils/

# Wrong -- will fail with module resolution errors
npx vitest run --config libs/utils/vitest.config.ts
```

Without `--root`, Vitest resolves paths relative to the monorepo root instead of the package root, causing import resolution failures. This affects all packages in `libs/`.
```

### Architecture

```markdown
---
tags:
  - packages
  - dependencies
  - imports
source: mission-2025-04-18-package-restructure
extractedAt: 2025-04-18T09:15:00Z
confidence: high
category: architecture
---

# Package Dependency Chain Is Strictly Ordered

Packages in `libs/` follow a strict dependency chain. A package can only import from packages above it in the hierarchy:

```
@myapp/types        (no dependencies)
    |
@myapp/utils        (depends on types)
@myapp/prompts      (depends on types)
@myapp/platform     (depends on types)
@myapp/model-resolver    (depends on types)
@myapp/dependency-resolver (depends on types)
    |
@myapp/git-utils    (depends on types, utils, platform)
    |
apps/server, apps/ui    (can depend on any package)
```

Violating this order causes circular dependencies and build failures. When adding new imports to a package, verify the dependency is allowed by this chain.
```

### Tooling

```markdown
---
tags:
  - npm
  - scripts
  - testing
source: mission-2025-07-01-ci-setup
extractedAt: 2025-07-01T13:00:00Z
confidence: medium
category: tooling
---

# Test Commands Use Different Frameworks

The project has multiple test commands that use different frameworks:

- `npm run test` -- Playwright (E2E tests, requires browser binaries).
- `npm run test:server` -- Vitest (server unit tests).
- `npm run test:packages` -- Vitest (shared package tests, runs across all `libs/`).
- `npm run test:all` -- Vitest (combines `test:packages` and `test:server`).

When a task card says "run tests," check which test command is appropriate for the files you changed. If you only changed server code, `npm run test:server` is sufficient. If you changed a shared package, use `npm run test:packages`. Only run `npm run test` (Playwright) when E2E verification is needed.
```

### Prompt

```markdown
---
tags:
  - researcher
  - exploration
  - prompting
source: mission-2025-06-25-api-redesign
extractedAt: 2025-06-25T17:30:00Z
confidence: medium
category: prompt
---

# Give Researchers Specific Starting Points

Researcher agents produce significantly better results when given specific file paths or directory paths to start exploring, rather than open-ended instructions like "explore the codebase."

Instead of:
> Research how authentication works in this project.

Use:
> Research how authentication works. Start with `apps/server/src/routes/auth/` and `apps/server/src/lib/auth.ts`. Look for middleware in `apps/server/src/middleware/`.

Starting points reduce wasted exploration turns and ensure the researcher examines the most relevant code first. The researcher will still explore beyond the starting points if needed, but the initial direction prevents aimless searching.
```

---

## Anti-Patterns

### Empty Tags

```yaml
tags: []    # BAD: will never match any mission goal
```

Every learning needs at least one tag. Gotchas technically do not need tags for loading (they are always loaded), but tags still help with searching and organization.

### Vague Summaries

```markdown
# Be Careful With Imports    # BAD: vague, not actionable

Something weird happens with imports sometimes.    # BAD: no specifics
```

Learnings must be specific and actionable. Include file paths, commands, error messages, or code snippets that make the learning immediately useful.

### Duplicate Entries

If a learning already exists for a topic, update the existing file rather than creating a new one. Check for existing files with similar tags or names before creating a new learning. When reinforced by a new mission:
- Update the `source` to the latest mission ID.
- Update `extractedAt` to the current timestamp.
- Bump `confidence` if appropriate (medium to high after second confirmation).
- Add any new details to the body.

### Stale Data

Learnings can become stale when the codebase changes. If a refactoring removes the code that a gotcha warns about, the learning should be deleted or updated. During `/debrief`, the retrospective agent checks whether existing learnings still apply and flags any that reference files or patterns that no longer exist.
