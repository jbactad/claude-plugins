# Memory Scoring Algorithm

## Overview

The scoring algorithm determines which memory files an agent receives for a given feature. It runs inside `loadRelevantMemory(projectPath, featureTitle, featureDescription, fsModule)` in `@automaker/utils`.

## Core Functions

### `extractTerms(text: string): string[]`

Tokenize input text into normalized terms for matching.

**Steps:**
1. Convert text to lowercase
2. Split on whitespace, punctuation, hyphens, and underscores
3. Remove stop words (a, an, the, is, are, to, for, with, etc.)
4. Remove terms shorter than 2 characters
5. Deduplicate the result

**Example:**
```
Input:  "Add JWT authentication to login endpoint"
Output: ["add", "jwt", "authentication", "login", "endpoint"]
```

### `countMatches(haystack: string[], needles: string[]): number`

Count how many terms from `needles` appear in `haystack`.

**Steps:**
1. Convert `haystack` to a Set for O(1) lookups
2. Iterate over `needles`, counting members present in the Set
3. Return the count

**Example:**
```
haystack: ["jwt", "authentication", "middleware", "bearer-token"]
needles:  ["jwt", "authentication", "login", "endpoint"]
Result:   2  (jwt, authentication)
```

### `calculateUsageScore(usageStats: { loaded: number, referenced: number, successfulFeatures: number }): number`

Derive a multiplier from historical usage data using rate-based calculations.

**Formula:**
```
if loaded === 0: return 1.0  (new file, neutral score)

referenceRate = referenced / loaded
successRate = referenced > 0 ? successfulFeatures / referenced : 0

usageScore = 0.5 + referenceRate * 0.3 + successRate * 0.2
```

- New files (loaded = 0) get a neutral score of 1.0
- Base is 0.5, with up to 0.3 added from reference rate and up to 0.2 from success rate
- Maximum possible score is 1.0 (0.5 + 0.3 + 0.2)
- Higher reference-to-load ratio indicates the memory is actively useful
- Higher success-to-reference ratio indicates the memory leads to good outcomes

**Examples:**
```
{ loaded: 0,  referenced: 0, successfulFeatures: 0 }   → 1.0   (new file, neutral)
{ loaded: 10, referenced: 5, successfulFeatures: 3 }   → 0.77  (0.5 + 0.15 + 0.12)
{ loaded: 10, referenced: 10, successfulFeatures: 10 }  → 1.0   (0.5 + 0.3 + 0.2 = max)
{ loaded: 20, referenced: 2, successfulFeatures: 0 }   → 0.53  (0.5 + 0.03 + 0.0)
```

## Scoring Formula

### Weight Factors

| Source | Weight | Rationale |
|--------|--------|-----------|
| `tags` | x3 | Specific keywords chosen to match feature vocabulary |
| `relevantTo` | x2 | Broader topic associations |
| `summary` | x1 | General term matching, lowest specificity |

### Score Calculation

For each memory file, given the feature title and description:

```
featureTerms = extractTerms(featureTitle + " " + featureDescription)

tagScore      = countMatches(tags, featureTerms) * 3
relevantScore = countMatches(relevantTo, featureTerms) * 2
summaryTerms  = extractTerms(summary)
summaryScore  = countMatches(summaryTerms, featureTerms) * 1

matchScore = tagScore + relevantScore + summaryScore
usageScore = calculateUsageScore(usageStats)

finalScore = matchScore * importance * usageScore
```

### Selection Process

1. **Always include:** `gotchas.md` and any file with `importance >= 0.9` (bypass scoring)
2. **Score remaining files** using the formula above
3. **Sort** by `finalScore` descending
4. **Select top N** files where N = `maxMemoryFiles` (default: 5) minus the count of always-included files
5. **Skip files** with `finalScore === 0` (no relevance signal at all)

## Worked Example

### Setup

Consider a feature: **"Add JWT authentication to login endpoint"**

```
featureTerms = extractTerms("Add JWT authentication" + " " + "to login endpoint")
             = ["add", "jwt", "authentication", "login", "endpoint"]
```

The project has these memory files:

#### File: `gotchas.md`
```yaml
tags: [deployment, ci, env-vars]
relevantTo: [all]
summary: Critical warnings and known pitfalls
importance: 0.95
usageStats: { loaded: 30, referenced: 8, successfulFeatures: 6 }
```

#### File: `authentication.md`
```yaml
tags: [jwt, session, oauth, bearer-token, middleware]
relevantTo: [login, security, user-management, api-design]
summary: Authentication patterns including JWT handling and session conventions
importance: 0.8
usageStats: { loaded: 12, referenced: 4, successfulFeatures: 3 }
```

#### File: `testing.md`
```yaml
tags: [vitest, playwright, fixtures, mocking]
relevantTo: [unit-tests, e2e, coverage]
summary: Test patterns, fixture locations, and mocking strategies
importance: 0.6
usageStats: { loaded: 8, referenced: 1, successfulFeatures: 1 }
```

