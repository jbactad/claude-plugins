---
name: memory-manager
description: This skill should be used when the user asks to "manage Automaker memory", "add a learning", "create memory files", "organize project memory", "update .automaker/memory", "view agent learnings", or wants to interact with the Automaker memory system. Also use when discussing memory file YAML frontmatter, memory scoring, smart memory selection, or how to help AI agents learn from past feature implementations.
---

# Automaker Memory Manager

## Overview

The Automaker memory system persists learnings across feature implementations so AI agents benefit from past experience. Memory files live at `.automaker/memory/*.md` within each project. Each file uses YAML frontmatter for metadata and a markdown body for the actual learnings. Automaker smart-selects the most relevant memory files for each feature based on a scoring algorithm, injecting them into agent prompts under a `# Project Memory` heading.

## Memory System Architecture

### File Organization

- Store all memory files in `.automaker/memory/`
- Use the filename as the category name (e.g., `patterns.md`, `gotchas.md`)
- Reserve `_index.md` as a human-readable project overview (note: `_index.md` is explicitly **excluded** from agent memory loading and scoring — it serves as documentation only)
- Keep each file focused on a single category or topic
- Limit individual files to a reasonable size — split large categories into subcategories

### How Automaker Loads Memory

The function `loadRelevantMemory(projectPath, featureTitle, featureDescription, fsModule)` in `@automaker/utils` drives memory selection:

1. Skip `_index.md` (excluded from scoring and loading — use it only as human-readable project documentation)
2. Score each `.md` file using weighted term matching against the feature title and description (see [references/scoring-algorithm.md](references/scoring-algorithm.md) for the complete algorithm)
3. Include files with `score > 0` or `importance >= 0.9`
4. Sort by score, select the top 5 files
5. Always include `gotchas.md` even if not scored
6. Inject selected files into the agent prompt under `# Project Memory`

Supporting functions:
- `appendLearning(projectPath, category, learning)` — add new entries programmatically
- `incrementUsageStat(filePath, stat)` — atomically update loaded/referenced/successfulFeatures counters

## Creating Memory Files

### Frontmatter Structure

Every memory file requires YAML frontmatter. See [references/memory-format.md](references/memory-format.md) for the complete field specification.

```markdown
---
tags:
  - authentication
  - jwt
  - middleware
relevantTo:
  - login
  - session
  - auth
summary: Authentication patterns and JWT handling conventions
importance: 0.8
relatedFiles: []
usageStats:
  loaded: 0
  referenced: 0
  successfulFeatures: 0
---

# Authentication Patterns

## JWT Token Handling
- Always validate tokens in middleware before route handlers
- Use RS256 algorithm, never HS256 in production
```

### Writing Effective Content

Follow these principles when writing memory content:

- **Focus on non-obvious patterns.** Capture things an agent would not know from reading code alone — design decisions, historical context, subtle constraints.
- **Include file paths.** Specify where patterns apply (e.g., "Apply this middleware pattern in `apps/server/src/routes/`").
- **Write in imperative form.** Agents follow instructions more reliably than descriptions. Write "Use RS256 for JWT signing" not "We use RS256 for JWT signing."
- **Document gotchas.** Record things that failed or caused bugs. These prevent agents from repeating mistakes.
- **Keep entries atomic.** Each bullet or section should convey one discrete learning. Avoid merging unrelated points.
- **Prefer specificity over generality.** "Set `connection.timeout` to 30000ms in database config" beats "Use appropriate timeouts."

## Managing Existing Memories

### Reviewing Current State

1. List all files in `.automaker/memory/`
2. Read each file, evaluating whether content is still accurate
3. Check `usageStats` to identify files that are never loaded (potential candidates for better tagging or removal)

### Updating Learnings

- **Add new learnings** by appending to the appropriate category file, or creating a new category if none fits
- **Update outdated entries** when codebase patterns change — stale memory is worse than no memory
- **Remove incorrect information** immediately; incorrect learnings cause agents to produce bugs
- **Adjust importance scores** based on how critical the information is — raise importance for learnings that prevent production issues, lower it for nice-to-know conventions
- **Refresh tags and relevantTo** when the vocabulary of the project evolves (e.g., renaming a module should update tags referencing it)

### Reorganizing Categories

When a file grows too large or covers too many topics:

