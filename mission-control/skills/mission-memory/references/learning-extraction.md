# Learning Extraction Process

The retrospective agent extracts learnings from completed missions and saves them as memory files. This document describes the trigger, inputs, extraction process, deduplication, confidence assignment, and output format.

## Trigger

Learning extraction is triggered by the `/debrief` command when `autoLearn` is enabled in the mission settings. The retrospective agent runs after all mission tasks have completed (or after the mission is aborted with partial results).

If `autoLearn` is disabled, the `/debrief` command still runs a retrospective analysis and reports findings, but does not persist learnings to disk.

## Input

The retrospective agent receives three inputs:

### 1. Mission State (`active.json`)

The mission state file contains the goal, settings, task cards, agent assignments, and status of each task. This tells the agent what was planned and what was achieved.

### 2. Mission Log (`log.jsonl`)

The mission log is a line-delimited JSON file recording every event during mission execution: task starts, task completions, task failures, agent messages, tool calls, errors, and retries. This tells the agent what actually happened at runtime.

### 3. Task Results

The output of each completed task, including implementation reports from implementers, research findings from researchers, and review verdicts from reviewers. This tells the agent what each agent produced.

## Extraction Process

The retrospective agent follows five analysis steps. Each step produces candidate learnings that are then deduplicated and persisted.

### Step 1: Identify Successful Patterns

Scan the mission log and task results for patterns that correlated with successful outcomes:

- Which orchestration pattern was used, and did it work well?
- Were there agent or model choices that performed notably well?
- Did any phase ordering or dependency structure avoid problems?
- Were there file ownership decisions that prevented conflicts?

**What to extract:** Reusable approaches that should be repeated. Category: `pattern`.

### Step 2: Identify Failures and Root Causes

Scan for tasks that failed, required retries, or produced unsatisfactory results:

- What went wrong? Trace from the symptom to the root cause.
- Was the failure due to a bad plan, a wrong model choice, insufficient context, or a codebase quirk?
- Could the failure have been prevented with prior knowledge?

**What to extract:** Traps to avoid. Category: `gotcha` (if universal) or `pattern` (if the fix is a specific approach).

### Step 3: Assess Agent and Model Choices

Review whether the right agents and models were assigned:

- Did any haiku agent struggle with a task that should have used sonnet?
- Did any sonnet agent handle a task that haiku could have done (wasted budget)?
- Were researcher agents given proper starting points, or did they waste turns on aimless exploration?
- Were reviewers effective, or did they rubber-stamp work?

**What to extract:** Model and agent selection heuristics. Category: `pattern` or `tooling`.

### Step 4: Extract Prompt Patterns

Analyze agent prompts and their correlation with output quality:

- Did specific prompt structures produce better results?
- Were there cases where adding context (file paths, examples, constraints) improved output?
- Were there prompts that were too vague and led to unfocused work?

**What to extract:** Prompt techniques. Category: `prompt`.

### Step 5: Identify Gotchas

Look for unexpected behaviors, codebase quirks, or environmental issues that caused confusion or wasted time:

- Build system surprises (missing build steps, ordering requirements).
- Test framework quirks (flags, configuration, path resolution).
- Dependency issues (version conflicts, circular imports).
- Tooling surprises (CLI flags that behave unexpectedly).

**What to extract:** Universal traps. Category: `gotcha`.

## Deduplication

Before saving a new learning, the retrospective agent checks existing memory files in `.mission-control/memory/`:

1. **Read all existing memory files** and build an index of topics, tags, and summaries.
2. **For each candidate learning**, check if an existing file covers the same topic:
   - If an existing file covers the exact same topic, **reinforce** it instead of duplicating:
     - Update `source` to the current mission ID.
     - Update `extractedAt` to the current timestamp.
     - Bump `confidence` if appropriate (e.g., medium to high after second confirmation).
     - Merge any new details into the body.
   - If an existing file covers a related but distinct topic, create a new file with distinct tags.
   - If no existing file covers the topic, create a new file.
3. **Check for stale learnings.** If an existing learning references files, functions, or patterns that no longer exist in the codebase, flag it for removal or update.

## Confidence Assignment

| Level | Criteria | Example |
|-------|----------|---------|
| `high` | Pattern observed and confirmed across 2+ missions. Or: a gotcha with clear, reproducible evidence (specific error message, specific command). | "Vitest requires --root flag" -- confirmed in 3 separate missions with the same error. |
| `medium` | Observed in a single mission with clear cause-and-effect. The evidence is direct, not inferred. | "Researcher agents performed better when given starting file paths" -- observed in this mission's log (researcher A with paths completed in 5 turns; researcher B without paths took 15 turns). |
| `low` | Inferred from indirect evidence. Correlation without clear causation. Or: a pattern observed once in unusual circumstances that may not generalize. | "Using opus for the planning phase might have prevented the re-planning that happened mid-mission" -- speculative, no controlled comparison. |