#### File: `api-conventions.md`
```yaml
tags: [rest, endpoint, response-format, status-codes, validation]
relevantTo: [routes, handlers, api-design, backend]
summary: API design decisions and endpoint naming conventions
importance: 0.7
usageStats: { loaded: 5, referenced: 2, successfulFeatures: 1 }
```

#### File: `database.md`
```yaml
tags: [drizzle, postgresql, migration, schema]
relevantTo: [data-layer, persistence, models]
summary: Database schema conventions and migration procedures
importance: 0.6
usageStats: { loaded: 3, referenced: 0, successfulFeatures: 0 }
```

### Step 1: Always-Include Files

`gotchas.md` has `importance: 0.95` (>= 0.9) — include automatically.

Remaining slots: 5 - 1 = 4

### Step 2: Score Each Remaining File

**`authentication.md`**
```
tagScore = countMatches(["jwt", "session", "oauth", "bearer-token", "middleware"], featureTerms) * 3
         = 1 * 3 = 3   (matches: jwt)

relevantScore = countMatches(["login", "security", "user-management", "api-design"], featureTerms) * 2
              = 1 * 2 = 2   (matches: login)

summaryTerms = ["authentication", "patterns", "including", "jwt", "handling", "session", "conventions"]
summaryScore = countMatches(summaryTerms, featureTerms) * 1
             = 2 * 1 = 2   (matches: authentication, jwt)

matchScore = 3 + 2 + 2 = 7
usageScore = 0.5 + (4/12) * 0.3 + (3/4) * 0.2 = 0.5 + 0.1 + 0.15 = 0.75
finalScore = 7 * 0.8 * 0.75 = 4.2
```

**`testing.md`**
```
tagScore = countMatches(["vitest", "playwright", "fixtures", "mocking"], featureTerms) * 3
         = 0 * 3 = 0

relevantScore = countMatches(["unit-tests", "e2e", "coverage"], featureTerms) * 2
              = 0 * 2 = 0

summaryTerms = ["test", "patterns", "fixture", "locations", "mocking", "strategies"]
summaryScore = countMatches(summaryTerms, featureTerms) * 1
             = 0 * 1 = 0

matchScore = 0
finalScore = 0 * 0.6 * anything = 0.0
```

**`api-conventions.md`**
```
tagScore = countMatches(["rest", "endpoint", "response-format", "status-codes", "validation"], featureTerms) * 3
         = 1 * 3 = 3   (matches: endpoint)

relevantScore = countMatches(["routes", "handlers", "api-design", "backend"], featureTerms) * 2
              = 0 * 2 = 0

summaryTerms = ["api", "design", "decisions", "endpoint", "naming", "conventions"]
summaryScore = countMatches(summaryTerms, featureTerms) * 1
             = 1 * 1 = 1   (matches: endpoint)

matchScore = 3 + 0 + 1 = 4
usageScore = 0.5 + (2/5) * 0.3 + (1/2) * 0.2 = 0.5 + 0.12 + 0.1 = 0.72
finalScore = 4 * 0.7 * 0.72 = 2.016
```

**`database.md`**
```
tagScore = countMatches(["drizzle", "postgresql", "migration", "schema"], featureTerms) * 3
         = 0 * 3 = 0

relevantScore = countMatches(["data-layer", "persistence", "models"], featureTerms) * 2
              = 0 * 2 = 0

summaryTerms = ["database", "schema", "conventions", "migration", "procedures"]
summaryScore = countMatches(summaryTerms, featureTerms) * 1
             = 0 * 1 = 0

matchScore = 0
finalScore = 0 * 0.6 * anything = 0.0
```

### Step 3: Sort and Select

| File | Final Score |
|------|-------------|
| `authentication.md` | 4.2 |
| `api-conventions.md` | 2.016 |
| `testing.md` | 0.0 (skipped) |
| `database.md` | 0.0 (skipped) |

### Step 4: Final Selection

Files loaded for the feature "Add JWT authentication to login endpoint":

1. **`gotchas.md`** — always included (importance >= 0.9)
2. **`authentication.md`** — score 4.2 (strong match on tags, relevantTo, and summary)
3. **`api-conventions.md`** — score 2.016 (moderate match on endpoint-related terms)

`testing.md` and `database.md` score 0.0 and are skipped. The agent receives 3 files total.

## Key Takeaways for Optimization

- **Tags are the strongest signal (x3 weight).** Use the exact terms that appear in feature descriptions.
- **RelevantTo casts a wider net.** Use it for related areas that share the same memory.
- **Importance acts as a gate.** Files below 0.3 importance rarely get selected unless the match is very strong.
- **Usage stats provide a gentle boost**, not a dominant factor. A well-tagged file with zero usage still outscores a poorly-tagged file with high usage.
- **Zero-scoring files are never loaded.** If a file has no term overlap with the feature context, it will not appear regardless of importance (unless importance >= 0.9).
