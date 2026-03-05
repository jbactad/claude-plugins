# Memory File Format Specification

## YAML Frontmatter Schema

Every memory file in `.automaker/memory/` must include YAML frontmatter delimited by `---` lines at the top of the file.

```yaml
---
tags: string[]           # Keywords for scoring against feature descriptions
relevantTo: string[]     # Broader topics/areas this memory relates to
summary: string          # One-line description for scoring
importance: number       # 0.0 to 1.0 (>= 0.9 always loaded)
relatedFiles: string[]   # File paths related to this memory (informational)
usageStats:
  loaded: number         # Times this file was included in agent context
  referenced: number     # Times agent explicitly referenced this memory
  successfulFeatures: number  # Times a feature using this memory completed successfully
---
```

## Field-by-Field Documentation

### `tags` (string[])

**Purpose:** Provide specific keywords that the scoring algorithm matches against feature titles and descriptions. Tags carry a **x3 weight** in the scoring formula.

**How to choose tags:**
- Use concrete, specific terms that appear in feature descriptions
- Include technology names, library names, and protocol names
- Mirror the vocabulary developers use when writing feature titles
- Keep tags lowercase and hyphenated for consistency

**Good tags:**
```yaml
tags:
  - jwt
  - authentication
  - refresh-token
  - middleware
  - bearer-token
```

**Bad tags:**
```yaml
tags:
  - code          # Too vague, matches everything
  - important     # Not a searchable topic
  - misc          # Meaningless for scoring
  - stuff         # Provides no signal
```

### `relevantTo` (string[])

**Purpose:** Define broader topic areas this memory relates to. RelevantTo carries a **x2 weight** in the scoring formula. Use this field to capture associations that are wider than specific tags.

**How to choose relevantTo (vs tags):**
- Tags = specific terms (e.g., `jwt`, `bcrypt`, `passport`)
- RelevantTo = broad areas (e.g., `authentication`, `security`, `user-management`)
- A memory about JWT should tag `jwt` but be relevantTo `authentication` and `security`

**Good relevantTo:**
```yaml
relevantTo:
  - authentication
  - security
  - user-management
  - api-design
```

**Bad relevantTo:**
```yaml
relevantTo:
  - jwt              # Too specific — belongs in tags
  - RS256            # Implementation detail — belongs in tags
  - everything       # Meaningless for scoring
```

### `summary` (string)

**Purpose:** Provide a concise one-line description used for scoring (x1 weight) and for quick human scanning. The scoring algorithm tokenizes this string and matches terms against the feature context.

**Guidelines:**
- Keep to a single sentence
- Include the most important keywords naturally
- Describe what the memory covers, not what it is

**Good summaries:**
```yaml
summary: Authentication patterns including JWT handling, session management, and middleware conventions
```

**Bad summaries:**
```yaml
summary: Some notes about auth   # Too vague, missing key terms
summary: This file contains various authentication-related learnings gathered over time from multiple feature implementations across the project  # Too long, dilutes term density
```

### `importance` (number)

**Purpose:** Control how aggressively this memory file gets selected. Range from 0.0 to 1.0. The importance value multiplies directly into the final score.

**Special behavior:**
- `importance >= 0.9` — File is **always loaded** regardless of scoring, bypassing the selection algorithm entirely
- `importance >= 0.7` — High priority, selected for most loosely-related features
- `importance >= 0.4` — Moderate priority, selected when relevance is clear
- `importance < 0.4` — Low priority, only selected for strongly matching features

**Guidelines for setting importance:**
| Importance | Use For |
|------------|---------|
| 0.9 - 1.0 | Critical warnings, project-wide gotchas, must-know information |
| 0.7 - 0.8 | Core patterns used in most features, architectural decisions |
| 0.5 - 0.6 | Domain-specific knowledge, useful for a subset of features |
| 0.3 - 0.4 | Niche topics, rarely needed but valuable when relevant |
| 0.1 - 0.2 | Historical notes, nice-to-know, low-impact conventions |

### `relatedFiles` (string[])

**Purpose:** List file paths related to this memory entry. Informational field used for documentation — does not affect scoring.

**Examples:**
```yaml
relatedFiles:
  - src/middleware/auth.ts
  - src/routes/login.ts
```

Initialize to `[]` for new files.

### `usageStats` (object)

**Purpose:** Track how often this memory file is loaded and referenced. These statistics feed into the `calculateUsageScore()` function, which acts as a multiplier on the final score.

#### `usageStats.loaded` (number)

Count of times this file was included in an agent's context. Incremented automatically by Automaker when the file is selected during `loadRelevantMemory()`. Initialize to `0` for new files.

#### `usageStats.referenced` (number)

Count of times an agent explicitly referenced or cited this memory during execution. Incremented via `recordMemoryUsage()` when the agent output references the memory. Initialize to `0` for new files.

#### `usageStats.successfulFeatures` (number)

Count of times a feature that loaded this memory completed successfully. Incremented when a feature using this memory reaches `completed` status. Initialize to `0` for new files.

**How usageStats influence scoring:**
- Files with zero usage start with a neutral usage score (1.0)
- The usage score is rate-based: `0.5 + (referenced/loaded) * 0.3 + (successfulFeatures/referenced) * 0.2`
- A higher reference-to-load ratio indicates the file is actively useful
- A higher success-to-reference ratio indicates the file leads to good outcomes
- See `scoring-algorithm.md` for the exact `calculateUsageScore()` formula

## Complete Example

A well-structured memory file:

```markdown
---
tags:
  - database
  - drizzle
  - migration
  - schema
  - postgresql
relevantTo:
  - data-layer
  - persistence
  - models
  - backend
summary: Database schema conventions, Drizzle ORM patterns, and migration procedures
importance: 0.7
relatedFiles:
  - libs/db/src/schema/
usageStats:
  loaded: 12
  referenced: 4
  successfulFeatures: 3
---

# Database Patterns

## Schema Conventions
- Define all schemas in `libs/db/src/schema/` with one file per table
- Export schemas from `libs/db/src/schema/index.ts`
- Use `snake_case` for column names, `camelCase` for TypeScript properties
- Always include `createdAt` and `updatedAt` timestamps on every table

## Migration Procedures
- Generate migrations with `npm run db:generate` after schema changes
- Never edit generated migration files manually
- Run `npm run db:migrate` to apply pending migrations
- Test migrations against a fresh database before committing

## Gotchas
- Drizzle `eq()` does not handle `null` — use `isNull()` instead
- The `returning()` clause is PostgreSQL-specific; do not use with SQLite in tests
- Connection pool max size is set to 10 in production; exceeding it causes silent hangs
```

## Anti-Patterns

### Frontmatter with no useful tags
```yaml
---
tags: []
relevantTo: []
summary: ""
importance: 0.5
relatedFiles: []
usageStats:
  loaded: 0
  referenced: 0
  successfulFeatures: 0
---
```
This file will score near zero for every feature. Always provide meaningful tags and a summary.

### Overlapping category files
Avoid creating `auth.md`, `authentication.md`, and `login.md` that all cover the same topic. Consolidate into a single file with comprehensive tags and relevantTo values.

### Stale usageStats after reorganization
When splitting or merging memory files, reset `usageStats` to `{ loaded: 0, referenced: 0, successfulFeatures: 0 }` since the historical stats no longer apply to the new file content.