**Rules for confidence assignment:**
- Never assign `high` to a first-time observation. First observations are `medium` at most.
- Gotchas with specific error messages and reproduction steps can be `high` on first observation (the evidence is self-contained).
- Bump from `medium` to `high` only when a second mission confirms the pattern.
- `low` learnings that are not confirmed within 5 missions should be reviewed for deletion.

## Output Format

Each extracted learning is saved as a markdown file in `.mission-control/memory/`:

```
.mission-control/memory/{descriptive-kebab-case-name}.md
```

The file follows the format documented in `memory-format.md`: YAML frontmatter with `tags`, `source`, `extractedAt`, `confidence`, and `category`, followed by a markdown body.

## Examples: Good vs Bad Extraction

### Good Extraction

**Mission context:** A full-stack feature mission failed at Phase 4 (frontend implementation) because the implementer imported from `@automaker/server` directly instead of using the shared `@automaker/types` package.

**Extracted learning:**

```markdown
---
tags:
  - imports
  - frontend
  - types
  - shared-packages
source: mission-2025-08-12-user-dashboard
extractedAt: 2025-08-12T18:00:00Z
confidence: medium
category: gotcha
---

# Frontend Must Not Import from Server Package

The frontend (`apps/ui`) must never import directly from `@automaker/server`. Shared types, interfaces, and constants must come from `@automaker/types` or other `libs/` packages.

Direct server imports cause build failures because the UI build does not resolve server-side modules. The error manifests as "Module not found: @automaker/server" during Vite compilation.

If a type exists in the server but not in `@automaker/types`, move the type to `@automaker/types` first, then import from there in both server and UI.
```

**Why this is good:**
- Specific: names the exact packages, the error message, and the fix.
- Actionable: tells the agent exactly what to do and what to avoid.
- Properly categorized: this is a gotcha (universal trap), not a pattern.
- Appropriate confidence: medium (first observation, clear evidence).

---

### Bad Extraction

**Same mission context as above.**

**Poorly extracted learning:**

```markdown
---
tags:
  - code
source: mission-2025-08-12-user-dashboard
extractedAt: 2025-08-12T18:00:00Z
confidence: high
category: pattern
---

# Be Careful with Imports

Imports can cause problems. Make sure you import from the right place. The frontend had issues with imports during this mission.
```

**Why this is bad:**
- **Vague tags.** `code` matches almost every mission, making this learning noise rather than signal.
- **No specifics.** Doesn't name the packages, the error, or the fix. An agent reading this learns nothing actionable.
- **Wrong confidence.** Marked `high` despite being a first observation.
- **Wrong category.** Marked `pattern` (a positive approach to reuse) instead of `gotcha` (a trap to avoid).
- **No file paths or commands.** A learning without concrete references is a learning that will be ignored.

---

### Good Extraction (Prompt Pattern)

**Mission context:** In a codebase exploration mission, researcher A was told "explore the authentication system" and spent 18 turns before producing useful findings. Researcher B was told "explore the authentication system, starting with `src/middleware/auth.ts` and `src/routes/auth/`" and produced comprehensive findings in 7 turns.

**Extracted learning:**

```markdown
---
tags:
  - researcher
  - exploration
  - prompting
source: mission-2025-09-03-auth-audit
extractedAt: 2025-09-03T14:15:00Z
confidence: medium
category: prompt
---

# Anchor Researcher Agents with Starting File Paths

When dispatching researcher agents, always include 2-3 specific file paths or directory paths as starting points in the task description. This reduces exploration turns by 50-60% based on observed comparisons.

Instead of: "Research how authentication works in this project."
Use: "Research how authentication works. Start with `src/middleware/auth.ts` and `src/routes/auth/`. Look for session management in `src/lib/session.ts`."

The researcher will still explore beyond these starting points if needed, but anchoring prevents the initial aimless `Glob **/*` and `Grep` passes that consume turns without producing insights.
```

---

### Bad Extraction (Prompt Pattern)

**Same mission context.**

```markdown
---
tags: []
source: mission-2025-09-03-auth-audit
extractedAt: 2025-09-03T14:15:00Z
confidence: low
category: prompt
---

# Prompting Tips

Researchers work better with good prompts. Try to be specific when asking them to research things.
```

**Why this is bad:**
- **Empty tags.** Will never match any mission.
- **No concrete technique.** "Be specific" is advice so generic it provides no value.
- **No evidence.** Doesn't reference the actual comparison or the turn count difference.
- **Low confidence for a directly observed pattern.** The turn count comparison is direct evidence, warranting `medium`.