1. Identify distinct subtopics within the file
2. Create new category files for each subtopic
3. Migrate relevant entries, preserving frontmatter metadata
4. Update tags and relevantTo to maintain scoring accuracy
5. Remove the original file or keep it as a slimmer overview

## Recommended Memory Categories

### Always-Present Files

| File | Purpose | Importance |
|------|---------|------------|
| `_index.md` | Human-readable project overview (not loaded into agent context — documentation only) | N/A |
| `gotchas.md` | Critical warnings, known pitfalls, things that break builds (always loaded) | >= 0.9 |

### Standard Categories

| File | Purpose | Typical Importance |
|------|---------|-------------------|
| `patterns.md` | Codebase patterns and architectural conventions | 0.7 - 0.8 |
| `api-conventions.md` | API design decisions, endpoint naming, response formats | 0.6 - 0.8 |
| `testing.md` | Test patterns, fixture locations, mocking strategies | 0.6 - 0.7 |
| `deployment.md` | Build pipeline notes, environment configuration | 0.5 - 0.7 |
| `dependencies.md` | Package choices, version constraints, compatibility notes | 0.5 - 0.7 |
| `debugging.md` | Common issues and their solutions, error patterns | 0.6 - 0.8 |

Adjust categories to fit the project. A data-heavy project might add `database.md` or `migrations.md`. A frontend-focused project might add `styling.md` or `state-management.md`.

## Initializing Memory for a New Project

Follow these steps to bootstrap memory for a project that has no `.automaker/memory/` directory:

1. **Create the directory** at `.automaker/memory/`
2. **Create `_index.md`** with:
   - Project name and purpose
   - Tech stack summary
   - Key directory layout
   - Note: `_index.md` is excluded from agent loading — it serves as human-readable documentation and a memory index
3. **Create `gotchas.md`** with:
   - Any known pitfalls from the project's history
   - Environment-specific issues
   - Set `importance: 0.9` or higher
4. **Create 2-3 initial category files** based on the project type:
   - For a web app: `patterns.md`, `api-conventions.md`, `testing.md`
   - For a CLI tool: `patterns.md`, `dependencies.md`, `debugging.md`
   - For a library: `patterns.md`, `api-conventions.md`, `dependencies.md`
5. **Populate initial content** by reviewing existing code, README, and configuration files for non-obvious conventions

### Example `_index.md`

```markdown
---
tags:
  - overview
  - architecture
  - setup
relevantTo:
  - all
  - onboarding
  - new-feature
summary: Project overview, tech stack, and directory layout
importance: 0.9
relatedFiles: []
usageStats:
  loaded: 0
  referenced: 0
  successfulFeatures: 0
---

# Project Index

## Tech Stack
- Runtime: Node.js 22 with TypeScript 5.9
- Framework: Express 5 + React 19
- Database: PostgreSQL 16 with Drizzle ORM
- Testing: Vitest (unit), Playwright (E2E)

## Key Directories
- `apps/server/src/routes/` — API route handlers
- `apps/ui/src/components/` — React components
- `libs/` — Shared packages

## Critical Conventions
- Import shared code from `@project/package-name`, never relative paths
- Run `npm run build:packages` after modifying any lib
```

## Scoring and Selection

The scoring algorithm determines which memory files an agent receives. Understanding the weights helps write better frontmatter:

- **Tags**: x3 weight — specific keywords that match feature descriptions
- **RelevantTo**: x2 weight — broader topic areas
- **Summary**: x1 weight — general term matching

Usage score uses rate-based formula: `0.5 + (referenced/loaded) * 0.3 + (successfulFeatures/referenced) * 0.2`. New files get a neutral score of 1.0.

Final score: `(tagScore + relevantToScore + summaryScore) * importance * usageScore`. See [references/scoring-algorithm.md](references/scoring-algorithm.md) for the complete algorithm with worked examples.

### Optimizing for Scoring

- Choose filenames that match how developers describe features (e.g., `authentication.md` not `auth-stuff.md`)
- Use tags that mirror the vocabulary in feature titles and descriptions
- Set `relevantTo` to broader categories that encompass multiple features
- Write summaries that contain the key terms developers would use

## References

- For the complete YAML frontmatter specification with field-by-field documentation, see [references/memory-format.md](references/memory-format.md)
- For the full scoring algorithm with weight factors and worked examples, see [references/scoring-algorithm.md](references/scoring-algorithm.md)
