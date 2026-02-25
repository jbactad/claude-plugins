---
name: mission-memory-knowledge
description: >
  Knowledge about the mission memory system — persistent learnings extracted from completed
  missions. Use when the user asks about mission learnings, wants to view or manage memory
  files, or needs guidance on how the learning system works.
user-invocable: false
---

# Mission Memory System

Mission memory stores learnings extracted from completed missions in `.claude/mission-memory/`. These learnings are loaded into new missions to avoid repeating mistakes and reuse successful patterns. Over time, the memory builds a project-specific knowledge base that makes every mission smarter than the last.

## What Mission Memory Is

Mission memory is a persistent, per-project learning system. Each learning is a markdown file with YAML frontmatter that captures a single insight: a pattern that worked, a gotcha to avoid, an architectural constraint, a tooling quirk, or a prompt technique that improved agent output.

Learnings are not documentation. They are operational knowledge -- the kind of thing a senior engineer would tell a new team member on their first day: "Don't do X because Y" or "Always do A before B because C."

## Where Files Live

```
.claude/mission-memory/
├── use-named-exports.md
├── vitest-root-flag.md
├── circular-dep-gotcha.md
├── monorepo-build-order.md
├── researcher-prompt-pattern.md
└── ...
```

Each file is a standalone learning. File names should be descriptive kebab-case identifiers. There is no index file -- the system discovers learnings by reading all `.md` files in the directory.

## Categories

Every learning belongs to one of five categories:

| Category | Description | Loading Behavior |
|----------|-------------|------------------|
| **pattern** | A successful approach that should be reused. Example: "Always run `build:packages` before `build:server` in this monorepo." | Loaded when tags match the mission goal. |
| **gotcha** | A mistake or trap that must be avoided. Example: "Vitest in this monorepo requires the `--root` flag when run from the repo root." | **Always loaded** into every mission regardless of tags. Gotchas represent universal traps. |
| **architecture** | A structural constraint or design decision. Example: "Packages in `libs/` can only depend on packages above them in the dependency chain." | Loaded when tags match the mission goal. |
| **tooling** | A tool-specific quirk or configuration detail. Example: "The `npm run test:server` command uses Vitest, not Jest." | Loaded when tags match the mission goal. |
| **prompt** | A prompt pattern that improved agent output. Example: "Researchers produce better results when given specific file paths to start from rather than open-ended exploration." | Loaded when tags match the mission goal. |

## How Learnings Are Extracted

Learnings are extracted by a retrospective agent during the `/debrief` command when `autoLearn` is enabled. The retrospective agent reviews the entire mission -- the state file, the log, the task results -- and identifies insights worth preserving.

The extraction process:
1. Identify successful patterns (what worked well and should be repeated).
2. Identify failures and root causes (what went wrong and how to avoid it).
3. Assess agent and model choices (were the right agents and models used?).
4. Extract prompt patterns (did any prompting techniques improve or degrade output quality?).
5. Identify gotchas (traps or unexpected behaviors that wasted time).

See `references/learning-extraction.md` for the full extraction process and examples.

## How Learnings Are Loaded

When a new mission starts, the memory system loads relevant learnings into the agent context:

1. **Gotchas are always loaded.** Every learning with `category: gotcha` is injected into every mission, regardless of tags. These represent universal traps that apply across all mission types.
2. **Tag matching.** For non-gotcha learnings, the system compares the learning's `tags` against the mission goal text. A learning is considered relevant if any of its tags appear in the mission goal (case-insensitive substring match).
3. **Top N selection.** If more learnings match than the context budget allows, the system selects the top N most relevant learnings, prioritizing by confidence (high > medium > low) and recency (`extractedAt` timestamp).

Loaded learnings are injected into the agent's system prompt as a "Project Learnings" section. Agents are instructed to respect these learnings as project-specific rules.

## Memory File Format

Each memory file uses YAML frontmatter with the following fields:

```yaml
---
tags:
  - <string>        # Keywords for matching against mission goals
source: <string>    # Mission ID that produced this learning
extractedAt: <ISO-8601 datetime>
confidence: <low|medium|high>
category: <pattern|gotcha|architecture|tooling|prompt>
---
```

The body is a markdown description of the learning. It should be concise (1-3 paragraphs), specific (include file paths and commands where applicable), and actionable (tell the agent what to do or avoid).

See `references/memory-format.md` for the full schema, field-by-field documentation, and examples for each category.

## Manually Creating or Editing Memory Files

You do not need to run a mission to create memory files. Any markdown file with the correct YAML frontmatter placed in `.claude/mission-memory/` will be picked up by the system.

To manually create a learning:

1. Create a new `.md` file in `.claude/mission-memory/` with a descriptive kebab-case name.
2. Add YAML frontmatter with the required fields (`tags`, `source`, `extractedAt`, `confidence`, `category`).
3. For the `source` field, use `manual` to indicate a human-created learning.
4. Write the learning body in markdown.

To edit an existing learning, modify the file directly. You can change the confidence level, add tags, update the body, or change the category.

To remove a learning, delete the file.

## References

- `references/memory-format.md` -- Full schema documentation, field guidelines, and examples for each category.
- `references/learning-extraction.md` -- How the retrospective agent extracts learnings, deduplication, confidence assignment, and examples of good vs bad extractions.
